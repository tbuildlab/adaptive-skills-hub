[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ArchivePath,
    [Parameter(Mandatory = $true)][string]$ChecksumPath,
    [Parameter(Mandatory = $true)][string]$WorkspaceRoot,
    [ValidateSet('plugin', 'standalone')][string]$Mode = 'plugin',
    [switch]$MigrateStandalone,
    [string]$DataRoot
)

$ErrorActionPreference = 'Stop'
# PowerShell 5.1 otherwise serializes redirected non-ASCII output through the
# active legacy code page.  Pin UTF-8 so release automation and users receive
# the exact host-managed installation instruction on every Windows locale.
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$NexusArrow = [char]0x2192
function Fail([string]$Message) { throw "Nexus installation failed: $Message" }
function ExtendedPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if ($full.StartsWith('\\?\')) { return $full }
    if ($full.StartsWith('\\')) { return ('\\?\UNC\' + $full.TrimStart('\')) }
    return ('\\?\' + $full)
}
if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) { Fail 'archive was not found' }
if (-not (Test-Path -LiteralPath $ChecksumPath -PathType Leaf)) { Fail 'checksum receipt was not found' }
$expected = ((Get-Content -LiteralPath $ChecksumPath -Raw).Trim() -split '\s+')[0]
if ($expected -notmatch '^[a-fA-F0-9]{64}$') { Fail 'checksum receipt is invalid' }
$actual = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected.ToLowerInvariant()) { Fail 'archive checksum mismatch' }

# Read-only bootstrap equivalent of setup_nexus.prepare_workspace_registration.
# The bootstrap always registers nexus-default; Python repeats the check before
# configuration writes. Resolve directory handles so junctions and case/path
# spelling compare like pathlib.resolve(), without requiring system Python.
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class NexusWorkspacePath {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFile(string path, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(SafeFileHandle handle, StringBuilder path, uint size, uint flags);
    public static string Resolve(string path) {
        using (var handle = CreateFile(path, 0, 7, IntPtr.Zero, 3, 0x02000000, IntPtr.Zero)) {
            if (handle.IsInvalid) throw new System.ComponentModel.Win32Exception();
            var buffer = new StringBuilder(32768);
            uint length = GetFinalPathNameByHandle(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0 || length >= buffer.Capacity) throw new System.ComponentModel.Win32Exception();
            return buffer.ToString().TrimEnd('\\');
        }
    }
}
'@
function WorkspaceDirectory([string]$Value) {
    if ($Value -eq '~' -or $Value.StartsWith('~\') -or $Value.StartsWith('~/')) {
        $Value = $HOME + $Value.Substring(1)
    }
    if ($Value -notmatch '^(?:[A-Za-z]:[\\/]|\\\\)') { Fail 'workspace root must be an absolute non-root directory' }
    $full = [IO.Path]::GetFullPath($Value)
    if ($full.TrimEnd('\', '/') -eq [IO.Path]::GetPathRoot($full).TrimEnd('\', '/')) { Fail 'workspace root must be an absolute non-root directory' }
    if (-not (Test-Path -LiteralPath $full -PathType Container)) { Fail 'workspace root must be an existing directory' }
    return [NexusWorkspacePath]::Resolve((ExtendedPath $full))
}
$workspacePath = WorkspaceDirectory $WorkspaceRoot
$local = if ($DataRoot) { $DataRoot } elseif ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA 'Nexus' } else { Join-Path $HOME '.nexus' }
if ($local -eq '~' -or $local.StartsWith('~\') -or $local.StartsWith('~/')) { $local = $HOME + $local.Substring(1) }
$local = [IO.Path]::GetFullPath($local)
$workspaceConfig = Join-Path $local 'workspaces.json'
if (Test-Path -LiteralPath $workspaceConfig) {
    $config = Get-Content -LiteralPath $workspaceConfig -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config -isnot [System.Management.Automation.PSCustomObject] -or $config.PSObject.Properties.Name -cnotcontains 'schema_version' -or $config.PSObject.Properties.Name -cnotcontains 'workspaces' -or $config.schema_version -cne 'nexus.mcp.workspace.v1' -or $config.workspaces -isnot [System.Management.Automation.PSCustomObject]) { Fail 'existing workspace configuration is invalid' }
    # JSON IDs, unlike PowerShell property lookup, are case-sensitive.
    $registration = @($config.workspaces.PSObject.Properties | Where-Object { $_.Name -ceq 'nexus-default' })
    if ($registration.Count -gt 0) {
        $existing = $registration[0].Value
        if ($existing -isnot [System.Management.Automation.PSCustomObject] -or $existing.PSObject.Properties.Name -cnotcontains 'root' -or $existing.root -isnot [string]) { Fail 'existing workspace registration is invalid' }
        if (-not [StringComparer]::OrdinalIgnoreCase.Equals((WorkspaceDirectory $existing.root), $workspacePath)) { Fail 'workspace ID already belongs to a different root; existing mapping preserved' }
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $ArchivePath))
try {
    $roots = @{}
    foreach ($entry in $archive.Entries) {
        $name = $entry.FullName.Replace('\', '/')
        if ($name -match '(^/|^[A-Za-z]:|(^|/)\.\.(/|$))') { Fail 'archive has an unsafe path' }
        if ((([int64]$entry.ExternalAttributes -shr 16) -band 0xF000) -eq 0xA000) { Fail 'archive has a symbolic-link entry' }
        $parts = $name.Split('/', [System.StringSplitOptions]::RemoveEmptyEntries)
        if ($parts.Length -lt 2) { Fail 'archive must have one top-level directory' }
        $roots[$parts[0]] = $true
    }
    if ($roots.Count -ne 1) { Fail 'archive must have exactly one top-level directory' }
    $top = @($roots.Keys)[0]
    $base = Join-Path $local 'releases'
    $target = Join-Path $base $top
    if (Test-Path -LiteralPath $target) { Fail 'this release is already extracted; use release_install.py upgrade or rollback' }
    [IO.Directory]::CreateDirectory((ExtendedPath $base)) | Out-Null
    foreach ($entry in $archive.Entries) {
        if ([string]::IsNullOrEmpty($entry.Name)) { continue }
        $relative = $entry.FullName.Replace('/', [IO.Path]::DirectorySeparatorChar)
        $output = Join-Path $base $relative
        $parent = Split-Path -Parent $output
        [IO.Directory]::CreateDirectory((ExtendedPath $parent)) | Out-Null
        $input = $entry.Open(); try { $stream = [IO.File]::Open((ExtendedPath $output), [IO.FileMode]::CreateNew); try { $input.CopyTo($stream) } finally { $stream.Dispose() } } finally { $input.Dispose() }
    }
} finally { $archive.Dispose() }

$python = Join-Path $target 'runtime\python\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { Fail 'release-owned embedded Python runtime is unavailable' }
$runtimeProbe = & $python -I -B -c "import mcp, sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"
if ($LASTEXITCODE -ne 0) { Fail 'release-owned embedded Python runtime is incompatible' }
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -match 'WindowsApps') {
    Write-Host 'Detected a Windows App Execution Alias placeholder; it is ignored.'
} elseif ($pythonCommand) {
    Write-Host 'Detected a system Python command; it is ignored in favor of the Nexus-owned runtime.'
} else {
    Write-Host 'No usable system Python command detected; using the Nexus-owned runtime.'
}
$arguments = @((Join-Path $target 'scripts\release_install.py'))
if ($DataRoot) { $arguments += @('--data-root', $DataRoot) }
$arguments += @('install', '--workspace-root', $WorkspaceRoot, '--mode', $Mode)
if ($MigrateStandalone) { $arguments += '--migrate-standalone' }
& $python @arguments
if ($LASTEXITCODE -ne 0) { Fail 'release configuration failed; extracted files remain verified for inspection' }
if ($Mode -eq 'plugin') {
    Write-Host ("Nexus personal marketplace source is ready. Required action: ChatGPT Desktop {0} Plugins {0} Personal {0} Nexus {0} + Install" -f $NexusArrow)
    Write-Host 'After ChatGPT Desktop installs the Plugin, start a new chat and use @Nexus.'
} else {
    Write-Host 'Nexus standalone installation completed.'
}
