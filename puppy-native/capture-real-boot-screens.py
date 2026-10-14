#!/usr/bin/env python3
"""Capture an ACTUAL QEMU Puppy screen, not an illustrative render.

Puppy boot verification is independent: serial markers come from the guest
autostart script, whereas images come from QEMU's live VNC output. The
screenshot file's mere presence cannot certify a successful boot.
"""
from __future__ import annotations
import argparse
import time
from pathlib import Path
from PIL import Image
from vncdotool import api

def desktop_visible(path: Path) -> bool:
    with Image.open(path) as img:
        rgb=img.convert("RGB")
        w,h=rgb.size
        if w < 1024 or h < 700: return False
        # JWM actual bottom tray persists in both branded and unbranded Puppy.
        coords=((12,h-17),(w//2,h-17),(w-55,h-17))
        return sum(sum(rgb.getpixel(p))/3>28 for p in coords)>=2

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--max-seconds",type=int,default=570)
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    with api.connect("127.0.0.1::5900",timeout=35) as vnc:
        vnc.timeout=35
        frame=0
        while time.monotonic()-started<args.max_seconds:
            frame+=1
            path=out/"qemu-live-latest.png"
            vnc.captureScreen(str(path))
            if frame==1:
                initial=out/"qemu-after-boot-selection.png"
                initial.write_bytes(path.read_bytes())
            if desktop_visible(path):
                first=out/"qemu-real-desktop-first.png"
                first.write_bytes(path.read_bytes())
                print("VNC_HOST_OBSERVED_ACTUAL_DESKTOP",flush=True)
                time.sleep(25)  # allow Puppy Quick Setup to appear
                vnc.captureScreen(str(out/"qemu-real-desktop-settled.png"))
                # Actual BookwormPup64 welcome dialog in the screenshot is
                # positioned at x269..1017, y149..645 on 1280x800. Use
                # mouse only: vncdotool.keyPress("alt-f4") crashes on this
                # runner with TypeError, and faking screenshots is forbidden.
                with Image.open(out/"qemu-real-desktop-settled.png") as img:
                    rgb=img.convert("RGB")
                    if rgb.size == (1280,800):
                        orange=rgb.getpixel((530,159))
                        white=rgb.getpixel((530,245))
                        welcome=(orange[0]>175 and 70<orange[1]<200 and
                                 orange[2]<70 and min(white)>160)
                    else:
                        welcome=False
                print("VNC_HOST_PUPPY_WELCOME_OBSERVED="+str(welcome),flush=True)
                if welcome:
                    vnc.mouseMove(1004,160)
                    vnc.mousePress(1)
                    time.sleep(9)
                vnc.captureScreen(str(out/"qemu-real-desktop-after-setup.png"))
                # The original JWM menu button really is at the bottom left.
                if desktop_visible(out/"qemu-real-desktop-after-setup.png"):
                    vnc.mouseMove(43,785)
                    vnc.mousePress(1)
                    time.sleep(5)
                vnc.captureScreen(str(out/"qemu-real-start-menu.png"))
                print("VNC_HOST_CAPTURED_REAL_BOOT_DESKTOP_AND_MENU",flush=True)
                return 0
            if frame%4==1: print("VNC_HOST_WAITING_FOR_REAL_DESKTOP",frame,flush=True)
            time.sleep(12)
    print("VNC_HOST_DESKTOP_NOT_OBSERVED",flush=True)
    return 1

if __name__=="__main__":
    raise SystemExit(main())
