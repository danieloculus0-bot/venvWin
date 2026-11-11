"""Safe venvWin identity assets for native Puppy boot and workspace."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "puppy-native" / "art"


def test_exact_venvwin_public_wordmark_in_boot_and_desktop():
    for name in ("venvwin-boot.svg", "venvwin-wallpaper.svg"):
        content = (ROOT / name).read_text(encoding="utf-8")
        root = ET.fromstring(content)
        assert root.tag.endswith("svg")
        assert "venv" in content and "Win" in content
        assert "PORTABLE" in content
        assert "#ff8a00" in content
        assert "puppy" not in content.lower()
        assert "100% working" not in content.lower()


def test_boot_image_is_native_landscape_source():
    tree = ET.parse(ROOT / "venvwin-boot.svg").getroot()
    assert tree.attrib["width"] == "1280"
    assert tree.attrib["height"] == "720"
