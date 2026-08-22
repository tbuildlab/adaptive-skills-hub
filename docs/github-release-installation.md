# Install Nexus from a GitHub Release (Windows RC)

## Prerequisites

This path needs no repository clone, `D:` drive, administrator rights, API key,
OAuth, or remote MCP. You need Windows, Python 3.10+, one real non-root
workspace directory, and (for Plugin mode) a compatible Codex/ChatGPT Desktop
host. Download the ZIP, ZIP receipt, PowerShell bootstrap, and bootstrap
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

## Existing standalone MCP

If `nexus-r2-local` already exists, Plugin installation defaults to refusal to
avoid double registration. Keep it with `-Mode standalone`, or explicitly run
with `-MigrateStandalone`. The latter supports only a losslessly restorable
official CLI stdio configuration and restores it if activation fails.

## Maintenance

After extraction, use the printed release root:

```powershell
python <release-root>\scripts\release_install.py verify
python <release-root>\scripts\release_install.py upgrade --workspace-root C:\Work\MyProject --mode plugin
python <release-root>\scripts\release_install.py rollback
python <release-root>\scripts\release_install.py uninstall --remove-runtime
```

Nexus never auto-downloads, auto-installs, or silently downgrades. Uninstall
retains Nexus-local backups and never removes a workspace, another MCP server,
or downloaded release files. Close active Plugin sessions before uninstalling
because the host may hold plugin files open.
