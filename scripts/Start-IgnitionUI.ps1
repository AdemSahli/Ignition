<#
.SYNOPSIS
    Start the Ignition web UI (Python FastAPI server).
.DESCRIPTION
    Launches python -m ignition.server. Requires -RepoRoot (or parent of scripts = repo root).
#>
param([string]$RepoRoot = '', [int]$Port = 9080)
$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
if (-not $RepoRoot) { $RepoRoot = (Split-Path $ScriptDir -Parent) }
$RepoRoot = (Resolve-Path -Path $RepoRoot -ErrorAction SilentlyContinue).Path
if (-not $RepoRoot) { $RepoRoot = (Split-Path $ScriptDir -Parent) }
if (-not (Test-Path -Path (Join-Path $RepoRoot 'ignition') -PathType Container)) {
    Write-Error "ignition package not found under $RepoRoot. Pass -RepoRoot to the folder that contains ignition and scripts."
    exit 1
}
$env:PYTHONPATH = $RepoRoot
Push-Location $RepoRoot
try { & python -m ignition.server --repo-root $RepoRoot --port $Port; exit $LASTEXITCODE } finally { Pop-Location }
