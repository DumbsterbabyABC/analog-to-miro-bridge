param(
    [string]$Port = "COM7",
    [switch]$NoRun
)

$ErrorActionPreference = "Stop"

$requiredFiles = @(
    "config.py",
    "wifi_utils.py",
    "matrix_scanner.py",
    "miro_sync.py",
    "pcf8575.py",
    "pcf_link_scanner.py",
    "main.py"
)

Write-Host "Deploy to ESP32 on $Port"

# Always run from the script directory so relative file paths are stable.
Set-Location -Path $PSScriptRoot



foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        throw "Missing file: $file"
    }
}

Write-Host "Copy files -> :/"
$copyArgs = @("connect", $Port, "fs", "cp")
$copyArgs += $requiredFiles
$copyArgs += ":/"
python -m mpremote @copyArgs

if (-not $NoRun) {
    Write-Host "Run main.py"
    python -m mpremote connect $Port run main.py
} else {
    Write-Host "Upload finished. Skipping run because -NoRun was set."
}

Write-Host "Done."
