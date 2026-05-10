from __future__ import annotations

from pathlib import Path

from venvwin.open import classify_windows_file, open_windows_file
from venvwin.paths import capsules_dir, ensure_runtime_dirs, profiles_dir
from venvwin.profile import RunnerProfile, save_profile


def prepare_runtime(tmp_path: Path) -> Path:
    root = tmp_path / "runtime"
    ensure_runtime_dirs(root)
    save_profile(profiles_dir(root), RunnerProfile.default())
    return root


def test_file_classification_is_predictable(tmp_path: Path) -> None:
    assert classify_windows_file(tmp_path / "setup.exe") == "installer"
    assert classify_windows_file(tmp_path / "installer.exe") == "installer"
    assert classify_windows_file(tmp_path / "tool.exe") == "portable-exe"
    assert classify_windows_file(tmp_path / "package.msi") == "installer"
    assert classify_windows_file(tmp_path / "bundle.msix") == "installer"


def test_open_portable_exe_dry_run_creates_capsule_and_launch_command(tmp_path: Path) -> None:
    root = prepare_runtime(tmp_path)
    app = tmp_path / "LegacyTool.exe"
    app.write_bytes(b"MZ")

    result = open_windows_file(capsules_dir(root), profiles_dir(root), app, dry_run=True)

    assert result["action"] == "open"
    assert result["file_type"] == "portable-exe"
    assert result["capsule_id"] == "legacytool"
    assert result["command"] == ["wine", str(app)]
    assert result["env"]["WINEARCH"] == "win64"
    assert Path(result["env"]["WINEPREFIX"]).name == "prefix"


def test_open_msi_dry_run_routes_through_msiexec(tmp_path: Path) -> None:
    root = prepare_runtime(tmp_path)
    package = tmp_path / "Setup.msi"
    package.write_bytes(b"msi")

    result = open_windows_file(capsules_dir(root), profiles_dir(root), package, dry_run=True)

    assert result["action"] == "install"
    assert result["file_type"] == "installer"
    assert result["command"] == ["wine", "msiexec", "/i", str(package)]
    assert result["env"]["WINEARCH"] == "win64"
