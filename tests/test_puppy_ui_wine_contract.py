"""Source checks for original dark-orange UI and modular Wine in native Puppy.

These checks DO NOT prove the code has executed in a Puppy guest.
"""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PUPPY = ROOT / "puppy-native"
BUILDER = (PUPPY / "build-puppy.sh").read_text()
SESSION = (PUPPY / "venvwin-session").read_text()
WINE = PUPPY / "venvwin-wine"
CONTROL = PUPPY / "venvwin-control-center"
CONTROL_TEXT = CONTROL.read_text()
THEME = (PUPPY / "venvwin-gtk.css").read_text()
GUI = (ROOT / "src/venvwin/gui_first_run.py").read_text()


def test_native_hooks_are_syntactically_valid():
    subprocess.run(["bash", "-n", str(PUPPY / "build-puppy.sh")], check=True)
    for file in (WINE, CONTROL, PUPPY / "venvwin-session", PUPPY / "venvwin-theme-apply"):
        subprocess.run(["sh", "-n", str(file)], check=True)


def test_real_ydrv_stages_recovered_gui_wine_and_puppy_startup():
    assert "venvwin-session" in BUILDER
    assert 'root/Startup/venvwin-session' in BUILDER
    assert 'usr/local/bin/venvwin-wine' in BUILDER
    assert 'venvwin-control-center' in BUILDER
    assert 'venvwin-gtk.css' in BUILDER
    assert 'usr/share/applications/venvwin-app.desktop' in BUILDER
    assert '-boot_image any replay -commit' in BUILDER
    assert 'ydrv_dpupbw64_10.0.12.sfs' in BUILDER


def test_premium_mint_style_is_recovered_not_reinvented():
    assert "#ff8a00" in THEME
    assert "#101216" in THEME
    assert "#ff8a00" in GUI
    assert '"Wine runner"' in GUI
    assert "Wine setup / status" in GUI
    assert "Adwaita:dark" in CONTROL_TEXT
    assert "tkinter" in CONTROL_TEXT
    assert "yad" in CONTROL_TEXT


def test_startup_avoids_automatic_wine_and_persistent_host_writes():
    assert "venvwin-wine --status" in SESSION
    assert "venvwin-wine --install" not in SESSION
    assert "wineboot" not in SESSION
    assert "apt-get" not in SESSION
    assert "venvwin-control-center" in SESSION
    assert "PYTHONPATH=" in SESSION
    assert "venvwin dashboard" in SESSION


def test_missing_wine_runner_fails_closed_with_real_status():
    env = dict(os.environ)
    env["PATH"] = "/this-dir-does-not-exist"
    result = subprocess.run(["/bin/sh", str(WINE), "--status"], text=True,
                            capture_output=True, env=env, timeout=10)
    assert result.returncode == 70
    assert "WINE_RUNNER_MISSING" in result.stdout


def test_installer_never_mutates_without_explicit_native_tool_and_consent():
    env = dict(os.environ)
    env["PATH"] = "/this-dir-does-not-exist"
    result = subprocess.run(["/bin/sh", str(WINE), "--install"], text=True,
                            capture_output=True, env=env, timeout=10)
    assert result.returncode == 69
    assert "WINE_INSTALL_UNAVAILABLE" in result.stderr


def test_unverified_optional_wine_sfs_is_not_silently_mounted():
    result = subprocess.run(["/bin/sh", str(WINE), "--load-sfs",
                             "/not-a-real-module.sfs"], text=True,
                            capture_output=True, timeout=10)
    assert result.returncode == 66
    assert "WINE_SFS_MISSING" in result.stderr


def test_native_readiness_is_still_unproven():
    evidence = (ROOT / "src/venvwin/puppy_evidence.py").read_text()
    assert '"runtime_overlay": _check(' in evidence
    assert '"persistence_reboot": _check(' in evidence
    assert "no independently imported actual guest mount report" in evidence
    docs = (PUPPY / "WINE-AND-UI-INTEGRATION.md").read_text()
    assert "Not a verified product" in docs
