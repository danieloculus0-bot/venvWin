"""Real venvWin wallpaper selection preserves Puppy ROX desktop functionality."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess

import pytest

try:
    from PIL import Image
except ImportError:
    Image = None  # Optional host-side screenshot test dependency

ROOT=Path(__file__).resolve().parents[1]
APPLY=ROOT/"puppy-native"/"venvwin-wallpaper-apply"
CHECK=ROOT/"puppy-native"/"check-wallpaper-screenshot.py"


def verifier():
    spec=importlib.util.spec_from_file_location("venvwallpapercheck",CHECK)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m


@pytest.mark.skipif(Image is None, reason='Pillow is optional outside the QEMU screenshot CI')
def test_wallpaper_verifier_accepts_actual_approved_image(tmp_path: Path):
    image=Image.new("RGB",(1280,800),(10,18,24))
    wall=tmp_path/"approved.png"
    shot=tmp_path/"real.png"
    image.save(wall)
    image.save(shot)
    assert verifier().compare_capture(wall,shot)==[0.0,0.0,0.0]


@pytest.mark.skipif(Image is None, reason='Pillow is optional outside the QEMU screenshot CI')
def test_wallpaper_verifier_detects_wrong_image(tmp_path: Path):
    approved=Image.new("RGB",(1280,800),(240,118,28))
    wrong=Image.new("RGB",(1280,800),(16,19,24))
    wall=tmp_path/"approved.png"
    shot=tmp_path/"real.png"
    approved.save(wall)
    wrong.save(shot)
    result=subprocess.run(["python3",str(CHECK),"--wallpaper",str(wall),
                            "--capture",str(shot)],text=True,capture_output=True)
    assert result.returncode!=0
    assert "APPROVED_WALLPAPER_NOT_VISIBLE" in result.stdout


def test_rox_apply_preserves_icons_and_reloads_real_pinboard(tmp_path: Path):
    home=tmp_path/"home"
    pin=home/"Choices/ROX-Filer/PuppyPin"
    pin.parent.mkdir(parents=True)
    pin.write_text(
        '<?xml version="1.0"?>\n<pinboard>\n'
        '  <backdrop style="Stretched">/usr/share/backgrounds/puppy.png</backdrop>\n'
        '  <icon x="32" y="128" label="Terminal">/usr/local/bin/defaultterminal</icon>\n'
        '</pinboard>\n'
    )
    approved=tmp_path/"approved.png"
    approved.write_bytes(b"approved-image-fixture")
    fakebin=tmp_path/"bin"
    fakebin.mkdir()
    marker=tmp_path/"rox-invoked"
    rox=fakebin/"rox"
    rox.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$VENVWIN_ROX_TEST_MARKER"\n')
    rox.chmod(0o755)
    env=os.environ.copy()
    env.update({"HOME":str(home),"DISPLAY":":99",
                "VENVWIN_WALLPAPER_PATH":str(approved),
                "VENVWIN_ROX_TEST_MARKER":str(marker),
                "PATH":str(fakebin)+os.pathsep+env.get("PATH","")})
    for attempt in range(2):
        proc=subprocess.run(["sh",str(APPLY)],env=env,text=True,capture_output=True)
        assert proc.returncode==0,(proc.stdout,proc.stderr)
    text=pin.read_text()
    assert text.count(str(approved))==1
    assert '<icon x="32" y="128" label="Terminal">' in text
    assert "/usr/share/backgrounds/puppy.png" not in text
    assert "--RPC" in marker.read_text()
    assert (home / ".config/wallpaper/bg_img").read_text().strip() == str(approved)


def test_unknown_rox_pinboard_fails_closed(tmp_path: Path):
    home=tmp_path/"home"
    pin=home/"Choices/ROX-Filer/PuppyPin"
    pin.parent.mkdir(parents=True)
    pin.write_text("<not-a-pinboard/>")
    approved=tmp_path/"approved.png"
    approved.write_text("test")
    env=os.environ.copy()
    env.update({"HOME":str(home),"DISPLAY":":99",
                "VENVWIN_WALLPAPER_PATH":str(approved)})
    proc=subprocess.run(["sh",str(APPLY)],env=env,text=True,capture_output=True)
    assert proc.returncode != 0
    assert "UNKNOWN_ROX_PINBOARD" in proc.stderr
