# Quick smoke test for the Ignition UI (Python server): start server, GET /api/components, GET /api/status, POST /api/command, stop server.
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path $PSScriptRoot -Parent
$uiScript = Join-Path $PSScriptRoot 'Start-IgnitionUI.ps1'
$job = Start-Job -ScriptBlock {
    param($script, $root)
    & $script -RepoRoot $root
} -ArgumentList $uiScript, $RepoRoot
Start-Sleep -Seconds 5
$getComponentsOk = $false
$getStatusOk = $false
$postOk = $false
try {
    $r = Invoke-WebRequest -Uri 'http://localhost:9080/api/components' -UseBasicParsing
    $getComponentsOk = ($r.StatusCode -eq 200)
    Write-Host "GET /api/components: $($r.StatusCode)"
} catch { Write-Host "GET /api/components error: $($_.Exception.Message)" }
try {
    $r2 = Invoke-WebRequest -Uri 'http://localhost:9080/api/status' -UseBasicParsing
    $getStatusOk = ($r2.StatusCode -eq 200)
    Write-Host "GET /api/status: $($r2.StatusCode)"
} catch { Write-Host "GET /api/status error: $($_.Exception.Message)" }
try {
    $body = '{ "command":"Status" }'
    $r3 = Invoke-WebRequest -Uri 'http://localhost:9080/api/command' -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
    $postOk = ($r3.StatusCode -eq 200)
    Write-Host "POST /api/command Status: $($r3.StatusCode)"
} catch { Write-Host "POST /api/command error: $($_.Exception.Message)" }
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue
$allOk = $getComponentsOk -and $getStatusOk -and $postOk
if ($allOk) { Write-Host "UI smoke test: PASS" } else { Write-Host "UI smoke test: FAIL (components=$getComponentsOk status=$getStatusOk command=$postOk)" }
