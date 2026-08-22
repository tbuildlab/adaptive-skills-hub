# Portable Nexus installation

## Prerequisites

- Windows with a `python` command available to ChatGPT Desktop/Codex for the
  Plugin launcher.
- Python 3.10 or newer to create the dedicated R2 environment.
- A clone of the private Nexus repository; Git is optional after source is
  obtained.
- One approved, non-root local project directory. Network access is needed only
  when setup installs the fixed R2 Python dependency; an existing compatible
  runtime can be supplied with `--runtime-python` instead.

No API key, OAuth account, remote MCP endpoint, administrator permission, or
personal Skill library is required.

## Install lifecycle

1. Clone/download the private source into any normal local directory. The source
   is location-independent; no `D:` path is embedded in package files.
2. Run `python scripts/setup_nexus.py install --workspace-root <absolute-project-root>`. It assigns the private Plugin alias `nexus-default`; an explicit alternate `--workspace-id` remains available for standalone administrative use.
3. Run `python scripts/setup_nexus.py check`.
4. For an optional Desktop Plugin test, add the local marketplace and Plugin with
   the same install command plus `--with-plugin`, then restart Desktop and use a
   new conversation.
5. For an update, validate the clone and plugin manifest, create one cachebuster,
   reinstall `nexus-desktop@nexus-local-pilot`, and start a new conversation.
6. For removal, run `python scripts/setup_nexus.py uninstall --remove-plugin`.
   It removes only named Nexus configuration and retains backups.

The installer deliberately does not change `~/.codex/config.toml`; that protects
unrelated MCP servers and makes standalone R3 rollback explicit and reversible.

## Archive

Create a private review archive outside the source directory:

```powershell
python scripts/package_nexus.py --output C:\Temp\nexus-desktop-pilot.zip
```

The adjacent `.sha256` receipt must match the archive. Before sharing a private
archive, inspect its member list and confirm it has no `.env`, local data,
credentials, absolute developer paths, private Skills, logs, or runtime state.
