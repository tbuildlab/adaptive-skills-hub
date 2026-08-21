#!/usr/bin/env python3
"""Regenerate the static package manifest without volatile runtime state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Runtime indexes and live-test packets can contain machine-specific paths,
# generated vendor assets, and large transient artifacts.  The static manifest
# intentionally covers only version-controlled package files.
EXCLUDED_PARTS = {"state", "output", "__pycache__", ".git"}
entries: dict[str, dict[str, int | str]] = {}


def _manifest_bytes(contents: bytes) -> bytes:
    """Use UTF-8 LF-normalized bytes so Git line-ending checkout is stable."""
    try:
        return contents.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        return contents


for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.name in {"MANIFEST.json", "registry.json"} or any(part in EXCLUDED_PARTS for part in path.parts):
        continue
    contents = _manifest_bytes(path.read_bytes())
    entries[path.relative_to(ROOT).as_posix()] = {"bytes": len(contents), "sha256": hashlib.sha256(contents).hexdigest()}
(ROOT / "MANIFEST.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Built static manifest with {len(entries)} files.")
