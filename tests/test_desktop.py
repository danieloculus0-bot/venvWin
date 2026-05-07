from pathlib import Path

from venvwin.capsule import create_capsule
from venvwin.desktop import generate_desktop_launcher
from venvwin.profile import RunnerProfile


def test_generate_desktop_launcher(tmp_path: Path):
    capsule = create_capsule(tmp_path, "Test App", RunnerProfile.default())

    launcher = generate_desktop_launcher(
        tmp_path,
        capsule,
        "Test App",
        "C:\\Program Files\\Test\\test.exe",
    )

    content = launcher.read_text(encoding="utf-8")
    assert launcher.name == "test-app.desktop"
    assert "[Desktop Entry]" in content
    assert "Name=Test App" in content
    assert "WINEPREFIX=" in content
    assert "test.exe" in content
