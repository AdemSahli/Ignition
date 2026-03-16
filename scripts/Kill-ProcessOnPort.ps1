<#
.SYNOPSIS
    Kill the process listening on a given TCP port (Windows).

.DESCRIPTION
    Uses netstat -ano to find the PID bound to -Port, then runs taskkill /F /PID.
    Run from any directory. Pass one or more port numbers.

.PARAMETER Port
    TCP port number (e.g. 8080 for Spring Boot, 4200 for Angular dev server).
#>
param(
    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $false)]
    [int[]]$Port
)

foreach ($p in $Port) {
    # netstat -ano: last column is PID; match lines with :<port> and LISTENING
    $lines = netstat -ano 2>$null | Select-String ":$p\s" | Select-String "LISTENING"
    $pids = @()
    foreach ($line in $lines) {
        $parts = ($line.Line -split '\s+')
        $last = $parts[-1]
        if ($last -match '^\d+$') { $pids += [int]$last }
    }
    $pids = $pids | Sort-Object -Unique
    if ($pids.Count -eq 0) {
        Write-Host "No process found listening on port $p."
        continue
    }
    foreach ($procId in $pids) {
        Write-Host "Killing PID $procId (port $p)..."
        & taskkill /F /PID $procId 2>$null
        if ($LASTEXITCODE -eq 0) { Write-Host "  Done." } else { Write-Host "  Failed (try running as Administrator)." }
    }
}
