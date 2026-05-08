param(
    [string]$RepoPath = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

Write-Host "== venvWin Portable Windows WSL flash-ready runner =="
Write-Host "Repo path: $RepoPath"

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "wsl.exe not found. Install WSL Ubuntu first."
}

if (-not (Test-Path $RepoPath)) {
    throw "Repo path does not exist: $RepoPath"
}

$resolved = (Resolve-Path $RepoPath).Path

if ($resolved -match '^([A-Za-z]):\\(.*)$') {
    $drive = $matches[1].ToLowerInvariant()
    $rest = $matches[2] -replace '\\', '/'
    $wslPath = "/mnt/$drive/$rest"
} else {
    throw "Only normal Windows drive paths are supported, like C:\\Users\\Daniel\\venvWin"
}

Write-Host "WSL path: $wslPath"
Write-Host "Running bootstrap. This may ask for your Ubuntu sudo password."

$cmd = "cd '$wslPath' && chmod +x venvwin-portable/bootstrap-flash-ready-ubuntu.sh && ./venvwin-portable/bootstrap-flash-ready-ubuntu.sh"
wsl.exe bash -lc $cmd

if ($LASTEXITCODE -ne 0) {
    throw "WSL flash-ready build failed with exit code $LASTEXITCODE"
}

$verdictPath = Join-Path $resolved "dist\venvwin-flash-ready-verdict.txt"
$isoPath = Join-Path $resolved "dist\venvwin-portable-alpha-standard.iso"

if (-not (Test-Path $verdictPath)) {
    throw "Missing verdict file: $verdictPath"
}

$verdict = Get-Content $verdictPath -Raw
Write-Host "== Verdict =="
Write-Host $verdict

if ($verdict -notmatch "status=FLASH_READY") {
    throw "Build completed but verdict is not FLASH_READY. Do not flash."
}

if (-not (Test-Path $isoPath)) {
    throw "Missing ISO: $isoPath"
}

Write-Host "FLASH READY: $isoPath"
Write-Host "Next: use venvwin-portable/usb-flash-guide.md before writing any USB drive."
