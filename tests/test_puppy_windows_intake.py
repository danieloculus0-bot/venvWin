"""End-to-end intake semantics: EXE/MSI, Wine prefixes, shortcuts and failures.

Fake Wine covers routing only. Separate CI executes genuine PE binaries under Wine.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from venvwin.capsule import create_capsule
from venvwin.intake import discover_application_exes, create_application_shortcut
from venvwin.profile import RunnerProfile


def _cli(env, *args):
    return subprocess.run([sys.executable, "-m", "venvwin.cli", *args],
                          text=True, capture_output=True, env=env, timeout=20)


def _fake_wine(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "wine"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib,os,sys\n"
        "prefix=pathlib.Path(os.environ['WINEPREFIX'])\n"
        "app=prefix/'drive_c'/'Program Files'/'venvWin Demo'/'Demo.exe'\n"
        "if any('broken' in x.lower() for x in sys.argv[1:]): sys.exit(27)\n"
        "if any('empty' in x.lower() for x in sys.argv[1:]): sys.exit(0)\n"
        "if any(x.lower().endswith(('.msi','setup.exe')) for x in sys.argv[1:]):\n"
        "    app.parent.mkdir(parents=True,exist_ok=True);app.write_bytes(b'MZ real target stub')\n"
        "else: (prefix/'app-executed.txt').write_text('executed')\n"
        "sys.exit(0)\n"
    )
    fake.chmod(0o755)
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    env = os.environ.copy()
    env["PATH"] = str(bindir) + os.pathsep + os.environ.get("PATH", "")
    env["VENVWIN_HOME"] = str(tmp_path / "runtime")
    env["VENVWIN_DESKTOP_DIR"] = str(desktop)
    return env, desktop


def test_msi_in_installed_exe_out_and_shortcut_relaunch(tmp_path):
    env, desktop = _fake_wine(tmp_path)
    assert _cli(env, "init").returncode == 0
    installer = tmp_path / "Widget.msi"
    installer.write_bytes(b"MSI test fixture")
    first = _cli(env, "open", str(installer))
    assert first.returncode == 0, first.stderr
    result = json.loads(first.stdout)
    assert result["status"] == "installed_shortcut_created_not_yet_launched"
    assert len(result["launch_targets"]) == 1
    path = Path(result["desktop_shortcut"])
    assert path.parent == desktop and path.is_file()
    assert ' run "widget" ' in path.read_text()
    run = _cli(env, "run", "widget", result["launch_targets"][0])
    assert run.returncode == 0, run.stderr
    report = json.loads(run.stdout)
    assert report["status"] == "windows_binary_executed"
    assert (Path(report["env"]["WINEPREFIX"]) / "app-executed.txt").read_text() == "executed"


def test_failed_exe_installer_cannot_claim_app_ready(tmp_path):
    env, desktop = _fake_wine(tmp_path)
    _cli(env, "init")
    broken = tmp_path / "broken-setup.exe"
    broken.write_bytes(b"MZ bad")
    result = _cli(env, "open", str(broken))
    assert result.returncode == 27
    data = json.loads(result.stdout)
    assert data["status"] == "installer_failed"
    assert not list(desktop.glob("*.desktop"))


def test_msi_installer_without_target_is_not_falsely_ready(tmp_path):
    env, desktop = _fake_wine(tmp_path)
    assert _cli(env, "init").returncode == 0
    sample = tmp_path / "Empty.msi"
    sample.write_bytes(b"MSI")
    run = _cli(env, "open", str(sample))
    assert run.returncode == 0, run.stderr
    data = json.loads(run.stdout)
    assert data["status"] == "installer_succeeded_no_application_target_found"
    assert data["launch_targets"] == []
    assert not list(desktop.glob("*.desktop"))


def test_desktop_paths_with_spaces_and_percent_are_escaped(tmp_path):
    root = tmp_path / "capsules"
    capsule = create_capsule(root, "Test 100% Win App", RunnerProfile.default())
    exe = tmp_path / "My Apps" / 'Demo 100%.exe'
    exe.parent.mkdir()
    exe.write_bytes(b"MZ")
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    launcher = create_application_shortcut(root, capsule, exe, desktop)
    text = launcher.read_text()
    assert "100%%" in text.split("Exec=", 1)[1]
    assert '"test-100%%-win-app"' not in text
    assert str(exe).replace("%", "%%") in text
    assert 'run ' in text


def test_wine_builtin_windows_apps_are_not_installer_targets(tmp_path):
    prefix = tmp_path / "prefix"
    builtin = prefix / "drive_c" / "Program Files"
    for folder, name in [
        ("Internet Explorer", "iexplore.exe"),
        ("Windows Media Player", "wmplayer.exe"),
        ("Windows NT/Accessories", "wordpad.exe"),
    ]:
        destination = builtin / folder / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"MZ wine stub")
    actual = builtin / "venvWin Demo" / "Demo.exe"
    actual.parent.mkdir()
    actual.write_bytes(b"MZ installed")
    assert discover_application_exes(str(prefix)) == [actual]
