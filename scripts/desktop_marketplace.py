"""Safe per-user Nexus Marketplace adapter for ChatGPT Desktop.

The adapter deliberately manages only the documented personal marketplace at
``~/.agents/plugins/marketplace.json``, its own state directory beside that
manifest, and its own plugin copy at ``~/plugins/nexus-desktop``.  The latter
is important: ChatGPT Desktop discovers marketplace entries and loads their
bundled skills through different host paths.  The documented personal-marketplace
layout uses ``./plugins/<plugin>`` (relative to the user profile), not a plugin
copy nested below ``.agents``.  It does *not* write ``~/.codex/config.toml``,
invoke Codex, alter PATH, or automate Desktop UI.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from typing import Any

if __package__:
    from .release_common import ReleaseError, sha256_file
else:
    from release_common import ReleaseError, sha256_file


MARKETPLACE_FILENAME = "marketplace.json"
MANAGED_DIRECTORY = "nexus-marketplace"
STATE_FILENAME = "nexus-marketplace-state.json"
STATE_SCHEMA = "nexus.desktop.marketplace.state.v1"
PLUGIN_NAME = "nexus-desktop"
PLUGIN_FOLDER = "plugins/nexus-desktop"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _atomic_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(value)
            handle.flush()
            # A torn marketplace write is worse than a failed installation.
            # fsync is supported by normal NTFS files and harmless elsewhere.
            __import__("os").fsync(handle.fileno())
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
    temporary.replace(path)


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _profile_root(profile_home: Path | None = None) -> Path:
    candidate = (profile_home or Path.home()).expanduser()
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("Windows user profile is unavailable") from exc
    if not resolved.is_dir() or resolved == Path(resolved.anchor):
        raise ReleaseError("Windows user profile is invalid")
    return resolved


def _real_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("personal marketplace directory is unavailable") from exc
    if not resolved.is_dir() or resolved.is_symlink():
        raise ReleaseError("personal marketplace directory must be a real directory")
    return resolved


def paths(profile_home: Path | None = None) -> tuple[Path, Path, Path]:
    """Return trusted personal marketplace, Nexus-owned state root, and state path."""
    profile = _profile_root(profile_home)
    agents = _real_directory(profile / ".agents")
    marketplace_root = _real_directory(agents / "plugins")
    managed_root = _real_directory(marketplace_root / MANAGED_DIRECTORY)
    if marketplace_root not in managed_root.parents:
        raise ReleaseError("Nexus marketplace root is outside the personal marketplace")
    return marketplace_root / MARKETPLACE_FILENAME, managed_root, managed_root / STATE_FILENAME


def plugin_root(profile_home: Path | None = None) -> Path:
    """Return the documented, host-indexed personal plugin location."""
    profile = _profile_root(profile_home)
    root = _real_directory(profile / "plugins")
    target = root / PLUGIN_NAME
    if root not in target.parents:
        raise ReleaseError("Nexus plugin root is outside the user plugin directory")
    return target


def _uncreated_marketplace_path(profile_home: Path | None = None) -> Path:
    """Calculate the documented location without changing a fresh profile."""
    profile = _profile_root(profile_home)
    return profile / ".agents" / "plugins" / MARKETPLACE_FILENAME


def _load_marketplace(path: Path) -> tuple[dict[str, Any], bytes | None]:
    if not path.exists():
        return {"name": "personal-marketplace", "plugins": []}, None
    if not path.is_file() or path.is_symlink():
        raise ReleaseError("personal marketplace manifest must be a real file")
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("personal marketplace manifest is invalid") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("name"), str) or not payload["name"].strip():
        raise ReleaseError("personal marketplace manifest is invalid")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or not all(isinstance(item, dict) for item in plugins):
        raise ReleaseError("personal marketplace manifest is invalid")
    for item in plugins:
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ReleaseError("personal marketplace manifest contains an invalid plugin entry")
    return payload, raw


def _relative_plugin_path(_version: str) -> str:
    """Return the canonical source path for ``~/.agents/plugins``.

    Personal marketplaces resolve ``./plugins/<name>`` from the user profile.
    Keeping this path stable also allows Desktop to refresh the installed
    plugin's skills instead of leaving them in a marketplace-only staging tree.
    """
    candidate = f"./plugins/{PLUGIN_NAME}"
    pure = PurePosixPath(candidate)
    if not candidate.startswith("./") or ".." in pure.parts or pure.is_absolute():
        raise ReleaseError("Nexus marketplace plugin path is invalid")
    return candidate


def _entry(version: str) -> dict[str, Any]:
    return {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": _relative_plugin_path(version)},
        # This is a documented personal-marketplace policy request.  Whether a
        # particular Desktop build consumes it automatically is intentionally
        # a human acceptance question, never an installer assumption.
        "policy": {"installation": "INSTALLED_BY_DEFAULT", "authentication": "ON_INSTALL"},
        "category": "Developer tools",
    }


def _load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("Nexus marketplace ownership state is invalid") from exc
    return _validate_state(payload)


def _validate_state(payload: Any) -> dict[str, Any]:
    """Validate an in-memory ownership record, including rollback state."""
    required = {
        "schema_version", "owner", "version", "marketplace_path", "plugin_root",
        "marketplace_before", "marketplace_after_sha256", "entry", "previous_state",
    }
    if not isinstance(payload, dict) or set(payload) != required or payload.get("schema_version") != STATE_SCHEMA or payload.get("owner") != "Nexus":
        raise ReleaseError("Nexus marketplace ownership state is invalid")
    if not isinstance(payload["version"], str) or not isinstance(payload["marketplace_before"], str):
        raise ReleaseError("Nexus marketplace ownership state is invalid")
    if not isinstance(payload["marketplace_after_sha256"], str) or len(payload["marketplace_after_sha256"]) != 64:
        raise ReleaseError("Nexus marketplace ownership state is invalid")
    if not isinstance(payload["entry"], dict) or not isinstance(payload["previous_state"], (dict, type(None))):
        raise ReleaseError("Nexus marketplace ownership state is invalid")
    return payload


def _contained(path: Path, root: Path) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("Nexus marketplace path is unavailable") from exc
    if root not in resolved.parents and resolved != root:
        raise ReleaseError("Nexus marketplace path escapes its owned directory")
    if resolved.is_symlink():
        raise ReleaseError("Nexus marketplace path must not be a symlink")
    return resolved


def _same_path(left: Path, right: Path) -> bool:
    """Compare canonical Windows paths without trusting spelling/case."""
    return os.path.normcase(str(left.resolve(strict=False))) == os.path.normcase(str(right.resolve(strict=False)))


def _prepare_plugin(
    release_root: Path,
    managed_root: Path,
    version: str,
    runtime: Path,
    nexus_data_root: Path,
    profile_home: Path | None = None,
) -> Path:
    source = release_root / PLUGIN_FOLDER
    if not source.is_dir() or source.is_symlink():
        raise ReleaseError("verified release plugin source is unavailable")
    runtime = runtime.resolve(strict=True)
    expected_runtime = (release_root / "runtime" / "python" / "python.exe").resolve(strict=True)
    if runtime != expected_runtime or not runtime.is_file() or runtime.is_symlink():
        raise ReleaseError("Nexus marketplace launcher must use the release-owned runtime")
    try:
        nexus_data_root = nexus_data_root.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("Nexus marketplace launcher data root is unavailable") from exc
    if not nexus_data_root.is_dir() or nexus_data_root.is_symlink() or nexus_data_root == Path(nexus_data_root.anchor):
        raise ReleaseError("Nexus marketplace launcher data root is invalid")
    target = plugin_root(profile_home)
    target_parent = target.parent
    if target.exists():
        existing = _owned_plugin(target, target_parent)
        try:
            existing_owner = json.loads((existing / ".nexus-marketplace-owner.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReleaseError("Nexus marketplace plugin ownership cannot be verified") from exc
        if existing_owner.get("version") == version:
            return existing
    stage = managed_root / ".staging" / version / "nexus-desktop"
    if stage.exists():
        raise ReleaseError("interrupted Nexus marketplace preparation requires rollback before retry")
    stage.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, stage, symlinks=False)
    mcp_path = stage / ".mcp.json"
    try:
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        server = mcp["mcpServers"]["nexus_desktop_local"]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        shutil.rmtree(stage, ignore_errors=True)
        raise ReleaseError("verified release plugin MCP manifest is invalid") from exc
    if not isinstance(server, dict):
        shutil.rmtree(stage, ignore_errors=True)
        raise ReleaseError("verified release plugin MCP manifest is invalid")
    server["command"] = str(runtime)
    server["args"] = ["./scripts/launch_nexus_mcp.py"]
    server["cwd"] = "."
    # This is a per-process MCP setting, not a user/global environment change.
    # It keeps the bridge correct when a caller deliberately selects a
    # non-default Nexus data root.
    server["env"] = {"NEXUS_DATA_ROOT": str(nexus_data_root)}
    _atomic_bytes(mcp_path, _json_bytes(mcp))
    marker = {
        "schema_version": STATE_SCHEMA,
        "owner": "Nexus",
        "version": version,
        "release_runtime": str(runtime),
        "release_plugin_sha256": sha256_file(source / ".mcp.json"),
    }
    _atomic_bytes(stage / ".nexus-marketplace-owner.json", _json_bytes(marker))
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        # Preserve the exact earlier Nexus-owned plugin until the new source is
        # fully staged.  This is per-user, reversible state; no third-party
        # plugin is ever moved or overwritten.
        retired = managed_root / "retired" / f"nexus-desktop-{existing_owner['version']}"
        if retired.exists():
            _contained(retired, managed_root)
            raise ReleaseError("a previous Nexus plugin backup already exists; use rollback before retry")
        retired.parent.mkdir(parents=True, exist_ok=True)
        target.replace(retired)
        try:
            stage.replace(target)
        except Exception:
            retired.replace(target)
            raise
    else:
        stage.replace(target)
    _contained(target, target_parent)
    return target


def _owned_plugin(path: Path, managed_root: Path) -> Path:
    if not path.exists():
        raise ReleaseError("Nexus marketplace plugin ownership cannot be verified")
    resolved = _contained(path, managed_root)
    marker = resolved / ".nexus-marketplace-owner.json"
    try:
        owner = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("Nexus marketplace plugin ownership cannot be verified") from exc
    if not isinstance(owner, dict) or owner.get("owner") != "Nexus" or owner.get("schema_version") != STATE_SCHEMA:
        raise ReleaseError("Nexus marketplace plugin ownership cannot be verified")
    return resolved


def _remove_owned_plugin(path: Path, owner_root: Path) -> None:
    resolved = _owned_plugin(path, owner_root)
    shutil.rmtree(resolved)


def _remove_retired_plugins(managed_root: Path) -> None:
    """Remove only Nexus-owned superseded copies after ownership verification."""
    retired_root = managed_root / "retired"
    if not retired_root.exists():
        return
    _contained(retired_root, managed_root)
    for candidate in retired_root.iterdir():
        _owned_plugin(candidate, retired_root)
    shutil.rmtree(retired_root)


def install(release_root: Path, version: str, runtime: Path, nexus_data_root: Path, profile_home: Path | None = None) -> dict[str, Any]:
    """Prepare Nexus' documented personal marketplace source without a host CLI."""
    # Validate an existing user file before creating even our own directory.
    # A malformed Marketplace must remain wholly untouched on failure.
    provisional_marketplace = _uncreated_marketplace_path(profile_home)
    payload, before = _load_marketplace(provisional_marketplace)
    marketplace, managed_root, state_path = paths(profile_home)
    if not _same_path(marketplace, provisional_marketplace):
        raise ReleaseError("personal marketplace location changed during setup")
    existing_state = _load_state(state_path)
    desired = _entry(version)
    matches = [item for item in payload["plugins"] if item.get("name") == PLUGIN_NAME]
    if matches:
        if existing_state and len(matches) == 1 and matches[0] == existing_state["entry"]:
            if existing_state["version"] == version and matches[0] == desired:
                # RC5+ entries use the host-indexed profile plugin root.  A
                # legacy RC4 entry may be Nexus-owned too, but it must never
                # be treated as a successful RC5 installation merely because
                # Plugin Management can see its marketplace card.
                current_plugin = Path(existing_state["plugin_root"])
                expected_plugin = plugin_root(profile_home)
                if _same_path(current_plugin, expected_plugin):
                    verified = _owned_plugin(current_plugin, current_plugin.parent)
                    if verified.is_dir():
                        return existing_state
                else:
                    # Preserve a verified RC4 copy as the previous state for
                    # rollback.  The new marketplace entry will point only to
                    # the documented profile-level source path.
                    _owned_plugin(current_plugin, managed_root)
            payload["plugins"] = [item for item in payload["plugins"] if item.get("name") != PLUGIN_NAME]
        else:
            raise ReleaseError("an unmanaged Nexus marketplace entry already exists; refusing to overwrite it")
    plugin_location = _prepare_plugin(release_root, managed_root, version, runtime, nexus_data_root, profile_home)
    backup_bytes = before if before is not None else b""
    backup_path = managed_root / "backups" / f"marketplace-{_sha256_bytes(backup_bytes)}.json.b64"
    if not backup_path.exists():
        _atomic_bytes(backup_path, base64.b64encode(backup_bytes) + b"\n")
    payload["plugins"].append(desired)
    after = _json_bytes(payload)
    try:
        _atomic_bytes(marketplace, after)
        state = {
            "schema_version": STATE_SCHEMA,
            "owner": "Nexus",
            "version": version,
            "marketplace_path": str(marketplace),
            "plugin_root": str(plugin_location),
            "marketplace_before": str(backup_path),
            "marketplace_after_sha256": _sha256_bytes(after),
            "entry": desired,
            "previous_state": existing_state,
        }
        _atomic_bytes(state_path, _json_bytes(state))
        return state
    except Exception:
        # The prior marketplace file is restored only if this adapter was the
        # last writer; otherwise preserve the user's newer configuration.
        if marketplace.exists() and _sha256_bytes(marketplace.read_bytes()) == _sha256_bytes(after):
            if before is None:
                marketplace.unlink(missing_ok=True)
            else:
                _atomic_bytes(marketplace, before)
        _remove_owned_plugin(plugin_location, plugin_location.parent)
        raise


def _restore_backup(state: dict[str, Any], marketplace: Path) -> None:
    backup = Path(state["marketplace_before"])
    try:
        encoded = backup.read_bytes().strip()
        raw = base64.b64decode(encoded, validate=True)
    except (OSError, ValueError) as exc:
        raise ReleaseError("Nexus marketplace backup is unavailable or invalid") from exc
    if raw:
        _atomic_bytes(marketplace, raw)
    else:
        marketplace.unlink(missing_ok=True)


def uninstall(profile_home: Path | None = None, rollback: bool = False) -> dict[str, Any] | None:
    """Remove only Nexus-owned Marketplace material; never touch host config."""
    marketplace, managed_root, state_path = paths(profile_home)
    state = _load_state(state_path)
    if state is None:
        raise ReleaseError("no Nexus personal marketplace installation is recorded")
    if not _same_path(Path(state["marketplace_path"]), marketplace):
        raise ReleaseError("Nexus marketplace ownership state targets another profile")
    current, raw = _load_marketplace(marketplace)
    if raw is None:
        raise ReleaseError("Nexus marketplace manifest disappeared; refusing to remove plugin files")
    entry = state["entry"]
    occurrences = [item for item in current["plugins"] if item == entry]
    if len(occurrences) != 1:
        raise ReleaseError("Nexus marketplace entry changed; refusing to remove unrelated configuration")
    # Verify every controlled deletion target before changing the user's
    # Marketplace manifest. A forged state file must be entirely fail-closed.
    plugin_location = Path(state["plugin_root"])
    current_plugin_root = _owned_plugin(plugin_location, plugin_location.parent)
    previous = state["previous_state"] if rollback else None
    previous_location: Path | None = None
    retired_previous: Path | None = None
    if previous is not None:
        # State nesting is trusted only after the same schema checks used for a
        # top-level record.  This is important before moving any retained copy.
        _validate_state(previous)
        previous_location = Path(previous["plugin_root"])
        if _same_path(previous_location, plugin_root(profile_home)):
            candidate = managed_root / "retired" / f"nexus-desktop-{previous['version']}"
            if candidate.exists():
                retired_previous = _owned_plugin(candidate, candidate.parent)
            elif not previous_location.exists():
                raise ReleaseError("Nexus rollback source is unavailable; refusing to remove current plugin")
        else:
            # An RC4 source was already in the managed tree and was retained
            # in place during migration to the host-indexed layout.
            _owned_plugin(previous_location, managed_root)
    if rollback and _sha256_bytes(raw) == state["marketplace_after_sha256"]:
        _restore_backup(state, marketplace)
    else:
        current["plugins"] = [item for item in current["plugins"] if item != entry]
        _atomic_bytes(marketplace, _json_bytes(current))
    _remove_owned_plugin(current_plugin_root, current_plugin_root.parent)
    if rollback and retired_previous is not None and previous_location is not None:
        if previous_location.exists():
            raise ReleaseError("Nexus rollback target already exists; refusing to overwrite it")
        previous_location.parent.mkdir(parents=True, exist_ok=True)
        retired_previous.replace(previous_location)
        if not any(retired_previous.parent.iterdir()):
            retired_previous.parent.rmdir()
    if not rollback:
        _remove_retired_plugins(managed_root)
    if not rollback and isinstance(state["previous_state"], dict):
        # RC4 stored its copied source below our managed marketplace tree.
        # RC5 preserves that verified copy only long enough to make rollback
        # lossless.  A normal uninstall must clean it up too; otherwise an
        # obsolete Nexus-owned source could survive after its marketplace
        # entry has been removed.
        legacy_location = Path(state["previous_state"].get("plugin_root", ""))
        if legacy_location.exists():
            _remove_owned_plugin(legacy_location, managed_root)
    if previous is not None:
        _atomic_bytes(state_path, _json_bytes(previous))
    else:
        state_path.unlink(missing_ok=True)
    return previous
