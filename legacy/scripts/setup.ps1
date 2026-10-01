$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VirtualEnvironment = Join-Path $ProjectRoot ".venv"
$Python = Join-Path $VirtualEnvironment "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv $VirtualEnvironment
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -e "${ProjectRoot}[documents,web]"

Write-Host ""
Write-Host "Chat & Web is ready. Start the workbench with:"
Write-Host "  .venv\Scripts\python -m agenticrag serve"
