#!/usr/bin/env python3
"""Derive a corrected private RC from the verified immutable RC4 payload.

This is intentionally narrower than the normal release builder.  It exists
because the reviewed wheelhouse and CPython archive used for RC4 are already
vendored in the accepted private artifact, not in the source checkout.  The
tool verifies RC4's pinned GitHub asset hash and its internal manifest before
copying a small allowlisted set of current release sources, then writes a new
manifest and receipts.  It never downloads dependencies or reuses an
unverified archive.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

if not __package__:
    # Match build_release.py: the Nexus-owned embeddable runtime is isolated.
    _SCRIPT_DIRECTORY = Path(__file__).resolve().parent
    if str(_SCRIPT_DIRECTORY) not in sys.path:
        sys.path.insert(0, str(_SCRIPT_DIRECTORY))

if __package__:
    from .build_release import ROOT, source_payloads, write_manifest
    from .release_common import MANIFEST_NAME, ReleaseError, safe_extract, sha256_file, verify_release_tree
else:
    from build_release import ROOT, source_payloads, write_manifest
    from release_common import MANIFEST_NAME, ReleaseError, safe_extract, sha256_file, verify_release_tree


BASE_VERSION = "0.1.0-rc.4"
BASE_ARCHIVE_SHA256 = "0e518fe5fa6c28a1d720c2a94aaa5e56b89fa87e3c4a4bf884432469e9795e51"


def _receipt_digest(receipt: Path, archive: Path) -> str:
    try:
        fields = receipt.read_text(encoding="ascii").strip().split()
    except OSError as exc:
        raise ReleaseError("base release checksum receipt is unavailable") from exc
    if len(fields) != 2 or fields[1] != archive.name or len(fields[0]) != 64:
        raise ReleaseError("base release checksum receipt is invalid")
    try:
        int(fields[0], 16)
    except ValueError as exc:
        raise ReleaseError("base release checksum receipt is invalid") from exc
    return fields[0].lower()


def _write_receipt(path: Path) -> Path:
    receipt = path.with_suffix(path.suffix + ".sha256")
    receipt.write_text(f"{sha256_file(path)}  {path.name}\n", encoding="ascii", newline="\n")
    return receipt


def build(
    base_archive: Path,
    base_receipt: Path,
    output: Path,
    version: str,
    *,
    expected_base_sha256: str = BASE_ARCHIVE_SHA256,
) -> tuple[Path, Path]:
    """Create a new release only from the pinned, verified RC4 base."""
    if version == BASE_VERSION:
        raise ReleaseError("a rebased release must use a new version")
    archive = base_archive.resolve(strict=True)
    if not archive.is_file() or archive.is_symlink():
        raise ReleaseError("base release archive is unavailable")
    received = _receipt_digest(base_receipt.resolve(strict=True), archive)
    actual = sha256_file(archive)
    if received != expected_base_sha256 or actual != expected_base_sha256:
        raise ReleaseError("base release archive does not match the pinned RC4 artifact")
    output = output.resolve()
    if ROOT == output or ROOT in output.parents:
        raise ReleaseError("release output must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    target_archive = output / f"Nexus-{version}-windows.zip"
    if target_archive.exists() or target_archive.with_suffix(".zip.sha256").exists():
        raise ReleaseError("release output already exists")
    with tempfile.TemporaryDirectory(prefix="nexus-rebase-") as temporary:
        temp = Path(temporary)
        base_root = safe_extract(archive, temp / "extract")
        base_manifest = verify_release_tree(base_root)
        if base_manifest.get("version") != BASE_VERSION:
            raise ReleaseError("base release manifest is not RC4")
        stage = temp / f"Nexus-{version}"
        base_root.replace(stage)
        reviewed_sources = source_payloads()
        reviewed_source_bytes = {
            source.relative_to(ROOT).as_posix(): contents
            for source, contents in reviewed_sources
        }
        for source, contents in reviewed_sources:
            destination = stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contents)
        (stage / "release" / "VERSION").write_text(version + "\n", encoding="utf-8", newline="\n")
        plugin_manifest = stage / "plugins" / "nexus-desktop" / ".codex-plugin" / "plugin.json"
        try:
            plugin = json.loads(plugin_manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReleaseError("release plugin manifest is invalid") from exc
        if not isinstance(plugin, dict):
            raise ReleaseError("release plugin manifest is invalid")
        plugin["version"] = version
        plugin_manifest.write_text(json.dumps(plugin, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        write_manifest(stage, version)
        verify_release_tree(stage)
        with zipfile.ZipFile(target_archive, "x", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as bundle:
            for member in sorted(stage.rglob("*")):
                if member.is_file():
                    bundle.write(member, member.relative_to(stage.parent).as_posix())
    receipt = _write_receipt(target_archive)
    bootstrap = output / f"Install-Nexus-{version}.ps1"
    bootstrap.write_bytes(reviewed_source_bytes["scripts/Install-Nexus.ps1"])
    _write_receipt(bootstrap)
    manifest_asset = output / f"Nexus-{version}.release-manifest.json"
    with zipfile.ZipFile(target_archive) as bundle:
        manifest_asset.write_bytes(bundle.read(f"Nexus-{version}/{MANIFEST_NAME}"))
    _write_receipt(manifest_asset)
    return target_archive, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a verified Nexus RC from the immutable RC4 artifact")
    parser.add_argument("--base-archive", required=True)
    parser.add_argument("--base-checksum", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        archive, receipt = build(Path(args.base_archive), Path(args.base_checksum), Path(args.output_dir), args.version)
        print(f"Artifact: {archive}")
        print(f"Checksum: {receipt}")
        return 0
    except ReleaseError as exc:
        print(f"Nexus release rebase failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
