# Install Nexus 0.1.1 from a private GitHub Release (Windows x64)

Use the [stable Nexus 0.1.1 release](https://github.com/tbuildlab/adaptive-skills-hub/releases/tag/nexus-0.1.1).
Its source is the accepted plugin patch commit
`a8dbcc7c10177f20955ed7cce78b6609e663d1aa`; its immutable assets are not rebuilt
for later README or repository-catalog cleanup on `main`.

## Prerequisites

This path needs no repository clone, `D:` drive, administrator rights, API key,
OAuth, remote MCP, Microsoft Store, `py.exe`, preinstalled Python, Codex CLI,
Node, or npm. The `0.1.1` Windows ZIP
contains a pinned, Nexus-owned CPython 3.13.15 x64 runtime and the reviewed R2
dependencies. You need supported 64-bit Windows and one real non-root
workspace directory. The installer registers a Nexus-owned source in the
documented per-user personal marketplace at
`~/.agents/plugins/marketplace.json`; it never edits `~/.codex/config.toml`.
Download the ZIP, ZIP receipt, PowerShell bootstrap, and bootstrap receipt from
the same trusted GitHub Release.
The repository/release is private and proprietary. Recipients need their own
authorized GitHub repository access; a link does not grant access. Repository
visibility and licensing are unchanged. Do not install files from a mirror.

## Exact release downloads

Sign in to GitHub and download these six assets into one folder:

| Asset | Purpose |
| --- | --- |
| [Nexus-0.1.1-windows.zip](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Nexus-0.1.1-windows.zip) | Complete Windows release, including the owned runtime. |
| [ZIP checksum](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Nexus-0.1.1-windows.zip.sha256) | ZIP SHA-256 receipt. |
| [Install-Nexus-0.1.1.ps1](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Install-Nexus-0.1.1.ps1) | Verified bootstrap. |
| [Bootstrap checksum](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Install-Nexus-0.1.1.ps1.sha256) | Bootstrap SHA-256 receipt. |
| [Release manifest](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Nexus-0.1.1.release-manifest.json) | Exact release member sizes and hashes. |
| [Manifest checksum](https://github.com/tbuildlab/adaptive-skills-hub/releases/download/nexus-0.1.1/Nexus-0.1.1.release-manifest.json.sha256) | Manifest SHA-256 receipt. |

The ZIP SHA-256 is
`6b6b8f8f2ee8949557dd09ac2bffe14e0401c99aa2d2bafb9402f6f90d2f745a`.
Do not use GitHub's generated **Source code** ZIP/TAR as the installer: it has
no release-owned runtime or extracted `release-manifest.json`.

Alternatively, with GitHub CLI installed and already authenticated as an
authorized user:

```powershell
gh release download nexus-0.1.1 --repo tbuildlab/adaptive-skills-hub --dir .\Nexus-0.1.1-download
Set-Location .\Nexus-0.1.1-download
```

No credentials should be pasted into commands or shared with another user.

## Install

1. Verify the downloaded bootstrap against its `.sha256` receipt:

   ```powershell
   $expectedBootstrap = '37d82101a917030e6441abb8e711c57f6bbaa83779561fa2b4997a080d98608f'
   if ((Get-FileHash .\Install-Nexus-0.1.1.ps1 -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedBootstrap) {
     throw 'Nexus bootstrap checksum mismatch'
   }
   ```

   Compare it with the first field in the matching receipt from that Release.
2. Run the bootstrap. It verifies the ZIP receipt, rejects unsafe archive paths,
   extracts once under `%LOCALAPPDATA%\Nexus\releases`, validates the embedded
   manifest, and configures Nexus:

   ```powershell
   $projectRoot = Join-Path $env:USERPROFILE 'NexusProjects\MyProject'
   New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Nexus-0.1.1.ps1 `
     -ArchivePath .\Nexus-0.1.1-windows.zip `
     -ChecksumPath .\Nexus-0.1.1-windows.zip.sha256 `
     -WorkspaceRoot $projectRoot -Mode plugin
   ```

   `Bypass` affects only this PowerShell process; the installer requests no
   elevation.
3. The installer has prepared a **source**, not an installed Desktop Plugin.
   Complete the required host-managed action:

   ```text
   ChatGPT Desktop → Plugins → Personal → Nexus → + Install
   ```

4. Start a new ChatGPT Desktop conversation and type `@`; then select Nexus.

The bootstrap uses the verified release-local runtime. It does not alter
`PATH`, install a system Python, use `py.exe`, rely on a Windows App Execution
Alias, modify another Python, or download packages. If `python` resolves to a
WindowsApps alias or another system interpreter, it is reported only as ignored
diagnostics; a missing or incompatible system interpreter is not a blocker.

The installer copies the Plugin source to the documented personal location
`~/.codex/plugins/nexus-desktop` and registers it as
`./.codex/plugins/nexus-desktop` with policy `AVAILABLE`. The installer does
not treat marketplace discovery as proof that the `@` selector can load Nexus.
Desktop owns the actual plugin installation. After it has installed Nexus,
start a fresh conversation and type `@`. If Nexus is absent, report an exposure
failure; do not infer success from the source card or edit host files.

### Optional Codex CLI registration

On a local Codex installation whose `codex plugin --help` exposes `marketplace`,
`add`, and `list`, the supported CLI can perform the host-managed registration
after the verified release installer has prepared the personal source:

```powershell
codex plugin marketplace add "$env:USERPROFILE"
codex plugin add nexus-desktop@personal-marketplace
codex plugin list --json
```

If `personal-marketplace` already appears in `codex plugin marketplace list`,
skip the first command. Expect exactly one enabled installed Nexus record,
version `0.1.1`, ID `nexus-desktop@personal-marketplace`. The host manages its
cache; never manually copy, edit or delete cache files. Start a new conversation
after installation so its Skill and tools refresh.

The cloned repository catalog is a distinct developer path. On current `main`
its `nexus-local-pilot` catalog points to `./plugins/nexus-desktop` relative to
the checkout. It does not replace the generated personal catalog above. Do not
install both copies or create a standalone MCP with the same tool names.

## First use and truthful outcomes

Try `Use Nexus to plan a new editable PowerPoint presentation project.`
`nexus.plan_task` returns the `reference_research` object in `0.1.1`.
Substantial projects use bounded research; exact specs use reduced/targeted
research; tiny edits and explicit opt-out skip it. No suitable reference means
Nexus-original in-scope design and Host-owned PLAN → BUILD → TEST → VERIFY.

A real capability gap remains `fallback_needed / CAPABILITY_NOT_COVERED`.
Material scope/security/permission conflicts retain `HOLD_owner_decision` and
must not be promoted into a successful plan. A planning response is not artifact
execution or verification evidence. See [the current scope](../README.md#supported-scope).

## Existing standalone MCP

Plugin mode never registers `nexus-r2-local`; its bundled `.mcp.json` owns the
single Plugin MCP definition and launches it with the verified release-owned
embedded Python executable. Existing standalone R3 is a separate developer
mode. The Marketplace installer intentionally does not inspect or rewrite
Codex/ChatGPT host configuration to migrate it.

## Maintenance

After extraction, use the printed release root:

```powershell
$releaseRoot = Join-Path $env:LOCALAPPDATA 'Nexus\releases\Nexus-0.1.1'
$projectRoot = Join-Path $env:USERPROFILE 'NexusProjects\MyProject'
& "$releaseRoot\runtime\python\python.exe" -I -B "$releaseRoot\scripts\release_install.py" verify
if ($LASTEXITCODE -ne 0) { throw 'Nexus release verification failed' }
& "$releaseRoot\runtime\python\python.exe" -I -B "$releaseRoot\scripts\release_install.py" upgrade --workspace-root $projectRoot --mode plugin
```

For a previously extracted `0.1.1`, use `verify` and `upgrade` above rather than
extracting over it. For a new version, download its own versioned assets first.
Complete the Desktop/CLI refresh afterward. Never replace an old release's bytes
or change a frozen tag to reuse a version. To intentionally roll back or uninstall,
close active Nexus sessions, use Desktop's uninstall control, then invoke the
same verified installer's `rollback` or `uninstall` subcommand as appropriate.

Nexus never auto-downloads, auto-installs, or silently downgrades. Uninstall
retains Nexus-local backups and verified release files for rollback; it never
removes a workspace, another MCP server, or an unrelated system runtime. Close
active Plugin sessions before uninstalling because the host may hold plugin
files open. If Desktop has already installed the Plugin, use its documented
**Uninstall plugin** control first; the release installer then removes only the
Nexus Marketplace source, Nexus launch configuration, and Nexus-owned runtime
state. It never removes an unrelated Plugin, Skill, workspace, or Desktop
configuration. After uninstall and any required rollback have completed, a
user may remove the exact Nexus-owned release directory under
`%LOCALAPPDATA%\Nexus\releases`.
