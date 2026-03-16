<#
.SYNOPSIS
    Ignition CLI launcher: delegates to Python (Status, Up, Down, Generate-Config).
.DESCRIPTION
    Runs: python -m ignition.cli <command> [options]. Repo root: -RepoRoot or $env:IGNITION_REPO.
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Up', 'Down', 'Generate-Config', 'Status')]
    [string]$Command,
    [switch]$All,
    [string]$ComponentId,
    [string]$RepoRoot,
    [switch]$ShowModuleConsole,
    [switch]$LogModuleToFile,
    [ValidateSet('Table', 'Json')]
    [string]$OutputFormat = 'Table'
)
$ErrorActionPreference = 'Stop'
if (-not $RepoRoot) { $RepoRoot = if ($env:IGNITION_REPO) { $env:IGNITION_REPO } else { (Get-Location).Path } }
$RepoRoot = (Resolve-Path -Path $RepoRoot -ErrorAction SilentlyContinue).Path
if (-not $RepoRoot) { throw "Repo root not resolved. Set -RepoRoot or `$env:IGNITION_REPO." }
$pythonCmd = $null
try { $null = & py -3 -c "exit(0)" 2>$null; if ($LASTEXITCODE -eq 0) { $pythonCmd = @('py', '-3') } } catch {}
if (-not $pythonCmd) { try { $null = & python -c "exit(0)" 2>$null; if ($LASTEXITCODE -eq 0) { $pythonCmd = @('python') } } catch {} }
if (-not $pythonCmd) { try { $null = & python3 -c "exit(0)" 2>$null; if ($LASTEXITCODE -eq 0) { $pythonCmd = @('python3') } } catch {} }
if (-not $pythonCmd) { throw "Python 3 not found." }
$cliCommand = switch -Regex ($Command) { '^Status$' { 'status' } '^Up$' { 'up' } '^Down$' { 'down' } '^Generate-Config$' { 'generate-config' } default { ($Command -replace '\s', '-').ToLowerInvariant() } }
$args = @('--repo-root', $RepoRoot, $cliCommand)
if ($ComponentId) { $args += '--component-id', $ComponentId }
if ($All -and $Command -in 'Up','Down') { $args += '--all' }
if ($ShowModuleConsole -and $Command -eq 'Up') { $args += '--show-module-console' }
if ($LogModuleToFile -and $Command -eq 'Up') { $args += '--log-module-to-file' }
if ($Command -eq 'Status' -and $OutputFormat -eq 'Json') { $args += '--output', 'json' }
Push-Location $RepoRoot
try { & $pythonCmd[0] @($pythonCmd[1..($pythonCmd.Length-1)] + '-m', 'ignition.cli') @args; exit $LASTEXITCODE } finally { Pop-Location }
