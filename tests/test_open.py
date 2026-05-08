from pathlib import Path

from venvwin.open import app_name_from_path, classify_windows_file


def test_app_name_from_path():
    assert app_name_from_path(Path("Notepad-Plus-Plus.exe")) == "Notepad Plus Plus"
    assert app_name_from_path(Path("setup.exe")) == "setup"


def test_classify_windows_file():
    assert classify_windows_file(Path("setup.exe")) == "installer"
    assert classify_windows_file(Path("app-installer.exe")) == "installer"
    assert classify_windows_file(Path("thing.msi")) == "installer"
    assert classify_windows_file(Path("portable-tool.exe")) == "portable-exe"
