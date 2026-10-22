#!/usr/bin/env python3
"""Transactional installer for a verified Nexus GitHub Release tree.

It is intentionally a local-only lifecycle tool.  It never downloads code,
edits TOML, invokes a shell, starts a remote MCP server, invokes Codex, or
accepts an unverified release root.  Plugin discovery is registered through
the documented per-user ChatGPT Desktop personal marketplace instead.
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


def _configure_utf8_stdout() -> None:
    """Keep the documented Desktop action readable in legacy Windows consoles.

    The RC6 action uses the Unicode ``→`` separator.  A fresh embedded Python
    process can otherwise inherit a legacy code page and turn a successful
    source preparation into a late ``UnicodeEncodeError``.  This changes only
    this process's output encoding; it does not alter a user's console, PATH,
    or system locale.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")


_configure_utf8_stdout()

# The official embeddable Python's ._pth isolation intentionally omits the
# script directory. Add only this verified release-local directory so sibling
# lifecycle modules remain importable; do not consult PATH or user site paths.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

if __package__:
    from . import setup_nexus as setup
    from . import desktop_marketplace
    from .release_common import ReleaseError, atomic_json_write, verify_release_tree
else:
    import setup_nexus as setup
    import desktop_marketplace
    from release_common import ReleaseError, atomic_json_write, verify_release_tree


ROOT = Path(__file__).resolve().parents[1]
STATE_FILENAME = "github-release-state.json"
STATE_SCHEMA = "nexus.github.release.state.v2"


def diagnostic(message: str) -> None:
    """Emit opt-in lifecycle diagnostics without exposing configuration values."""
    if os.environ.get("NEXUS_RELEASE_DIAGNOSTICS") == "1":
        print(f"Nexus release diagnostic: {message}", file=sys.stderr, flush=True)


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


def configure(args: argparse.Namespace, root: Path) -> None:
    runtime = bundled_runtime(root)
    setup.install(argparse.Namespace(
        data_root=str(data_root(args.data_root)),
        workspace_root=args.workspace_root,
        workspace_id=args.workspace_id,
        runtime_python=str(runtime),
        with_plugin=False,
        # This remains a compatibility field of the pre-RC4 local setup
        # helper.  The distributable marketplace path never invokes it.
        codex_command="",
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
    diagnostic("probing the release-owned embedded Python runtime")
    result = subprocess.run(
        [str(resolved), "-I", "-B", "-c", "import mcp, sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"],
        cwd=str(resolved.parent), capture_output=True, text=True, timeout=20, shell=False,
    )
    if result.returncode:
        raise ReleaseError("release-owned embedded Python runtime is incompatible")
    return resolved


def current_install(root: Path) -> dict[str, Any] | None:
    current = read_json(state_path(root))
    if current is not None and current.get("schema_version") not in {"nexus.github.release.state.v1", STATE_SCHEMA}:
        raise ReleaseError("existing Nexus release state is invalid")
    return current


def install(args: argparse.Namespace) -> int:
    diagnostic("verifying extracted release integrity")
    manifest = verify_release_tree(ROOT)
    local = data_root(args.data_root)
    prior = current_install(local)
    config = local / setup.CONFIG_FILENAME
    workspaces = local / "workspaces.json"
    setup.prepare_workspace_registration(local, args.workspace_id, args.workspace_root)
    # Re-applying the exact same release is an idempotent repair/refresh, not
    # a new upgrade layer.  Retain its original rollback boundary so rollback
    # cannot restore a state record after removing the corresponding source.
    same_release = bool(
        prior
        and prior.get("version") == manifest["version"]
        and prior.get("mode") == args.mode
        and prior.get("release_root") == str(ROOT.resolve())
    )
    if same_release:
        retained_files = prior.get("previous_files")
        if not isinstance(retained_files, dict) or set(retained_files) != {"config", "workspaces"}:
            raise ReleaseError("existing Nexus release state is invalid")
        previous_files = retained_files
        previous_install = prior.get("previous_install")
    else:
        previous_files = {"config": snapshot_file(config), "workspaces": snapshot_file(workspaces)}
        previous_install = prior
    # Plugin mode uses the release-local runtime declared in its staged MCP
    # manifest.  Do not consult python.exe, py.exe, aliases, or PATH.
    runtime = bundled_runtime(ROOT)
    if prior and prior.get("schema_version") != STATE_SCHEMA and prior.get("mode") == "plugin":
        raise ReleaseError("an earlier CLI-managed Nexus plugin installation must be uninstalled with its original release before Marketplace installation")
    if args.migrate_standalone:
        raise ReleaseError("standalone MCP migration is intentionally unavailable in Marketplace mode; keep standalone mode separate")
    journal = local / "transactions" / f"install-{setup.utc_stamp()}.json"
    atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "prepared", "release_root": str(ROOT), "version": manifest["version"]})
    marketplace_prepared = False
    try:
        if args.mode == "plugin":
            diagnostic("preparing the Nexus personal Marketplace source")
            marketplace_state = desktop_marketplace.install(ROOT, manifest["version"], runtime, local)
            marketplace_prepared = True
        else:
            marketplace_state = None
        diagnostic("writing Nexus-owned workspace configuration")
        configure(args, ROOT)
        new_state = {
            "schema_version": STATE_SCHEMA,
            "version": manifest["version"],
            "release_root": str(ROOT.resolve()),
            "mode": args.mode,
            "marketplace": marketplace_state,
            "previous_install": previous_install,
            "previous_files": previous_files,
        }
        atomic_json_write(state_path(local), new_state)
        atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "committed", "release_root": str(ROOT), "version": manifest["version"]})
    except Exception:
        try:
            restore_file(config, previous_files["config"])
            restore_file(workspaces, previous_files["workspaces"])
            if marketplace_prepared:
                desktop_marketplace.uninstall(rollback=True)
            atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "rolled_back", "release_root": str(ROOT)})
        except Exception as rollback_error:
            atomic_json_write(journal, {"schema_version": STATE_SCHEMA, "status": "manual_recovery_required", "release_root": str(ROOT), "error": str(rollback_error)})
        raise
    if args.mode == "plugin":
        print("Nexus personal marketplace source is ready. Required action: ChatGPT Desktop → Plugins → Personal → Nexus → + Install")
        print(f"Nexus {manifest['version']} source preparation completed. Start a new chat after ChatGPT Desktop installs the Plugin.")
    else:
        print(f"Nexus {manifest['version']} installed in standalone mode")
    return 0


def uninstall(args: argparse.Namespace, rollback: bool = False) -> int:
    diagnostic("verifying extracted release integrity")
    verify_release_tree(ROOT)
    local = data_root(args.data_root)
    state = current_install(local)
    if not state:
        raise ReleaseError("no Nexus GitHub Release installation is recorded")
    if state.get("mode") == "plugin":
        desktop_marketplace.uninstall(rollback=rollback)
    if rollback:
        previous = state.get("previous_install")
        files = state.get("previous_files", {})
        if not isinstance(files, dict):
            raise ReleaseError("existing Nexus release state is invalid")
        restore_file(local / setup.CONFIG_FILENAME, files.get("config"))
        restore_file(local / "workspaces.json", files.get("workspaces"))
        if isinstance(previous, dict):
            atomic_json_write(state_path(local), previous)
        else:
            state_path(local).unlink(missing_ok=True)
        print("Nexus release rollback restored the prior local state")
        return 0
    setup.uninstall(argparse.Namespace(data_root=str(local), remove_plugin=False, remove_runtime=args.remove_runtime, codex_command=""))
    state_path(local).unlink(missing_ok=True)
    print("Nexus GitHub Release installation removed; backups remain in the Nexus data directory")
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Install a verified Nexus GitHub Release")
    cli.add_argument("--data-root", help="Nexus-owned local data directory; defaults to LOCALAPPDATA/Nexus")
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="verify this extracted release tree").set_defaults(handler=lambda _args: (verify_release_tree(ROOT), print("Nexus release integrity check passed"), 0)[2])
    for name, handler, description in (("install", install, "install a verified release"), ("upgrade", install, "activate this verified release as an upgrade")):
        command = commands.add_parser(name, help=description)
        command.add_argument("--workspace-root", required=True)
        command.add_argument("--workspace-id", default="nexus-default")
        command.add_argument("--mode", choices=("standalone", "plugin"), default="plugin")
        command.add_argument("--migrate-standalone", action="store_true", help=argparse.SUPPRESS)
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
