#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"
$root = Split-Path -Parent $PSScriptRoot
$py = "C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

function Invoke-Checked {
    param([string]$Label, [string[]]$Arguments)
    Write-Host "== $Label =="
    & $py @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] $Label (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "[PASS] $Label" -ForegroundColor Green
}

Push-Location $root
try {
    Invoke-Checked "unit tests" @("scripts\test_experiment_stats.py")
    Invoke-Checked "canonical case replay" @("scripts\reproduce_examples.py")
    Invoke-Checked "document checks" @("scripts\check_docs.py")
    Write-Host "`nAll checks passed." -ForegroundColor Green
}
finally {
    Pop-Location
}
