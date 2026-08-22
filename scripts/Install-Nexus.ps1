[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ArchivePath,
    [Parameter(Mandatory = $true)][string]$ChecksumPath,
    [Parameter(Mandatory = $true)][string]$WorkspaceRoot,
    [ValidateSet('plugin', 'standalone')][string]$Mode = 'plugin',
    [switch]$MigrateStandalone,
    [string]$RuntimePython,
    [string]$DataRoot,
    [string]$CodexCommand = 'codex'
)

$ErrorActionPreference = 'Stop'
function Fail([string]$Message) { throw "Nexus installation failed: $Message" }
if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) { Fail 'archive was not found' }
if (-not (Test-Path -LiteralPath $ChecksumPath -PathType Leaf)) { Fail 'checksum receipt was not found' }
$expected = ((Get-Content -LiteralPath $ChecksumPath -Raw).Trim() -split '\s+')[0]
if ($expected -notmatch '^[a-fA-F0-9]{64}$') { Fail 'checksum receipt is invalid' }
$actual = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected.ToLowerInvariant()) { Fail 'archive checksum mismatch' }

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
    $base = if ($DataRoot) { Join-Path $DataRoot 'releases' } elseif ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA 'Nexus\releases' } else { Join-Path $HOME '.nexus\releases' }
    $target = Join-Path $base $top
    if (Test-Path -LiteralPath $target) { Fail 'this release is already extracted; use release_install.py upgrade or rollback' }
    New-Item -ItemType Directory -Force -Path $base | Out-Null
    foreach ($entry in $archive.Entries) {
        if ([string]::IsNullOrEmpty($entry.Name)) { continue }
        $relative = $entry.FullName.Replace('/', [IO.Path]::DirectorySeparatorChar)
        $output = Join-Path $base $relative
        $parent = Split-Path -Parent $output
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        $input = $entry.Open(); try { $stream = [IO.File]::Open($output, [IO.FileMode]::CreateNew); try { $input.CopyTo($stream) } finally { $stream.Dispose() } } finally { $input.Dispose() }
    }
} finally { $archive.Dispose() }

$python = if ($RuntimePython) { $RuntimePython } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } elseif (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { Fail 'Python 3.10+ is required' }
$arguments = @((Join-Path $target 'scripts\release_install.py'))
if ($python -eq 'py') { $arguments = @('-3') + $arguments }
if ($DataRoot) { $arguments += @('--data-root', $DataRoot) }
$arguments += @('--codex-command', $CodexCommand, 'install', '--workspace-root', $WorkspaceRoot, '--mode', $Mode)
if ($RuntimePython) { $arguments += @('--runtime-python', $RuntimePython) }
if ($MigrateStandalone) { $arguments += '--migrate-standalone' }
& $python @arguments
if ($LASTEXITCODE -ne 0) { Fail 'release configuration failed; extracted files remain verified for inspection' }
Write-Host 'Nexus installation completed. Restart ChatGPT Desktop before using @Nexus.'
