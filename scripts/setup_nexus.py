#!/usr/bin/env python3
"""Safe local setup lifecycle for the Nexus Desktop Plugin.

The script writes only a Nexus-owned user-data directory.  It never edits an
existing ``~/.codex/config.toml`` or registers a global MCP server; the plugin
owns its bundled MCP mapping.  Plugin marketplace commands are optional and
explicit because they change Codex user configuration.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "nexus.desktop.local.v1"
WORKSPACE_SCHEMA_VERSION = "nexus.mcp.workspace.v1"
CONFIG_FILENAME = "nexus-desktop-plugin.json"
MARKETPLACE_NAME = "nexus-local-pilot"
PLUGIN_NAME = "nexus-desktop"


class SetupError(RuntimeError):
    """A deterministic, user-actionable setup failure."""


def default_data_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    return Path(local_app_data) / "Nexus" if local_app_data else Path.home() / ".nexus"


def default_codex_command() -> str:
    """Prefer the npm CMD shim; PowerShell and packaged EXEs may not be spawnable."""
    return shutil.which("codex.cmd") or shutil.which("codex.exe") or "codex"


def require_codex_cli(value: str) -> str:
    """Resolve and harmlessly probe the supported host CLI before mutation."""
    if not isinstance(value, str) or not value.strip():
        raise SetupError("Codex CLI is unavailable: plugin registration requires a runnable Codex CLI for this Windows user")
    requested = value.strip()
    candidate = Path(requested).expanduser()
    if candidate.is_absolute():
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise SetupError(
                "Codex CLI is unavailable: plugin registration requires a runnable Codex CLI for this Windows user"
            ) from exc
        if not resolved.is_file() or resolved.is_symlink():
            raise SetupError("Codex CLI is unavailable: plugin registration requires a runnable Codex CLI for this Windows user")
        command = str(resolved)
    else:
        command = shutil.which(requested) or ""
        if not command:
            raise SetupError("Codex CLI is unavailable: plugin registration requires a runnable Codex CLI for this Windows user")
    try:
        probe = subprocess.run(
            [command, "plugin", "--help"], check=False, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=15, shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SetupError("Codex CLI cannot start: plugin registration requires a runnable Codex CLI for this Windows user") from exc
    if probe.returncode:
        raise SetupError("Codex CLI is incompatible: its plugin command is unavailable for this Windows user")
    return command


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(path)


def backup(path: Path, backup_dir: Path) -> None:
    if path.is_file():
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_dir / f"{path.name}.{utc_stamp()}.bak")


def require_directory(value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute() or path == Path(path.anchor):
        raise SetupError(f"{label} must be an absolute non-root directory")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise SetupError(f"{label} does not exist") from exc
    if not resolved.is_dir() or resolved.is_symlink():
        raise SetupError(f"{label} must be a real directory")
    return resolved


def require_file(value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise SetupError(f"{label} must be an absolute file")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise SetupError(f"{label} does not exist") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise SetupError(f"{label} must be a real file")
    return resolved


def default_runtime_python(data_root: Path) -> Path:
    return data_root / "runtime-r2" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def create_runtime(data_root: Path) -> Path:
    runtime_root = data_root / "runtime-r2"
    if sys.version_info < (3, 10):
        raise SetupError("Python 3.10 or newer is required")
    if runtime_root.exists():
        raise SetupError("Nexus runtime already exists; use an explicit compatible runtime or uninstall it first")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(runtime_root)], check=True)
        python = default_runtime_python(data_root)
        release_lock = ROOT / "requirements-release.lock"
        wheelhouse = ROOT / "wheelhouse"
        if release_lock.is_file() and wheelhouse.is_dir():
            subprocess.run([
                str(python), "-m", "pip", "install", "--quiet", "--no-index", "--only-binary=:all:",
                "--find-links", str(wheelhouse), "--require-hashes", "--no-compile", "-r", str(release_lock),
            ], check=True)
        else:
            # Compatibility path for the pre-distribution private pilot only.
            subprocess.run([str(python), "-m", "pip", "install", "-r", str(ROOT / "requirements-r2-mcp.txt")], check=True)
        return require_file(str(python), "runtime Python")
    except Exception:
        if runtime_root.exists():
            shutil.rmtree(runtime_root)
        raise


def load_workspaces(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": WORKSPACE_SCHEMA_VERSION, "workspaces": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SetupError("existing workspace configuration is invalid") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != WORKSPACE_SCHEMA_VERSION or not isinstance(payload.get("workspaces"), dict):
        raise SetupError("existing workspace configuration is invalid")
    return payload


def prepare_workspace_registration(
    data_root: Path, workspace_id: str, workspace_root: str,
) -> tuple[Path, dict[str, Any]]:
    """Validate an additive registration before any installer mutation."""
    root = require_directory(workspace_root, "workspace root")
    if not workspace_id.replace("-", "").replace("_", "").isalnum():
        raise SetupError("workspace ID must contain only letters, numbers, hyphens, or underscores")
    workspaces = load_workspaces(data_root / "workspaces.json")
    if workspace_id in workspaces["workspaces"]:
        existing = workspaces["workspaces"][workspace_id]
        if not isinstance(existing, dict) or not isinstance(existing.get("root"), str):
            raise SetupError("existing workspace registration is invalid")
        if require_directory(existing["root"], "registered workspace root") != root:
            raise SetupError("workspace ID already belongs to a different root; existing mapping preserved")
    return root, workspaces


def run_plugin_install(codex_command: str) -> None:
    # The official CLI owns config mutation and marketplace identity; no TOML is
    # parsed or rewritten by this installer.
    codex_command = require_codex_cli(codex_command)
    standalone = subprocess.run(
        [codex_command, "mcp", "get", "nexus-r2-local"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if standalone.returncode == 0:
        raise SetupError(
            "standalone nexus-r2-local is already configured; do not install a duplicate Plugin MCP. "
            "Remove or disable it temporarily, keep its trusted configuration for rollback, then retry."
        )
    marketplaces = subprocess.run(
        [codex_command, "plugin", "marketplace", "list"],
        check=True,
        capture_output=True,
        text=True,
    )
    if MARKETPLACE_NAME not in marketplaces.stdout:
        subprocess.run([codex_command, "plugin", "marketplace", "add", str(ROOT)], check=True)
    subprocess.run([codex_command, "plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"], check=True)


def run_plugin_uninstall(codex_command: str) -> None:
    codex_command = require_codex_cli(codex_command)
    subprocess.run([codex_command, "plugin", "remove", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"], check=True)
    subprocess.run([codex_command, "plugin", "marketplace", "remove", MARKETPLACE_NAME], check=True)


def install(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root).expanduser().resolve()
    workspace_root, _ = prepare_workspace_registration(data_root, args.workspace_id, args.workspace_root)
    runtime_python = require_file(args.runtime_python, "runtime Python") if args.runtime_python else create_runtime(data_root)
    if args.runtime_python:
        subprocess.run([str(runtime_python), "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"], check=True)
    config_path = data_root / CONFIG_FILENAME
    workspace_path = data_root / "workspaces.json"
    backups = data_root / "backups"
    _, workspaces = prepare_workspace_registration(data_root, args.workspace_id, args.workspace_root)
    backup(config_path, backups)
    backup(workspace_path, backups)
    if args.workspace_id not in workspaces["workspaces"]:
        workspaces["workspaces"][args.workspace_id] = {"root": str(workspace_root)}
    atomic_json_write(workspace_path, workspaces)
    atomic_json_write(config_path, {
        "schema_version": SCHEMA_VERSION,
        "nexus_root": str(ROOT.resolve()),
        "python_executable": str(runtime_python),
        "workspace_config": str(workspace_path.resolve()),
    })
    if args.with_plugin:
        if shutil.which("python") is None:
            raise SetupError("the Plugin launcher requires a `python` command on PATH")
        run_plugin_install(args.codex_command)
    print(f"Nexus local configuration ready: {config_path}")
    print(f"Workspace registered: {args.workspace_id}")
    return 0


def check(args: argparse.Namespace) -> int:
    config_path = Path(args.data_root).expanduser().resolve() / CONFIG_FILENAME
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError
        require_directory(payload["nexus_root"], "Nexus root")
        require_file(payload["python_executable"], "runtime Python")
        workspaces = load_workspaces(require_file(payload["workspace_config"], "workspace configuration"))
        if not workspaces["workspaces"]:
            raise SetupError("workspace configuration has no workspace")
    except (KeyError, ValueError, SetupError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SetupError("Nexus local configuration check failed") from exc
    print("Nexus local configuration check passed")
    return 0


def uninstall(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root).expanduser().resolve()
    config_path = data_root / CONFIG_FILENAME
    workspace_path = data_root / "workspaces.json"
    backups = data_root / "backups"
    if args.remove_plugin:
        run_plugin_uninstall(args.codex_command)
    for path in (config_path, workspace_path):
        backup(path, backups)
        if path.exists():
            path.unlink()
    if args.remove_runtime:
        runtime_root = data_root / "runtime-r2"
        if runtime_root.exists():
            shutil.rmtree(runtime_root)
    print("Nexus local configuration removed; backups remain in the Nexus data directory")
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Nexus Desktop Plugin setup")
    cli.add_argument("--data-root", default=str(default_data_root()), help="Nexus-owned private local data directory")
    cli.add_argument("--codex-command", default=default_codex_command(), help="Codex CLI executable for explicit plugin lifecycle commands")
    commands = cli.add_subparsers(dest="command", required=True)
    install_command = commands.add_parser("install", help="create local Nexus runtime configuration")
    install_command.add_argument("--workspace-id", default="nexus-default", help="opaque Plugin workspace alias; defaults to nexus-default")
    install_command.add_argument("--workspace-root", required=True)
    install_command.add_argument("--runtime-python", help="existing Python that already has the fixed R2 MCP dependency")
    install_command.add_argument("--with-plugin", action="store_true", help="also use the official Codex CLI to add the local marketplace and plugin")
    install_command.set_defaults(handler=install)
    check_command = commands.add_parser("check", help="validate private local configuration")
    check_command.set_defaults(handler=check)
    uninstall_command = commands.add_parser("uninstall", help="remove only Nexus-owned local configuration")
    uninstall_command.add_argument("--remove-plugin", action="store_true", help="also remove the named Nexus plugin and marketplace through Codex CLI")
    uninstall_command.add_argument("--remove-runtime", action="store_true", help="also remove the Nexus-owned virtual environment")
    uninstall_command.set_defaults(handler=uninstall)
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (SetupError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Nexus setup failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
