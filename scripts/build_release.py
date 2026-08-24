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
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

if not __package__:
    # The official embeddable Python used by Nexus deliberately omits the
    # script directory from sys.path.  Keep the release builder runnable with
    # that owned runtime without consulting PATH or user site packages.
    _SCRIPT_DIRECTORY = Path(__file__).resolve().parent
    if str(_SCRIPT_DIRECTORY) not in sys.path:
        sys.path.insert(0, str(_SCRIPT_DIRECTORY))

if __package__:
    from .release_common import MANIFEST_NAME, MANIFEST_SCHEMA, ReleaseError, atomic_json_write, safe_member_name, sha256_file, verify_release_tree
else:
    from release_common import MANIFEST_NAME, MANIFEST_SCHEMA, ReleaseError, atomic_json_write, safe_member_name, sha256_file, verify_release_tree


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "release" / "VERSION"
RUNTIME_SPEC_FILE = ROOT / "release" / "windows-runtime.json"
ROOT_FILES = {"requirements-r2-mcp.txt"}
DIRECTORIES = {"ash", "config", "plugins/nexus-desktop"}
EXTRA_FILES = {
    ".agents/plugins/marketplace.json",
    "scripts/nexus_mcp.py",
    "scripts/setup_nexus.py",
    "scripts/desktop_marketplace.py",
    "scripts/release_common.py",
    "scripts/release_install.py",
    "scripts/Install-Nexus.ps1",
    "docs/github-release-installation.md",
    "docs/github-distribution-architecture.md",
    "docs/license-inventory.md",
    "release/VERSION",
    "release/windows-runtime.json",
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


def write_wheel_lock(stage: Path, wheelhouse: Path) -> None:
    wheels = sorted(wheelhouse.glob("*.whl"))
    if not wheels:
        raise ReleaseError("a reviewed wheelhouse with at least one wheel is required")
    entries: dict[str, tuple[str, list[str]]] = {}
    for wheel in wheels:
        if wheel.is_symlink() or not wheel.is_file():
            raise ReleaseError("wheelhouse must contain only real wheel files")
        name, version = wheel_metadata(wheel)
        if name in entries and entries[name][0] != version:
            raise ReleaseError("wheelhouse contains conflicting package versions")
        if name not in entries:
            entries[name] = (version, [])
        entries[name][1].append(sha256_file(wheel))
    lock = "\n".join(
        f"{name}=={version}" + "".join(f" --hash=sha256:{digest}" for digest in sorted(set(digests)))
        for name, (version, digests) in sorted(entries.items())
    ) + "\n"
    (stage / "requirements-release.lock").write_text(lock, encoding="ascii", newline="\n")


def runtime_spec() -> dict[str, str]:
    """Load the reviewed, pinned official Windows runtime identity."""
    try:
        payload = json.loads(RUNTIME_SPEC_FILE.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("embedded runtime specification is unavailable") from exc
    expected = {
        "schema_version", "provider", "python_version", "platform", "filename", "sha256",
        "source_url", "license", "license_notice", "python_pth",
    }
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ReleaseError("embedded runtime specification is invalid")
    if payload.get("schema_version") != "nexus.windows.embedded-runtime.v1" or payload.get("platform") != "win-amd64":
        raise ReleaseError("embedded runtime specification is invalid")
    for key in expected - {"schema_version"}:
        if not isinstance(payload.get(key), str) or not payload[key]:
            raise ReleaseError("embedded runtime specification is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", payload["sha256"]):
        raise ReleaseError("embedded runtime specification is invalid")
    return payload


def safe_zip_extract(source: Path, destination: Path) -> None:
    """Extract a reviewed ZIP without trusting traversal or symlink metadata."""
    try:
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                name = safe_member_name(info.filename)
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ReleaseError("embedded runtime archive contains a symlink")
                target = destination.joinpath(*PurePosixPath(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as input_handle, target.open("xb") as output_handle:
                    shutil.copyfileobj(input_handle, output_handle)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReleaseError("embedded runtime archive is invalid") from exc


def vendor_wheels(wheelhouse: Path, destination: Path) -> None:
    """Vendor reviewed wheels; embeddable Python deliberately does not ship pip."""
    destination.mkdir(parents=True, exist_ok=True)
    for wheel in sorted(wheelhouse.glob("*.whl")):
        safe_zip_extract(wheel, destination)


def configure_embedded_paths(runtime: Path, spec: dict[str, str]) -> None:
    path_file = runtime / spec["python_pth"]
    if not path_file.is_file() or path_file.is_symlink():
        raise ReleaseError("embedded runtime is missing its path configuration")
    # The PyWin32 wheel uses a .pth file.  The embeddable distribution's ._pth
    # mode does not process it reliably, so these paths must be explicit.
    path_file.write_text(
        "python313.zip\n.\nsite-packages\nsite-packages/win32\nsite-packages/win32/lib\n"
        "site-packages/pythonwin\nsite-packages/pywin32_system32\nimport site\n",
        encoding="ascii",
        newline="\n",
    )


def embedded_runtime_self_check(executable: Path) -> None:
    result = subprocess.run(
        [str(executable), "-I", "-B", "-c", "import mcp, sys; assert sys.version_info[:2] == (3, 13)"],
        cwd=executable.parent,
        capture_output=True,
        text=True,
        timeout=20,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode:
        raise ReleaseError("embedded runtime dependency self-check failed")


def prepare_embedded_runtime(stage: Path, wheelhouse: Path, python_embed: Path) -> None:
    spec = runtime_spec()
    try:
        archive = python_embed.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("a reviewed embedded Python runtime is required") from exc
    if archive.is_symlink() or archive.name != spec["filename"] or sha256_file(archive) != spec["sha256"]:
        raise ReleaseError("embedded Python runtime does not match the pinned official checksum")
    runtime = stage / "runtime" / "python"
    runtime.mkdir(parents=True)
    safe_zip_extract(archive, runtime)
    executable = runtime / "python.exe"
    if not executable.is_file() or executable.is_symlink() or not (runtime / "LICENSE.txt").is_file():
        raise ReleaseError("embedded runtime payload is incomplete")
    configure_embedded_paths(runtime, spec)
    vendor_wheels(wheelhouse, runtime / "site-packages")
    metadata = {
        "schema_version": "nexus.embedded-runtime.metadata.v1",
        "provider": spec["provider"],
        "python_version": spec["python_version"],
        "platform": spec["platform"],
        "source_url": spec["source_url"],
        "archive_sha256": spec["sha256"],
        "license": spec["license"],
    }
    atomic_json_write(runtime.parent / "runtime-metadata.json", metadata)
    embedded_runtime_self_check(executable)


def write_manifest(stage: Path, version: str) -> None:
    files: dict[str, dict[str, int | str]] = {}
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        # A release may be staged from an already-started embedded runtime.
        # Its ``__pycache__`` bytecode is host-generated state, not a signed
        # payload member; release_common.verify_release_tree intentionally
        # ignores exactly these files after extraction as well.
        if "__pycache__" in path.parts and path.suffix == ".pyc":
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


def build(output: Path, version: str, wheelhouse: Path, python_embed: Path) -> tuple[Path, Path]:
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
        plugin_mcp = stage / "plugins" / "nexus-desktop" / ".mcp.json"
        mcp_payload = json.loads(plugin_mcp.read_text(encoding="utf-8"))
        server = mcp_payload.get("mcpServers", {}).get("nexus_desktop_local")
        if not isinstance(server, dict):
            raise ReleaseError("plugin MCP manifest is invalid")
        # The plugin is rooted at plugins/nexus-desktop.  This release-local
        # executable avoids PATH, py.exe and Windows App Execution Aliases.
        server["command"] = "../../runtime/python/python.exe"
        plugin_mcp.write_text(json.dumps(mcp_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        try:
            resolved_wheelhouse = wheelhouse.resolve(strict=True)
        except OSError as exc:
            raise ReleaseError("a reviewed wheelhouse is required") from exc
        if not resolved_wheelhouse.is_dir() or resolved_wheelhouse.is_symlink():
            raise ReleaseError("a reviewed wheelhouse is required")
        write_wheel_lock(stage, resolved_wheelhouse)
        prepare_embedded_runtime(stage, resolved_wheelhouse, python_embed)
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
    # Publish the exact in-archive manifest as a separately hashable release
    # asset. This gives a downloader a six-asset receipt set without trusting
    # an extraction step just to inspect the allowlisted payload contract.
    manifest_asset = output / f"Nexus-{version}.release-manifest.json"
    with zipfile.ZipFile(archive) as bundle:
        manifest_asset.write_bytes(bundle.read(f"Nexus-{version}/{MANIFEST_NAME}"))
    manifest_receipt = manifest_asset.with_suffix(manifest_asset.suffix + ".sha256")
    manifest_receipt.write_text(f"{sha256_file(manifest_asset)}  {manifest_asset.name}\n", encoding="ascii", newline="\n")
    return archive, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a verified Nexus GitHub Release candidate")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--wheelhouse", required=True, help="reviewed offline wheels for the target Windows/Python runtime")
    parser.add_argument("--python-embed", required=True, help="official Windows x64 embeddable Python ZIP matching release/windows-runtime.json")
    parser.add_argument("--version", help="override release/VERSION for CI release candidates")
    args = parser.parse_args()
    try:
        archive, receipt = build(Path(args.output_dir).expanduser(), release_version(args.version), Path(args.wheelhouse).expanduser(), Path(args.python_embed).expanduser())
        print(f"Artifact: {archive}")
        print(f"Checksum: {receipt}")
        return 0
    except ReleaseError as exc:
        print(f"Nexus release build failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
