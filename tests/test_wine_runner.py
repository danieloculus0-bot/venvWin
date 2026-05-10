from __future__ import annotations

from pathlib import Path

import pytest

from venvwin.capsule import Capsule
from venvwin.profile import RunnerProfile
from venvwin.runner import WineRunner, get_runner


def make_capsule(tmp_path: Path) -> Capsule:
    profile = RunnerProfile.default()
    return Capsule.new("Sample App", tmp_path / "capsules", profile)


def test_wine_launch_command_uses_isolated_prefix(tmp_path: Path) -> None:
    capsule = make_capsule(tmp_path)
    command = WineRunner().prepare_launch(capsule, "C:/Program Files/Sample/sample.exe")

    assert command.env["WINEPREFIX"] == capsule.prefix_path
    assert command.env["WINEARCH"] == "win64"
    assert command.args == ["wine", "C:/Program Files/Sample/sample.exe"]


def test_wine_exe_installer_runs_directly(tmp_path: Path) -> None:
    capsule = make_capsule(tmp_path)
    command = WineRunner().prepare_install(capsule, "/downloads/setup.exe")

    assert command.args == ["wine", "/downloads/setup.exe"]


def test_wine_msi_installer_uses_msiexec(tmp_path: Path) -> None:
    capsule = make_capsule(tmp_path)
    command = WineRunner().prepare_install(capsule, "/downloads/setup.msi")

    assert command.args == ["wine", "msiexec", "/i", "/downloads/setup.msi"]


def test_wine_msix_is_honestly_rejected(tmp_path: Path) -> None:
    capsule = make_capsule(tmp_path)

    with pytest.raises(ValueError, match="MSIX/AppX"):
        WineRunner().prepare_install(capsule, "/downloads/app.msix")


def test_runner_lookup_accepts_wine_aliases() -> None:
    assert isinstance(get_runner("wine"), WineRunner)
    assert isinstance(get_runner("wine64"), WineRunner)
