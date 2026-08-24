"""Server-side workspace allowlisting and Windows reparse-point guards."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
from typing import Iterable

from .schemas import NexusMcpError, WORKSPACE_ID_RE

FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


def _is_windows_special(value: str) -> bool:
    normalized = value.replace("/", "\\")
    return normalized.startswith("\\\\") or normalized.startswith("\\?\\") or normalized.startswith("\\.\\")


def _is_reparse_point(path: Path) -> bool:
    try:
        status = os.lstat(path)
    except OSError as exc:
        raise NexusMcpError("CONTEXT_REJECTED", "path cannot be safely inspected") from exc
    return path.is_symlink() or bool(getattr(status, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)


def _assert_no_reparse_chain(path: Path) -> None:
    if _is_windows_special(str(path)):
        raise NexusMcpError("CONTEXT_REJECTED", "network and device paths are not allowed")
    if not path.is_absolute():
        raise NexusMcpError("CONTEXT_REJECTED", "path must be absolute")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if _is_reparse_point(current):
            raise NexusMcpError("CONTEXT_REJECTED", "reparse points are not allowed")


def _canonical_root(value: str | Path) -> Path:
    raw = str(value)
    if _is_windows_special(raw):
        raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace root is not a supported local path")
    path = Path(raw)
    if not path.is_absolute() or path == Path(path.anchor):
        raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace root is not a supported local directory")
    _assert_no_reparse_chain(path)
    try:
        canonical = path.resolve(strict=True)
    except OSError as exc:
        raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace root cannot be resolved") from exc
    if not canonical.is_dir() or canonical == Path.home().resolve():
        raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace root is not permitted")
    _assert_no_reparse_chain(canonical)
    return canonical


def _inside(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath([os.path.normcase(str(root)), os.path.normcase(str(candidate))]) == os.path.normcase(str(root))
    except ValueError:
        return False


@dataclass(frozen=True)
class AuthorizedWorkspace:
    workspace_id: str
    root: Path


class WorkspaceAuthorizer:
    """Immutable startup configuration. Tool callers can name an ID, never a path."""

    def __init__(self, workspaces: dict[str, AuthorizedWorkspace]) -> None:
        self._workspaces = dict(workspaces)

    @classmethod
    def from_file(cls, path: Path) -> "WorkspaceAuthorizer":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise NexusMcpError("NEXUS_UNAVAILABLE", "workspace configuration is unavailable") from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != "nexus.mcp.workspace.v1" or not isinstance(payload.get("workspaces"), dict):
            raise NexusMcpError("NEXUS_UNAVAILABLE", "workspace configuration is invalid")
        parsed: dict[str, AuthorizedWorkspace] = {}
        for workspace_id, entry in payload["workspaces"].items():
            if not isinstance(workspace_id, str) or not WORKSPACE_ID_RE.fullmatch(workspace_id) or not isinstance(entry, dict) or set(entry) - {"root"} or not isinstance(entry.get("root"), str):
                raise NexusMcpError("NEXUS_UNAVAILABLE", "workspace configuration is invalid")
            parsed[workspace_id] = AuthorizedWorkspace(workspace_id, _canonical_root(entry["root"]))
        if not parsed:
            raise NexusMcpError("NEXUS_UNAVAILABLE", "workspace configuration has no authorized workspace")
        return cls(parsed)

    @classmethod
    def from_roots_for_test(cls, roots: dict[str, Path]) -> "WorkspaceAuthorizer":
        return cls({key: AuthorizedWorkspace(key, _canonical_root(value)) for key, value in roots.items()})

    def resolve(self, workspace_id: str) -> AuthorizedWorkspace:
        if not WORKSPACE_ID_RE.fullmatch(workspace_id) or workspace_id not in self._workspaces:
            raise NexusMcpError("UNAUTHORIZED_WORKSPACE", "workspace is not authorized")
        return self._workspaces[workspace_id]


def guard_regular_file(path: Path, allowed_roots: Iterable[Path]) -> tuple[Path, os.stat_result]:
    """Reject alternate roots, links/junctions, and non-regular files before a read."""
    raw = str(path)
    if _is_windows_special(raw) or not path.is_absolute():
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill path is not permitted")
    roots: list[Path] = []
    for root in allowed_roots:
        # ``~/.codex/skills`` and ``~/.codex/plugins/cache`` are independent
        # optional roots on a clean host.  A missing one must not disable a
        # guarded Skill from the other.  Existing roots still use the complete
        # canonical/reparse validation below.
        try:
            os.lstat(root)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise NexusMcpError("SKILL_LOAD_FAILED", "trusted Skill source cannot be inspected") from exc
        roots.append(_canonical_root(root))
    if not roots:
        raise NexusMcpError("SKILL_LOAD_FAILED", "no trusted Skill source is available")
    absolute = Path(os.path.abspath(raw))
    _assert_no_reparse_chain(absolute)
    try:
        canonical = absolute.resolve(strict=True)
    except OSError as exc:
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill cannot be resolved") from exc
    if not any(_inside(root, canonical) for root in roots):
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill path is outside trusted sources")
    _assert_no_reparse_chain(canonical)
    try:
        before = os.lstat(canonical)
    except OSError as exc:
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill cannot be inspected") from exc
    if not stat.S_ISREG(before.st_mode):
        raise NexusMcpError("SKILL_LOAD_FAILED", "selected Skill is not a regular file")
    return canonical, before


def verify_unchanged(path: Path, before: os.stat_result) -> None:
    try:
        after = os.lstat(path)
    except OSError as exc:
        raise NexusMcpError("CONTEXT_REJECTED", "file changed during guarded read") from exc
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise NexusMcpError("CONTEXT_REJECTED", "file changed during guarded read")
