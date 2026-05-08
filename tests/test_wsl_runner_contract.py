from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_powershell_wsl_runner_points_to_bootstrap_and_artifacts():
    script = (ROOT / "venvwin-portable" / "run-wsl-flash-ready.ps1").read_text(encoding="utf-8")

    assert "venvWin Portable Windows WSL flash-ready runner" in script
    assert "bootstrap-flash-ready-ubuntu.sh" in script
    assert "dist\\venvwin-flash-ready-verdict.txt" in script
    assert "dist\\venvwin-portable-alpha-standard.iso" in script
    assert "status=FLASH_READY" in script
    assert "FLASH READY:" in script


def test_powershell_wsl_runner_converts_windows_path_to_wsl_path():
    script = (ROOT / "venvwin-portable" / "run-wsl-flash-ready.ps1").read_text(encoding="utf-8")

    assert "wsl.exe" in script
    assert "/mnt/$drive/$rest" in script
    assert "Resolve-Path" in script
    assert "Only normal Windows drive paths are supported" in script


def test_powershell_wsl_runner_refuses_non_flash_ready_verdict():
    script = (ROOT / "venvwin-portable" / "run-wsl-flash-ready.ps1").read_text(encoding="utf-8")

    assert "Build completed but verdict is not FLASH_READY. Do not flash." in script
    assert "Missing verdict file" in script
    assert "Missing ISO" in script
    assert "usb-flash-guide.md" in script


def test_preflight_requires_powershell_wsl_runner_contract():
    preflight = (ROOT / "venvwin-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    assert '"venvwin-portable/run-wsl-flash-ready.ps1"' in preflight
    assert "Checking PowerShell WSL runner contract" in preflight
    assert "bootstrap-flash-ready-ubuntu.sh" in preflight
    assert "status=FLASH_READY" in preflight
    assert "venvwin-portable-alpha-standard.iso" in preflight
    assert "venvwin-flash-ready-verdict.txt" in preflight
