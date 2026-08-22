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
Write-Host 'Nexus installation completed. Restart ChatGPT Desktop before using @Nexus.'
