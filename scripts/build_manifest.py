#!/usr/bin/env python3
"""Regenerate the static package manifest without volatile runtime state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import unicodedata

if __package__:
    from .release_common import is_private_memory_payload
else:
    from release_common import is_private_memory_payload

ROOT = Path(__file__).resolve().parents[1]
# Runtime indexes and live-test packets can contain machine-specific paths,
# generated vendor assets, and large transient artifacts.  The static manifest
# intentionally covers only version-controlled package files.
EXCLUDED_PARTS = {"state", "output", "__pycache__", ".pytest_cache", ".git"}
EXCLUDED_PARTS_CASEFOLDED = {part.casefold() for part in EXCLUDED_PARTS}
EXCLUDED_NAMES = {
    "MANIFEST.json",
    "registry.json",
    ".env",
    ".env.local",
    "workspaces.json",
    "nexus-desktop-plugin.json",
}
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
# This is intentionally an ignored, machine-local setup record.  Keeping it out
# of the static package manifest preserves the manifest's version-controlled
# package boundary while allowing local environment documentation to exist.
LOCAL_ONLY_PATHS = {
    Path("docs/local-development-environment.md"),
    # PowerShell may create this relative to the active repository.  It is a
    # machine-generated cache, never a distributable Nexus source file.
    Path("Microsoft/Windows/PowerShell/ModuleAnalysisCache"),
}
LOCAL_ONLY_PATHS_CASEFOLDED = {
    path.as_posix().casefold() for path in LOCAL_ONLY_PATHS
}
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


class ManifestBoundaryError(RuntimeError):
    """The static manifest boundary contains mutable ecosystem data."""


def _manifest_bytes(contents: bytes) -> bytes:
    """Use UTF-8 LF-normalized bytes so Git line-ending checkout is stable."""
    try:
        return contents.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        return contents


def _is_link_or_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError as exc:
        raise ManifestBoundaryError("manifest source could not be inspected") from exc
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


def _validated_manifest_name(value: str) -> str:
    if (
        not value
        or unicodedata.normalize("NFC", value) != value
        or len(value.encode("utf-8")) > 512
        or "\\" in value
        or "\x00" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ManifestBoundaryError("manifest source contains an unsafe path")
    parts = value.split("/")
    if (
        not 1 <= len(parts) <= 32
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
        raise ManifestBoundaryError("manifest source contains an unsafe path")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise ManifestBoundaryError("manifest source contains an unsafe path")
    return value


def build_manifest_bytes(*, root: Path = ROOT) -> tuple[bytes, dict[str, dict[str, int | str]]]:
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or _is_link_or_reparse(root):
        raise ManifestBoundaryError("manifest source root must be a real directory")
    entries: dict[str, dict[str, int | str]] = {}
    collision_keys: set[str] = set()
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix().encode("utf-8"),
    ):
        relative = path.relative_to(root)
        if path.name.casefold() in {"project-memory-config.json", ".nexus-project-memory-root.json"} or "project-memory" in {p.casefold() for p in relative.parts}:
            raise ManifestBoundaryError("private Project Memory entered manifest source")
        if _is_link_or_reparse(path):
            raise ManifestBoundaryError("manifest source must not contain links or reparse points")
        if path.name.casefold() == ECOSYSTEM_ROOT_MARKER.casefold():
            raise ManifestBoundaryError("repository-external ecosystem data root entered manifest source")
        if _is_forbidden_ecosystem_directory(path):
            raise ManifestBoundaryError(
                "repository-external ecosystem storage directory entered manifest source"
            )
        if (
            not path.is_file()
            or relative.as_posix().casefold() in LOCAL_ONLY_PATHS_CASEFOLDED
            or path.name.casefold() in EXCLUDED_NAMES_CASEFOLDED
            or path.name.casefold().startswith(".env.")
            or path.name.casefold().endswith((".key", ".pem", ".p12", ".pfx"))
            or any(token in relative.as_posix().casefold() for token in SENSITIVE_TOKENS)
            or any(
                part.casefold() in EXCLUDED_PARTS_CASEFOLDED
                for part in relative.parts
            )
            or any(part.casefold() in ECOSYSTEM_DATA_PARTS for part in relative.parts[:-1])
        ):
            continue
        name = _validated_manifest_name(relative.as_posix())
        collision = name.casefold()
        if collision in collision_keys:
            raise ManifestBoundaryError("manifest source contains colliding paths")
        collision_keys.add(collision)
        contents = _manifest_bytes(path.read_bytes())
        if is_private_memory_payload(contents):
            raise ManifestBoundaryError("private Project Memory payload entered manifest source")
        entries[name] = {
            "bytes": len(contents),
            "sha256": hashlib.sha256(contents).hexdigest(),
        }
    serialized = (json.dumps(entries, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return serialized, entries


def write_manifest(*, root: Path = ROOT, destination: Path | None = None) -> int:
    serialized, entries = build_manifest_bytes(root=root)
    output = Path(destination) if destination is not None else Path(root) / "MANIFEST.json"
    output.write_bytes(serialized)
    return len(entries)


def main() -> int:
    count = write_manifest()
    print(f"Built static manifest with {count} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
