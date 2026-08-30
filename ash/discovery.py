from __future__ import annotations

import os
import re
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .common import first_heading, parse_frontmatter_prefix, relative_or_absolute, stable_id, tokenize, utc_now

MAX_SKILL_INTEGRITY_BYTES = 128 * 1024
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv"}
SKILL_KEYWORDS = {
    "frontend", "backend", "api", "python", "react", "design", "ui", "ux", "test", "testing",
    "security", "data", "document", "presentation", "ppt", "agent", "ai", "research", "workflow",
    "animation", "accessibility", "orchestration", "architecture", "code", "review", "pdf",
}
DISABLED_PATH_MARKERS = (".disabled-", ".disabled_")


def _bounded_stable_skill_digest(path: Path) -> tuple[str | None, int | None]:
    """Hash a bounded SKILL.md without retaining or exposing instructions."""
    try:
        if path.is_symlink() or not path.is_file():
            return None, None
        before = path.stat()
        if before.st_size > MAX_SKILL_INTEGRITY_BYTES:
            return None, before.st_size
        raw = path.read_bytes()
        after = path.stat()
    except OSError:
        return None, None
    identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    if identity(before) != identity(after) or len(raw) != after.st_size:
        return None, after.st_size
    return hashlib.sha256(raw).hexdigest(), len(raw)


def _has_git_metadata(path: Path, boundary: Path) -> bool:
    """Detect an explicitly maintained checkout without invoking Git or following it upward."""
    current = path.resolve()
    boundary = boundary.resolve()
    while True:
        # The workspace itself can be a broad checkout containing unrelated
        # imported Skills.  It is not evidence that every child is separately
        # maintained, so never inherit a boundary-level .git directory.
        if current == boundary:
            return False
        if (current / ".git").exists():
            return True
        if current.parent == current:
            return False
        current = current.parent


def _is_disabled_path(path: Path) -> bool:
    return any(marker in part.casefold() for part in path.parts for marker in DISABLED_PATH_MARKERS)


def _provenance(path: Path, workspace_root: Path) -> dict[str, Any]:
    """Classify local provenance conservatively and deterministically.

    This is intentionally filesystem-only: no source, licence, or revision is
    guessed from a Skill name.  A checkout with visible Git metadata is an
    explicitly maintained local source; other paths inside the workspace are
    project-specific.  User-level Codex paths are lower authority than either.
    """
    resolved = path.resolve()
    workspace = workspace_root.resolve()
    disabled = _is_disabled_path(resolved)
    in_workspace = resolved.is_relative_to(workspace)
    maintained = in_workspace and _has_git_metadata(resolved.parent, workspace)
    normalized = str(resolved).replace("\\", "/").casefold()
    if maintained:
        scope, precedence, reason = "local-maintained", 50, "explicitly maintained local checkout"
    elif in_workspace:
        scope, precedence, reason = "project-specific", 40, "project-specific local source"
    elif "/.codex/skills/" in normalized:
        scope, precedence, reason = "codex-user", 20, "user-level Codex Skill"
    else:
        scope, precedence, reason = "external-local", 10, "other readable local source"
    if disabled:
        precedence = 0
        reason = "disabled path is ineligible for canonical execution"
    return {
        "source_scope": scope,
        "precedence": precedence,
        "precedence_reason": reason,
        "maintained_checkout": maintained,
        "disabled_path": disabled,
    }


def _resolve_duplicates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve only deterministic, auditable duplicate-name groups.

    A higher provenance tier is a safe canonical decision even when copies have
    diverged.  Equal-authority copies fail closed because discovery deliberately
    reads metadata prefixes only; their full content is not treated as inspected.
    Non-canonical copies remain discoverable but unrouteable.
    """
    resolutions: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["name"].casefold()].append(record)
    for key, group in groups.items():
        if len(group) < 2:
            continue
        group_id = f"duplicate:{key}"
        valid = [item for item in group if item["base_status"] == "available"]
        ranked = sorted(valid, key=lambda item: (-item["provenance"]["precedence"], item["skill_md_path"].casefold()))
        top_precedence = ranked[0]["provenance"]["precedence"] if ranked else None
        leaders = [item for item in ranked if item["provenance"]["precedence"] == top_precedence] if ranked else []
        canonical: dict[str, Any] | None = None
        outcome = "no_executable_candidate"
        reason = "no available duplicate copy"
        if len(leaders) == 1:
            canonical = leaders[0]
            outcome = "resolved_by_precedence"
            reason = canonical["provenance"]["precedence_reason"]
        elif leaders:
            outcome = "conflict"
            reason = "equal-authority copies require a deliberate full-content audit"
        for record in group:
            record["duplicate_group"] = group_id
            record["duplicate_outcome"] = outcome
            if record is canonical:
                record["duplicate_role"] = "canonical"
                record["status"] = "available"
            elif outcome == "conflict" and record["base_status"] == "available":
                record["duplicate_role"] = "conflict"
                record["status"] = "duplicate_conflict"
            else:
                record["duplicate_role"] = "shadowed"
                if record["base_status"] == "available":
                    record["status"] = "duplicate"
            record["canonical_skill_id"] = canonical["id"] if canonical else None
        resolutions.append({
            "group": group_id,
            "name": group[0]["name"],
            "members": [item["id"] for item in sorted(group, key=lambda item: item["skill_md_path"].casefold())],
            "canonical_skill_id": canonical["id"] if canonical else None,
            "outcome": outcome,
            "reason": reason,
            "content_identical": None,
            "content_inspection": "not performed during metadata-only discovery",
        })
    return sorted(resolutions, key=lambda item: item["group"])


def _walk(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root, topdown=True, onerror=lambda _err: None):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        current_path = Path(current)
        for filename in files:
            yield current_path / filename


def _infer_tags(*parts: str) -> list[str]:
    tokens = set().union(*(tokenize(part) for part in parts))
    return sorted(tokens & SKILL_KEYWORDS)


def discover_skills(
    roots: Iterable[Path], workspace_root: Path, exclude_roots: Iterable[Path] = (),
    duplicate_resolutions_out: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    excluded = [path.resolve() for path in exclude_roots]
    records: list[dict[str, Any]] = []
    for root in roots:
        root = root.resolve()
        if not root.exists():
            continue
        for path in _walk(root):
            if path.name != "SKILL.md":
                continue
            resolved = path.resolve()
            if any(resolved.is_relative_to(item) for item in excluded):
                continue
            metadata, error, prefix = parse_frontmatter_prefix(path)
            name = str(metadata.get("name") or path.parent.name).strip()
            description = str(metadata.get("description") or first_heading(prefix) or "").strip()
            status = "available" if error is None else "malformed"
            try:
                modified = path.stat().st_mtime
            except OSError:
                modified = None
                status = "inaccessible"
            content_sha256, content_bytes = _bounded_stable_skill_digest(path)
            record = {
                "id": stable_id("skill", resolved),
                "kind": "skill",
                "name": name,
                "description": description,
                "path": str(path.parent),
                "skill_md_path": str(resolved),
                "scope": "project" if resolved.is_relative_to(workspace_root.resolve()) else "external",
                "source": "local",
                "tags": _infer_tags(name, description, str(path.parent)),
                "status": status,
                "scan_error": error,
                "modified_epoch": modified,
                "metadata": metadata,
                "base_status": status,
                "metadata_fingerprint": hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
                "content_sha256": content_sha256,
                "content_bytes": content_bytes,
                "provenance": _provenance(resolved, workspace_root),
            }
            records.append(record)
    resolutions = _resolve_duplicates(records)
    if duplicate_resolutions_out is not None:
        duplicate_resolutions_out.extend(resolutions)
    return sorted(records, key=lambda item: (item["name"].casefold(), item["skill_md_path"]))


def _toml_field(prefix: str, field: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(field)}\s*=\s*['\"]([^'\"]+)['\"]", prefix)
    return match.group(1).strip() if match else None


def discover_agents(roots: Iterable[Path], workspace_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root in roots:
        root = root.resolve()
        if not root.exists():
            continue
        for path in _walk(root):
            if path.suffix.lower() not in {".toml", ".md"}:
                continue
            if path.suffix.lower() == ".md" and "agent" not in str(path.parent).lower() and "agent" not in path.name.lower():
                continue
            try:
                with path.open("r", encoding="utf-8") as handle:
                    prefix = handle.read(16 * 1024)
                stat = path.stat()
            except (OSError, UnicodeDecodeError):
                continue
            if path.suffix.lower() == ".toml":
                name = _toml_field(prefix, "name") or path.stem
                description = _toml_field(prefix, "description") or ""
            else:
                name = path.stem
                description = first_heading(prefix) or ""
            records.append({
                "id": stable_id("agent", path.resolve()), "kind": "agent", "name": name,
                "description": description, "path": str(path.resolve()),
                "scope": "project" if path.resolve().is_relative_to(workspace_root.resolve()) else "external",
                "source": "local", "tags": _infer_tags(name, description, str(path.parent)),
                "status": "available", "modified_epoch": stat.st_mtime,
            })
    return sorted(records, key=lambda item: (item["name"].casefold(), item["path"]))


def build_index(workspace_root: Path, hub_root: Path, additional_roots: Iterable[Path] = ()) -> dict[str, Any]:
    workspace_root = workspace_root.resolve()
    roots = [workspace_root, *[Path(item).resolve() for item in additional_roots]]
    agent_roots: list[Path] = []
    for root in roots:
        agent_roots.extend([root / ".codex" / "agents", root / ".agents"])
    duplicate_resolutions: list[dict[str, Any]] = []
    skills = discover_skills(
        roots, workspace_root, exclude_roots=[hub_root], duplicate_resolutions_out=duplicate_resolutions,
    )
    return {
        "schema_version": 2,
        "generated_at_utc": utc_now(),
        "workspace_root": str(workspace_root),
        "scan_roots": [str(root) for root in roots],
        "skills": skills,
        "duplicate_resolutions": duplicate_resolutions,
        "agents": discover_agents(agent_roots, workspace_root),
    }
