#!/usr/bin/env python3
"""Build a location-independent Nexus GitHub Release candidate artifact.

The builder is deliberately allowlist-only.  It cannot package the repository
README, local evidence, state, caches, credentials, or arbitrary new files.
For a distributable artifact a reviewed wheelhouse is required; the generated
lock file pins every included wheel by SHA-256 and installation is offline.
"""
from __future__ import annotations

import argparse
import email
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

from release_common import MANIFEST_NAME, MANIFEST_SCHEMA, ReleaseError, atomic_json_write, safe_member_name, sha256_file, verify_release_tree


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "release" / "VERSION"
ROOT_FILES = {"requirements-r2-mcp.txt"}
DIRECTORIES = {"ash", "config", "plugins/nexus-desktop"}
EXTRA_FILES = {
    ".agents/plugins/marketplace.json",
    "scripts/nexus_mcp.py",
    "scripts/setup_nexus.py",
    "scripts/release_common.py",
    "scripts/release_install.py",
    "scripts/Install-Nexus.ps1",
    "docs/github-release-installation.md",
    "docs/github-distribution-architecture.md",
    "docs/license-inventory.md",
    "release/VERSION",
}
SENSITIVE_PARTS = ("credential", "token", "oauth", "session", "cookie", "private_key")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def release_version(value: str | None) -> str:
    version = (value or VERSION_FILE.read_text(encoding="utf-8")).strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ReleaseError("release version must be SemVer-like")
    return version


def source_members() -> list[Path]:
    members: list[Path] = []
    for name in ROOT_FILES | EXTRA_FILES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise ReleaseError(f"required release file is unavailable: {name}")
        members.append(path)
    for directory in DIRECTORIES:
        root = ROOT / directory
        if not root.is_dir() or root.is_symlink():
            raise ReleaseError(f"required release directory is unavailable: {directory}")
        members.extend(
            path for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
            and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    result = sorted(set(members))
    for path in result:
        lower = path.relative_to(ROOT).as_posix().lower()
        if any(part in lower for part in SENSITIVE_PARTS) or path.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}:
            raise ReleaseError("release allowlist rejected a sensitive path")
    return result


def wheel_metadata(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as wheel:
            metadata_names = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                raise ReleaseError("wheel metadata is invalid")
            metadata = BytesParser().parsebytes(wheel.read(metadata_names[0]))
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReleaseError(f"wheel is invalid: {path.name}") from exc
    name = metadata.get("Name")
    version = metadata.get("Version")
    if not name or not version:
        raise ReleaseError(f"wheel metadata is invalid: {path.name}")
    return re.sub(r"[-_.]+", "-", name).lower(), version


def copy_wheelhouse(stage: Path, wheelhouse: Path) -> None:
    wheels = sorted(wheelhouse.glob("*.whl"))
    if not wheels:
        raise ReleaseError("a reviewed wheelhouse with at least one wheel is required")
    entries: dict[str, tuple[str, list[str]]] = {}
    target = stage / "wheelhouse"
    target.mkdir()
    for wheel in wheels:
        if wheel.is_symlink() or not wheel.is_file():
            raise ReleaseError("wheelhouse must contain only real wheel files")
        name, version = wheel_metadata(wheel)
        if name in entries and entries[name][0] != version:
            raise ReleaseError("wheelhouse contains conflicting package versions")
        if name not in entries:
            entries[name] = (version, [])
        entries[name][1].append(sha256_file(wheel))
        shutil.copy2(wheel, target / wheel.name)
    lock = "\n".join(
        f"{name}=={version}" + "".join(f" --hash=sha256:{digest}" for digest in sorted(set(digests)))
        for name, (version, digests) in sorted(entries.items())
    ) + "\n"
    (stage / "requirements-release.lock").write_text(lock, encoding="ascii", newline="\n")


def write_manifest(stage: Path, version: str) -> None:
    files: dict[str, dict[str, int | str]] = {}
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        name = path.relative_to(stage).as_posix()
        safe_member_name(name)
        files[name] = {"sha256": sha256_file(path), "size": path.stat().st_size}
    atomic_json_write(stage / MANIFEST_NAME, {
        "schema_version": MANIFEST_SCHEMA,
        "product": "Nexus",
        "distribution": "github-release",
        "version": version,
        "files": files,
    })


def build(output: Path, version: str, wheelhouse: Path) -> tuple[Path, Path]:
    output = output.resolve()
    if ROOT == output or ROOT in output.parents:
        raise ReleaseError("release output must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"Nexus-{version}-windows.zip"
    receipt = archive.with_suffix(".zip.sha256")
    if archive.exists() or receipt.exists():
        raise ReleaseError("release output already exists")
    with tempfile.TemporaryDirectory(prefix="nexus-release-") as temporary:
        stage = Path(temporary) / f"Nexus-{version}"
        stage.mkdir()
        for source in source_members():
            destination = stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        plugin_manifest = stage / "plugins" / "nexus-desktop" / ".codex-plugin" / "plugin.json"
        manifest_payload = json.loads(plugin_manifest.read_text(encoding="utf-8"))
        manifest_payload["version"] = version
        manifest_payload["description"] = "Local Nexus task-planning workflow for ChatGPT Desktop and Codex."
        plugin_manifest.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        try:
            resolved_wheelhouse = wheelhouse.resolve(strict=True)
        except OSError as exc:
            raise ReleaseError("a reviewed wheelhouse is required") from exc
        if not resolved_wheelhouse.is_dir() or resolved_wheelhouse.is_symlink():
            raise ReleaseError("a reviewed wheelhouse is required")
        copy_wheelhouse(stage, resolved_wheelhouse)
        write_manifest(stage, version)
        verify_release_tree(stage)
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as bundle:
            for member in sorted(stage.rglob("*")):
                if member.is_file():
                    bundle.write(member, member.relative_to(stage.parent).as_posix())
    receipt.write_text(f"{sha256_file(archive)}  {archive.name}\n", encoding="ascii", newline="\n")
    bootstrap = output / f"Install-Nexus-{version}.ps1"
    bootstrap_receipt = bootstrap.with_suffix(".ps1.sha256")
    shutil.copy2(ROOT / "scripts" / "Install-Nexus.ps1", bootstrap)
    bootstrap_receipt.write_text(f"{sha256_file(bootstrap)}  {bootstrap.name}\n", encoding="ascii", newline="\n")
    return archive, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a verified Nexus GitHub Release candidate")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--wheelhouse", required=True, help="reviewed offline wheels for the target Windows/Python runtime")
    parser.add_argument("--version", help="override release/VERSION for CI release candidates")
    args = parser.parse_args()
    try:
        archive, receipt = build(Path(args.output_dir).expanduser(), release_version(args.version), Path(args.wheelhouse).expanduser())
        print(f"Artifact: {archive}")
        print(f"Checksum: {receipt}")
        return 0
    except ReleaseError as exc:
        print(f"Nexus release build failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
