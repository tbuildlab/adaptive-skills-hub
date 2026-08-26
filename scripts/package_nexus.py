#!/usr/bin/env python3
"""Create a reviewable private Nexus source archive with a SHA-256 receipt."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "state", "output", "__pycache__", ".venv", "venv", "node_modules"}
EXCLUDED_NAMES = {"MANIFEST.json", "registry.json", ".env", ".env.local", "workspaces.json", "nexus-desktop-plugin.json"}
SENSITIVE_TOKENS = ("credential", "token", "oauth", "session", "cookie", "private_key")
# Historical release evidence deliberately remains in the private source tree,
# but it is not a portable-install artifact.  An allowlist prevents old local
# developer paths or machine-specific evidence from silently entering a zip.
ALLOWED_ROOT_FILES = {"SKILL.md", "sources.json", "requirements-r2-mcp.txt", "requirements-r2-mcp.lock"}
ALLOWED_DIRECTORIES = {"ash", "config", "plugins", "scripts", "tests", ".agents"}
ALLOWED_DOCS = {
    "docs/nexus-desktop-plugin-pilot.md",
    "docs/nexus-runtime-r5-adaptive-enhancement.md",
    "docs/nexus-runtime-r5-host-capability-inventory.md",
    "docs/portable-installation.md",
    "docs/license-inventory.md",
    "docs/upstream-source-registry.md",
    "docs/nexus-capability-foundation.md",
    "docs/nexus-agent-runtime-contract.md",
}


def allowed(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    lower = relative.as_posix().lower()
    return (
        path.is_file()
        and (
            relative.as_posix() in ALLOWED_ROOT_FILES
            or relative.as_posix() in ALLOWED_DOCS
            or relative.parts[0] in ALLOWED_DIRECTORIES
        )
        and not any(part in EXCLUDED_PARTS for part in relative.parts)
        and path.name not in EXCLUDED_NAMES
        and not any(token in lower for token in SENSITIVE_TOKENS)
        and not path.name.endswith((".key", ".pem", ".p12", ".pfx"))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a private Nexus pilot archive")
    parser.add_argument("--output", required=True, help="archive location outside the repository")
    args = parser.parse_args()
    destination = Path(args.output).expanduser().resolve()
    if destination.parent == ROOT or ROOT in destination.parents:
        parser.error("archive output must be outside the repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    members = [path for path in sorted(ROOT.rglob("*")) if allowed(path)]
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as archive:
        for path in members:
            archive.write(path, path.relative_to(ROOT).as_posix())
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    receipt = destination.with_suffix(destination.suffix + ".sha256")
    receipt.write_text(f"{digest}  {destination.name}\n", encoding="ascii")
    print(f"Archive: {destination}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
