#!/usr/bin/env python3
"""Create a reviewable private Nexus source archive with a SHA-256 receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
from typing import Any
import unicodedata
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "state", "output", "__pycache__", ".venv", "venv", "node_modules"}
EXCLUDED_NAMES = {"MANIFEST.json", "registry.json", ".env", ".env.local", "workspaces.json", "nexus-desktop-plugin.json"}
EXCLUDED_PARTS_CASEFOLDED = {part.casefold() for part in EXCLUDED_PARTS}
EXCLUDED_NAMES_CASEFOLDED = {name.casefold() for name in EXCLUDED_NAMES}
SENSITIVE_TOKENS = ("credential", "token", "oauth", "session", "cookie", "private_key")
ECOSYSTEM_ROOT_MARKER = ".nexus-ecosystem-root.json"
ECOSYSTEM_DATA_PARTS = {
    "ecosystem",
    "objects",
    "quarantine",
    "incoming",
    "intake-attempts",
    "trees",
    "revisions",
    "components",
    "decisions",
    "evidence",
    "comparisons",
    "locks",
    "observations",
    "state",
    "receipts",
    "staging",
    "tmp",
}
FORBIDDEN_ECOSYSTEM_DIRECTORIES = frozenset(ECOSYSTEM_DATA_PARTS)
ECOSYSTEM_DIGEST_NAMESPACES = {
    "objects",
    "intake-attempts",
    "trees",
    "revisions",
    "components",
    "evidence",
    "comparisons",
    "state",
}
STATIC_MANIFEST_NAME = "MANIFEST.json"
MAX_STATIC_MANIFEST_BYTES = 2 * 1024 * 1024
_STATIC_METADATA_FIELDS = {"bytes", "sha256"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_BIDI_CONTROLS = frozenset(
    chr(value)
    for value in (
        0x061C,
        0x200E,
        0x200F,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
    )
)
_WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)
_FORBIDDEN_MANIFEST_PARTS = frozenset(
    EXCLUDED_PARTS_CASEFOLDED | ECOSYSTEM_DATA_PARTS
)
_FORBIDDEN_MANIFEST_NAMES = frozenset(
    EXCLUDED_NAMES_CASEFOLDED | {ECOSYSTEM_ROOT_MARKER.casefold()}
)
# Historical release evidence deliberately remains in the private source tree,
# but it is not a portable-install artifact.  An allowlist prevents old local
# developer paths or machine-specific evidence from silently entering a zip.
ALLOWED_ROOT_FILES = {"SKILL.md", "sources.json", "requirements-r2-mcp.txt", "requirements-r2-mcp.lock"}
ALLOWED_RESEARCH = {"research/nexus-ecosystem-gap-scan.json"}
ALLOWED_DIRECTORIES = {"ash", "assets", "config", "plugins", "scripts", "tests", ".agents"}
ALLOWED_DOCS = {
    "docs/nexus-g2-openai-structured-v3.md",
    "docs/nexus-g2-openai-hosted-adapter-v1.md",
    "docs/nexus-core-internal-alpha-v1.md",
    "docs/nexus-core-alpha2-local-use-v1.md",
    "docs/nexus-g2-openai-managed-execution-v1.md",
    "docs/nexus-g2-openai-managed-use-v1.md",
    "docs/nexus-g2-openai-managed-sprint-report-v1.md",
    "docs/nexus-v2-g1.md",
    "docs/nexus-desktop-plugin-pilot.md",
    "docs/nexus-runtime-r5-adaptive-enhancement.md",
    "docs/nexus-runtime-r5-host-capability-inventory.md",
    "docs/portable-installation.md",
    "docs/license-inventory.md",
    "docs/upstream-source-registry.md",
    "docs/nexus-capability-foundation.md",
    "docs/nexus-post-r5-runtime-integration-slice1.md",
    "docs/nexus-post-r5-runtime-integration-slice2.md",
    "docs/nexus-post-r5-runtime-integration-slice3a.md",
    "docs/nexus-post-r5-runtime-integration-slice3b.md",
    "docs/nexus-post-r5-runtime-integration-slice3c-adr-pds.md",
    "docs/nexus-agent-runtime-contract.md",
    "docs/nexus-post-g6-reference-research-workflow.md",
    "docs/nexus-visual-identity-v1.md",
}


class PackageBoundaryError(RuntimeError):
    """The reviewed source-package boundary was violated."""


def _is_link_or_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError as exc:
        raise PackageBoundaryError("package source could not be inspected") from exc
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse_flag)


def _is_forbidden_ecosystem_directory(path: Path) -> bool:
    name = path.name.casefold()
    return path.is_dir() and (
        name in FORBIDDEN_ECOSYSTEM_DIRECTORIES
        or (
            name == "sha256"
            and path.parent.name.casefold() in ECOSYSTEM_DIGEST_NAMESPACES
        )
    )


def _assert_no_embedded_ecosystem_root(root: Path) -> None:
    if not root.is_dir() or _is_link_or_reparse(root):
        raise PackageBoundaryError("package source root must be a real directory")
    for path in root.rglob("*"):
        if _is_link_or_reparse(path):
            raise PackageBoundaryError("package source must not contain links or reparse points")
        if path.name.casefold() == ECOSYSTEM_ROOT_MARKER.casefold():
            raise PackageBoundaryError("repository-external ecosystem data root entered package source")
        if _is_forbidden_ecosystem_directory(path):
            raise PackageBoundaryError(
                "repository-external ecosystem storage directory entered package source"
            )


def _allowed_relative(relative: PurePosixPath) -> bool:
    folded = relative.as_posix().casefold()
    folded_name = relative.name.casefold()
    return (
        (
            relative.as_posix() in ALLOWED_ROOT_FILES
            or relative.as_posix() in ALLOWED_RESEARCH
            or relative.as_posix() in ALLOWED_DOCS
            or relative.parts[0] in ALLOWED_DIRECTORIES
        )
        and not any(
            part.casefold() in EXCLUDED_PARTS_CASEFOLDED
            for part in relative.parts
        )
        and not any(part.casefold() in ECOSYSTEM_DATA_PARTS for part in relative.parts[:-1])
        and folded_name not in EXCLUDED_NAMES_CASEFOLDED
        and folded_name != ECOSYSTEM_ROOT_MARKER.casefold()
        and not any(token in folded for token in SENSITIVE_TOKENS)
        and not folded_name.endswith((".key", ".pem", ".p12", ".pfx"))
    )


def allowed(path: Path, *, root: Path = ROOT) -> bool:
    relative = PurePosixPath(path.relative_to(root).as_posix())
    return path.is_file() and _allowed_relative(relative)


def _closed_manifest_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackageBoundaryError("static MANIFEST contains a duplicate JSON key")
        result[key] = value
    return result


def _validated_manifest_name(value: Any) -> str:
    if (
        type(value) is not str
        or not value
        or unicodedata.normalize("NFC", value) != value
        or len(value.encode("utf-8")) > 512
        or "\\" in value
        or "\x00" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise PackageBoundaryError("static MANIFEST contains an unsafe path")
    parts = value.split("/")
    folded_parts = tuple(part.casefold() for part in parts)
    folded_name = folded_parts[-1] if folded_parts else ""
    if (
        not 1 <= len(parts) <= 32
        or any(part in _FORBIDDEN_MANIFEST_PARTS for part in folded_parts)
        or folded_name in _FORBIDDEN_MANIFEST_NAMES
        or folded_name.startswith(".env.")
        or folded_name.endswith((".key", ".pem", ".p12", ".pfx"))
        or any(token in value.casefold() for token in SENSITIVE_TOKENS)
        or any(
            part in {"", ".", ".."}
            or ":" in part
            or part.endswith((".", " "))
            or len(part.encode("utf-8")) > 128
            or any(character in _BIDI_CONTROLS for character in part)
            or part.split(".", 1)[0].casefold() in _WINDOWS_RESERVED
            for part in parts
        )
    ):
        raise PackageBoundaryError("static MANIFEST contains an unsafe path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or path.name.casefold() == STATIC_MANIFEST_NAME.casefold()
    ):
        raise PackageBoundaryError("static MANIFEST contains an unsafe path")
    return value


def _manifest_bytes(contents: bytes) -> bytes:
    try:
        return contents.decode("utf-8", errors="strict").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        return contents


def _load_reviewed_manifest(root: Path) -> dict[str, dict[str, int | str]]:
    location = root / STATIC_MANIFEST_NAME
    raw = _stable_source_bytes(location)
    if len(raw) > MAX_STATIC_MANIFEST_BYTES:
        raise PackageBoundaryError("static MANIFEST exceeds its byte limit")
    try:
        payload = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_closed_manifest_object,
        )
    except PackageBoundaryError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageBoundaryError("static MANIFEST is invalid") from exc
    if type(payload) is not dict or not payload:
        raise PackageBoundaryError("static MANIFEST is invalid")
    collision_keys: set[str] = set()
    checked: dict[str, dict[str, int | str]] = {}
    for raw_name, metadata in payload.items():
        name = _validated_manifest_name(raw_name)
        collision = name.casefold()
        if collision in collision_keys:
            raise PackageBoundaryError("static MANIFEST contains colliding paths")
        collision_keys.add(collision)
        if (
            type(metadata) is not dict
            or set(metadata) != _STATIC_METADATA_FIELDS
            or type(metadata["bytes"]) is not int
            or not 0 <= metadata["bytes"] <= 9_223_372_036_854_775_807
            or type(metadata["sha256"]) is not str
            or not _SHA256_RE.fullmatch(metadata["sha256"])
        ):
            raise PackageBoundaryError("static MANIFEST metadata is invalid")
        checked[name] = dict(metadata)
    return checked


def _reviewed_members_and_manifest(
    *, root: Path
) -> tuple[list[Path], dict[str, dict[str, int | str]]]:
    _assert_no_embedded_ecosystem_root(root)
    manifest = _load_reviewed_manifest(root)
    observed = {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"))
        if allowed(path, root=root)
    }
    expected = {
        name
        for name in manifest
        if _allowed_relative(PurePosixPath(name))
    }
    if set(observed) != expected:
        raise PackageBoundaryError(
            "package-eligible files differ from the integrity-reviewed MANIFEST set"
        )
    members = [observed[name] for name in sorted(expected)]
    for path in members:
        relative = path.relative_to(root)
        if any(part.casefold() in ECOSYSTEM_DATA_PARTS for part in relative.parts[:-1]):
            raise PackageBoundaryError("mutable ecosystem data entered package membership")
    return members, manifest


def reviewed_members(*, root: Path = ROOT) -> list[Path]:
    members, _manifest = _reviewed_members_and_manifest(root=Path(root))
    return members


def _stable_source_bytes(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise PackageBoundaryError("package member could not be inspected") from exc
    if _is_link_or_reparse(path) or not path.is_file():
        raise PackageBoundaryError("package member must be a stable regular file")
    try:
        contents = path.read_bytes()
    except OSError as exc:
        raise PackageBoundaryError("package member could not be read") from exc
    try:
        after = path.lstat()
    except OSError as exc:
        raise PackageBoundaryError("package member could not be inspected") from exc
    identity = lambda item: (
        item.st_dev,
        item.st_ino,
        item.st_size,
        getattr(item, "st_mtime_ns", int(item.st_mtime * 1_000_000_000)),
    )
    if identity(before) != identity(after) or len(contents) != after.st_size:
        raise PackageBoundaryError("package member changed while it was read")
    return contents


def build_package(destination: Path, *, root: Path = ROOT) -> tuple[str, list[str]]:
    """Build one deterministic reviewed archive and return its digest/members."""
    destination = Path(destination).expanduser().resolve()
    root = Path(root).resolve(strict=True)
    if destination.parent == root or root in destination.parents:
        raise PackageBoundaryError("archive output must be outside the repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    members, manifest = _reviewed_members_and_manifest(root=root)
    names: list[str] = []
    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=False,
        ) as archive:
            for path in members:
                relative = path.relative_to(root).as_posix()
                contents = _manifest_bytes(_stable_source_bytes(path))
                metadata = manifest[relative]
                if (
                    len(contents) != metadata["bytes"]
                    or hashlib.sha256(contents).hexdigest() != metadata["sha256"]
                ):
                    raise PackageBoundaryError(
                        "package member differs from the integrity-reviewed MANIFEST"
                    )
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(
                    info,
                    contents,
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
                names.append(relative)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    return digest, names


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a private Nexus pilot archive")
    parser.add_argument("--output", required=True, help="archive location outside the repository")
    args = parser.parse_args()
    destination = Path(args.output).expanduser().resolve()
    try:
        digest, _members = build_package(destination)
    except PackageBoundaryError as exc:
        parser.error(str(exc))
    receipt = destination.with_suffix(destination.suffix + ".sha256")
    receipt.write_text(f"{digest}  {destination.name}\n", encoding="ascii")
    print(f"Archive: {destination}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
