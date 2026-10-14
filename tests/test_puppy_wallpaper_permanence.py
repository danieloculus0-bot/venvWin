"""Approved venvWin background MUST replace only the ROX backdrop.

Source-unit gates. Real boot + visual checks are separate.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "puppy-native" / "venvwin-wallpaper-apply"
BUILD = ROOT / "puppy-native" / "build-puppy.sh"
SESSION = ROOT / "puppy-native" / "venvwin-session"
EXPECTED_SHA = "6187575271bf955ba4daaca6db01f168fdead49b4abce22c7f3275a1b004b6ab"


def mutator_code():
    source = SCRIPT.read_text()
    return source.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]


def run_edit(pin_path: Path, wallpaper: str):
    return subprocess.run(
        [sys.executable, "-c", mutator_code(), str(pin_path), wallpaper],
        capture_output=True, text=True, timeout=10,
    )


def test_changes_only_approved_backdrop_without_resetting_icons(tmp_path):
    pin = tmp_path / "PuppyPin"
    original = '<?xml version="1.0"?>\n<pinboard>\n' \
        '  <backdrop style="Stretched">/old-puppy-background.jpg</backdrop>\n' \
        '  <icon x="191" y="88" label="Custom Desktop">/root/Desktop/custom.desktop</icon>\n' \
        '</pinboard>\n'
    pin.write_text(original)
    result = run_edit(pin, "/usr/share/backgrounds/venvwin-wallpaper.png")
    assert result.returncode == 0, result.stderr
    updated = pin.read_text()
    assert "/old-puppy-background.jpg" not in updated
    assert '<backdrop style="Stretched">/usr/share/backgrounds/venvwin-wallpaper.png</backdrop>' in updated
    assert '<icon x="191" y="88" label="Custom Desktop">/root/Desktop/custom.desktop</icon>' in updated
    assert run_edit(pin, "/usr/share/backgrounds/venvwin-wallpaper.png").returncode == 0


def test_rejects_unrecognized_pinboard(tmp_path):
    pin = tmp_path / "PuppyPin"
    original = "<html>not a ROX desktop</html>"
    pin.write_text(original)
    result = run_edit(pin, "/usr/share/backgrounds/venvwin-wallpaper.png")
    assert result.returncode != 0
    assert pin.read_text() == original


def test_can_insert_default_backdrop_when_missing(tmp_path):
    pin = tmp_path / "PuppyPin"
    pin.write_text("<pinboard>\n<icon x='12' y='18'>desktop</icon>\n</pinboard>\n")
    assert run_edit(pin, "/usr/share/backgrounds/venvwin-wallpaper.png").returncode == 0
    assert "venvwin-wallpaper.png" in pin.read_text()
    assert "<icon x='12' y='18'>desktop</icon>" in pin.read_text()


def test_build_uses_exact_approved_artwork_never_old_svg():
    source = BUILD.read_text()
    assert "venvwin-amber-arc.webp.b64" in source
    assert EXPECTED_SHA in source
    assert 'base64 -d "$WALLPAPER_SOURCE"' in source
    assert "venvwin-wallpaper.svg" not in source
    assert 'install -m 0755 "$ROOT/puppy-native/venvwin-wallpaper-apply"' in source
    assert 'venvwin-default-PuppyPin' in source


def test_reassert_only_during_first_boot_setup_not_indefinitely():
    source = SESSION.read_text()
    assert source.count("/usr/local/bin/venvwin-wallpaper-apply") == 3
    assert "sleep 27" in source and "sleep 34" in source
    assert "venvwin-wallpaper-apply" in BUILD.read_text()


def test_production_does_not_overwrite_existing_desktop_icon_layout():
    source = SCRIPT.read_text()
    assert "replace only the backdrop" in source.lower()
    assert "VENVWIN_ROX_REAL_PINBOARD_RELOADED" in source
    assert "VENVWIN_WALLPAPER_MISSING_NO_FAKE_SUCCESS" in source
