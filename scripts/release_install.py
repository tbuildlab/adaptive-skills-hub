#!/usr/bin/env python3
"""Transactional installer for a verified Nexus GitHub Release tree.

It is intentionally a local-only lifecycle tool.  It never downloads code,
edits TOML, invokes a shell, starts a remote MCP server, or accepts an
unverified release root.  Plugin configuration changes are delegated to the
official Codex CLI and are journaled so a failed migration restores the former
standalone MCP registration.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True
# The official embeddable Python's ._pth isolation intentionally omits the
# script directory. Add only this verified release-local directory so sibling
# lifecycle modules remain importable; do not consult PATH or user site paths.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

if __package__:
    from . import setup_nexus as setup
    from .release_common import ReleaseError, atomic_json_write, verify_release_tree
else:
    import setup_nexus as setup
    from release_common import ReleaseError, atomic_json_write, verify_release_tree


ROOT = Path(__file__).resolve().parents[1]
STATE_FILENAME = "github-release-state.json"
STATE_SCHEMA = "nexus.github.release.state.v1"
STANDALONE_NAME = "nexus-r2-local"


def data_root(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else setup.default_data_root().resolve()


def state_path(root: Path) -> Path:
    return root / STATE_FILENAME


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("existing Nexus release state is invalid") from exc
    if not isinstance(payload, dict):
        raise ReleaseError("existing Nexus release state is invalid")
    return payload


def snapshot_file(path: Path) -> str | None:
    return base64.b64encode(path.read_bytes()).decode("ascii") if path.exists() else None


def restore_file(path: Path, value: str | None) -> None:
    if value is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".restore")
    temporary.write_bytes(base64.b64decode(value.encode("ascii"), validate=True))
    temporary.replace(path)


def standalone_snapshot(codex: str) -> dict[str, Any] | None:
    result = subprocess.run([codex, "mcp", "get", STANDALONE_NAME, "--json"], check=False, capture_output=True, text=True, shell=False)
    if result.returncode:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReleaseError("existing standalone MCP configuration is unreadable") from exc
    validate_standalone_snapshot(payload)
    return payload


def validate_standalone_snapshot(payload: Any) -> None:
    if not isinstance(payload, dict) or payload.get("name") != STANDALONE_NAME:
        raise ReleaseError("existing standalone MCP configuration is unreadable")
    transport = payload.get("transport")
    if not isinstance(transport, dict) or transport.get("type") != "stdio":
        raise ReleaseError("only a stdio standalone Nexus MCP can be migrated")
    command, args, cwd, env = transport.get("command"), transport.get("args"), transport.get("cwd"), transport.get("env")
    if not isinstance(command, str) or not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ReleaseError("existing standalone MCP configuration is unreadable")
    executable = Path(command)
    if not executable.is_absolute() or not executable.is_file() or executable.is_symlink():
        raise ReleaseError("standalone MCP migration requires an absolute real executable")
    if cwd is not None or env not in (None, {}):
        raise ReleaseError("standalone MCP migration would not be lossless; remove it manually or use standalone mode")


def restore_standalone(codex: str, snapshot: dict[str, Any]) -> None:
    validate_standalone_snapshot(snapshot)
    transport = snapshot["transport"]
    command = transport["command"]
    args = transport["args"]
    subprocess.run([codex, "mcp", "add", STANDALONE_NAME, "--", command, *args], check=True, shell=False)


def remove_standalone(codex: str) -> None:
    subprocess.run([codex, "mcp", "remove", STANDALONE_NAME], check=True, shell=False)


def remove_plugin(codex: str) -> None:
    setup.run_plugin_uninstall(codex)


def enable_plugin(codex: str) -> None:
    setup.run_plugin_install(codex)


def configure(args: argparse.Namespace, root: Path) -> None:
    runtime = bundled_runtime(root)
    setup.install(argparse.Namespace(
        data_root=str(data_root(args.data_root)),
        workspace_root=args.workspace_root,
        workspace_id=args.workspace_id,
        runtime_python=str(runtime),
        with_plugin=False,
        codex_command=args.codex_command,
    ))


def bundled_runtime(root: Path) -> Path:
    """Return the release-owned interpreter, never a system PATH executable."""
    runtime = root / "runtime" / "python" / "python.exe"
    try:
        resolved = runtime.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("release-owned embedded Python runtime is unavailable") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise ReleaseError("release-owned embedded Python runtime is unavailable")
    result = subprocess.run(
        [str(resolved), "-I", "-B", "-c", "import mcp, sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"],
        cwd=str(resolved.parent), capture_output=True, text=True, timeout=20, shell=False,
    )
    if result.returncode:
        raise ReleaseError("release-owned embedded Python runtime is incompatible")
    return resolved


def current_install(root: Path) -> dict[str, Any] | None:
    current = read_json(state_path(root))
    if current is not None and current.get("schema_version") != STATE_SCHEMA:
        raise ReleaseError("existing Nexus release state is invalid")
    return current


def restore_previous(root: Path, codex: str, previous: dict[str, Any] | None) -> None:
    """Best-effort rollback after a failed activation, preserving the first error."""
    if not previous:
        return
    mode = previous.get("mode")
    if mode == "plugin":
        old_root = Path(previous.get("release_root", ""))
        if old_root.is_dir():
            verify_release_tree(old_root)
            subprocess.run([codex, "plugin", "marketplace", "add", str(old_root)], check=True, shell=False)
            subprocess.run([codex, "plugin", "add", f"{setup.PLUGIN_NAME}@{setup.MARKETPLACE_NAME}"], check=True, shell=False)
    standalone = previous.get("standalone_before")
    if isinstance(standalone, dict):
        restore_standalone(codex, standalone)


def install(args: argparse.Namespace) -> int:
    manifest = verify_release_tree(ROOT)
    local = data_root(args.data_root)
    prior = current_install(local)
    config = local / setup.CONFIG_FILENAME
    workspaces = local / "workspaces.json"
    previous_files = {"config": snapshot_file(config), "workspaces": snapshot_file(workspaces)}
    # Plugin mode uses the release-local runtime declared in its staged MCP
    # manifest.  Do not consult python.exe, py.exe, aliases, or PATH.
    bundled_runtime(ROOT)
    # Do this before reading/migrating host registrations or creating a journal.
    # A missing host must never degrade into raw WinError 2 after partial setup.
    codex_command = setup.require_codex_cli(args.codex_command) if args.mode == "plugin" else args.codex_command
    standalone = standalone_snapshot(codex_command) if args.mode == "plugin" else None
    if args.mode == "plugin" and standalone and not args.migrate_standalone:
        raise ReleaseError("standalone nexus-r2-local exists; use --migrate-standalone or choose standalone mode")
    journal = local / "transactions" / f"install-{setup.utc_stamp()}.json"
    atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "prepared", "release_root": str(ROOT), "version": manifest["version"]})
    plugin_removed = False
    standalone_removed = False
    try:
        if prior and prior.get("mode") == "plugin":
            remove_plugin(codex_command)
            plugin_removed = True
        if args.mode == "plugin" and standalone:
            remove_standalone(codex_command)
            standalone_removed = True
        if args.mode == "plugin":
            enable_plugin(codex_command)
        configure(args, ROOT)
        new_state = {
            "schema_version": STATE_SCHEMA,
            "version": manifest["version"],
            "release_root": str(ROOT.resolve()),
            "mode": args.mode,
            "standalone_before": standalone,
            "previous_install": prior,
            "previous_files": previous_files,
        }
        atomic_json_write(state_path(local), new_state)
        atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "committed", "release_root": str(ROOT), "version": manifest["version"]})
    except Exception:
        try:
            if args.mode == "plugin":
                remove_plugin(codex_command)
            restore_file(config, previous_files["config"])
            restore_file(workspaces, previous_files["workspaces"])
            if standalone_removed and standalone:
                restore_standalone(codex_command, standalone)
            elif plugin_removed:
                restore_previous(local, codex_command, prior)
            atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "rolled_back", "release_root": str(ROOT)})
        except Exception as rollback_error:
            atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "manual_recovery_required", "release_root": str(ROOT), "error": str(rollback_error)})
        raise
    print(f"Nexus {manifest['version']} installed in {args.mode} mode")
    return 0


def uninstall(args: argparse.Namespace, rollback: bool = False) -> int:
    verify_release_tree(ROOT)
    local = data_root(args.data_root)
    state = current_install(local)
    if not state:
        raise ReleaseError("no Nexus GitHub Release installation is recorded")
    if state.get("mode") == "plugin":
        remove_plugin(args.codex_command)
    if rollback:
        previous = state.get("previous_install")
        files = state.get("previous_files", {})
        if not isinstance(files, dict):
            raise ReleaseError("existing Nexus release state is invalid")
        restore_file(local / setup.CONFIG_FILENAME, files.get("config"))
        restore_file(local / "workspaces.json", files.get("workspaces"))
        restore_previous(local, args.codex_command, previous if isinstance(previous, dict) else None)
        standalone = state.get("standalone_before")
        if not previous and isinstance(standalone, dict):
            restore_standalone(args.codex_command, standalone)
        if isinstance(previous, dict):
            atomic_json_write(state_path(local), previous)
        else:
            state_path(local).unlink(missing_ok=True)
        print("Nexus release rollback restored the prior local state")
        return 0
    setup.uninstall(argparse.Namespace(data_root=str(local), remove_plugin=False, remove_runtime=args.remove_runtime, codex_command=args.codex_command))
    state_path(local).unlink(missing_ok=True)
    print("Nexus GitHub Release installation removed; backups remain in the Nexus data directory")
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Install a verified Nexus GitHub Release")
    cli.add_argument("--data-root", help="Nexus-owned local data directory; defaults to LOCALAPPDATA/Nexus")
    cli.add_argument("--codex-command", default=setup.default_codex_command())
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="verify this extracted release tree").set_defaults(handler=lambda _args: (verify_release_tree(ROOT), print("Nexus release integrity check passed"), 0)[2])
    for name, handler, description in (("install", install, "install a verified release"), ("upgrade", install, "activate this verified release as an upgrade")):
        command = commands.add_parser(name, help=description)
        command.add_argument("--workspace-root", required=True)
        command.add_argument("--workspace-id", default="nexus-default")
        command.add_argument("--mode", choices=("standalone", "plugin"), default="plugin")
        command.add_argument("--migrate-standalone", action="store_true")
        command.set_defaults(handler=handler)
    for name, rollback, description in (("uninstall", False, "remove Nexus-owned configuration"), ("rollback", True, "restore the pre-install local state")):
        command = commands.add_parser(name, help=description)
        command.add_argument("--remove-runtime", action="store_true")
        command.set_defaults(handler=lambda args, value=rollback: uninstall(args, rollback=value))
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (ReleaseError, setup.SetupError, OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"Nexus release operation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
