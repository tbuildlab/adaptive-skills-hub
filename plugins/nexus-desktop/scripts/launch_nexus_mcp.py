"""Launch the installed Nexus Runtime R2 process from private local configuration.

This thin plugin bridge intentionally has no network, shell, or MCP request
handling. It starts only the fixed R2 stdio entry point after reading one
user-owned configuration file created by ``scripts/setup_nexus.py``.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


SCHEMA_VERSION = "nexus.desktop.local.v1"
CONFIG_FILENAME = "nexus-desktop-plugin.json"


def _data_root() -> Path:
    explicit = os.environ.get("NEXUS_DATA_ROOT")
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            raise ValueError("Nexus data root is invalid")
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise ValueError("Nexus data root is unavailable") from exc
        if not resolved.is_dir() or resolved.is_symlink() or resolved == Path(resolved.anchor):
            raise ValueError("Nexus data root is invalid")
        return resolved
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Nexus"
    return Path.home() / ".nexus"


def _absolute_file(value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is invalid")
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"{field} is invalid")
    resolved = path.resolve(strict=True)
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(f"{field} is invalid")
    return resolved


def _absolute_directory(value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is invalid")
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"{field} is invalid")
    resolved = path.resolve(strict=True)
    if not resolved.is_dir() or resolved.is_symlink() or resolved == Path(resolved.anchor):
        raise ValueError(f"{field} is invalid")
    return resolved


def load_launch_configuration(config_path: Path | None = None) -> tuple[Path, Path, Path]:
    """Return trusted runtime Python, Nexus root, and workspace configuration."""
    location = config_path or (_data_root() / CONFIG_FILENAME)
    try:
        payload = json.loads(location.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Nexus local configuration is unavailable") from exc
    if not isinstance(payload, dict) or set(payload) != {
        "schema_version", "nexus_root", "python_executable", "workspace_config"
    } or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Nexus local configuration is invalid")
    root = _absolute_directory(payload["nexus_root"], "nexus_root")
    python = _absolute_file(payload["python_executable"], "python_executable")
    workspace = _absolute_file(payload["workspace_config"], "workspace_config")
    entrypoint = root / "scripts" / "nexus_mcp.py"
    if not entrypoint.is_file() or entrypoint.is_symlink() or not (root / "ash").is_dir():
        raise ValueError("Nexus installation is invalid")
    return python, root, workspace


def main() -> int:
    try:
        python, root, workspace = load_launch_configuration()
        completed = subprocess.run(
            [str(python), str(root / "scripts" / "nexus_mcp.py"), "--workspace-config", str(workspace)],
            cwd=str(root),
            check=False,
            shell=False,
        )
        return completed.returncode
    except Exception as exc:
        print(f"Nexus Desktop plugin could not start: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
