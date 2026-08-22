# Install Nexus from a GitHub Release (Windows RC)

## Prerequisites

This path needs no repository clone, `D:` drive, administrator rights, API key,
OAuth, remote MCP, Microsoft Store, `py.exe`, or preinstalled Python. RC2
contains a pinned, Nexus-owned CPython 3.13.15 x64 runtime and the reviewed R2
dependencies. You need supported 64-bit Windows and one real non-root
workspace directory. **Plugin mode additionally requires a runnable local
Codex CLI with the `plugin` command for the same Windows user.** The CLI is the
only supported component that registers a local marketplace; ChatGPT Desktop
visibility alone does not expose a configuration interface this installer may
rewrite. Download the ZIP, ZIP receipt, PowerShell bootstrap, and bootstrap
receipt from the same trusted GitHub Release.
The release stays restricted/private until the owner separately chooses a
license and repository visibility. Do not install files from a mirror.

## Install

1. Verify the downloaded bootstrap against its `.sha256` receipt:

   ```powershell
   Get-FileHash .\Install-Nexus-<version>.ps1 -Algorithm SHA256
   ```

   Compare it with the first field in the matching receipt from that Release.
2. Run the bootstrap. It verifies the ZIP receipt, rejects unsafe archive paths,
   extracts once under `%LOCALAPPDATA%\Nexus\releases`, validates the embedded
   manifest, and configures Nexus:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\Install-Nexus-<version>.ps1 `
     -ArchivePath .\Nexus-<version>-windows.zip `
     -ChecksumPath .\Nexus-<version>-windows.zip.sha256 `
     -WorkspaceRoot C:\Work\MyProject
   ```

   `Bypass` affects only this PowerShell process; the installer requests no
   elevation. Restart ChatGPT Desktop and open a new conversation for the final
   human `@Nexus` visibility check.

The bootstrap uses the verified release-local runtime. It does not alter
`PATH`, install a system Python, use `py.exe`, rely on a Windows App Execution
Alias, modify another Python, or download packages. If `python` resolves to a
WindowsApps alias or another system interpreter, it is reported only as ignored
diagnostics; a missing or incompatible system interpreter is not a blocker.

Before Plugin activation, Nexus probes the requested Codex CLI without changing
its configuration. If the CLI is unavailable, cannot start, or has no Plugin
command, installation fails closed before any Nexus-local setup state is
written. Do not manually edit host configuration as a workaround. You may use
`-Mode standalone` only when `@Nexus` Plugin visibility is not required.

## Existing standalone MCP

If `nexus-r2-local` already exists, Plugin installation defaults to refusal to
avoid double registration. Keep it with `-Mode standalone`, or explicitly run
with `-MigrateStandalone`. The latter supports only a losslessly restorable
official CLI stdio configuration and restores it if activation fails.

## Maintenance

After extraction, use the printed release root:

```powershell
<release-root>\runtime\python\python.exe -I -B <release-root>\scripts\release_install.py verify
<release-root>\runtime\python\python.exe -I -B <release-root>\scripts\release_install.py upgrade --workspace-root C:\Work\MyProject --mode plugin
<release-root>\runtime\python\python.exe -I -B <release-root>\scripts\release_install.py rollback
<release-root>\runtime\python\python.exe -I -B <release-root>\scripts\release_install.py uninstall
```

Nexus never auto-downloads, auto-installs, or silently downgrades. Uninstall
retains Nexus-local backups and verified release files for rollback; it never
removes a workspace, another MCP server, or an unrelated system runtime. Close
active Plugin sessions before uninstalling because the host may hold plugin
files open. After uninstall and any required rollback have completed, a user
may remove the exact Nexus-owned release directory under `%LOCALAPPDATA%\Nexus\releases`.
