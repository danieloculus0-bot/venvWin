from venvwin.capsule import Capsule
from venvwin.profile import RunnerProfile
from venvwin.runner import WineRunner


def test_wine_runner_prepares_install_command():
    profile = RunnerProfile(name="default", runner="wine", arch="win64")
    capsule = Capsule(
        app_name="Test App",
        capsule_id="test-app",
        created_at="now",
        updated_at="now",
        profile=profile,
        prefix_path="/tmp/venvwin/test-app/prefix",
    )

    command = WineRunner().prepare_install(capsule, "setup.exe")

    assert command.env["WINEPREFIX"] == "/tmp/venvwin/test-app/prefix"
    assert command.env["WINEARCH"] == "win64"
    assert command.args == ["wine", "setup.exe"]
    assert "WINEPREFIX=" in command.shell_preview()
