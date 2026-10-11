"""BEAN remains separately initiated, never an automatic Puppy boot dependency."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_no_default_bean_service_or_bulk_core():
    src=(ROOT/"puppy-native"/"venvwin-session").read_text()
    build=(ROOT/"puppy-native"/"build-puppy.sh").read_text()
    assert "venvwin-bean --serve" not in src
    assert "bean-core/" not in build
    assert "bean-mini-service" not in build
    assert "venvwin-bean" not in build
def test_venvwin_brand_retained():
    build=(ROOT/"puppy-native"/"build-puppy.sh").read_text()
    assert "venvwin-boot.svg" in build
    assert "venvwin-wallpaper.svg" in build
    assert "brand-jwm-template.py" in build
