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
                def has_orange_header(path: Path, x: int, y: int) -> bool:
                    with Image.open(path) as im:
                        rgb=im.convert("RGB")
                        if rgb.size != (1280,800): return False
                        r,g,b=rgb.getpixel((x,y))
                        return r>200 and 90<g<185 and b<55

                # Stock BookwormPup64 normally opens Quick Setup after the
                # real desktop becomes visible. Click its actual close button
                # only when its observed orange titlebar is present.
                if has_orange_header(out/"qemu-real-desktop-settled.png",530,116):
                    print("VNC_HOST_ORIGINAL_PUPPY_QUICK_SETUP_VISIBLE",flush=True)
                    vnc.mouseMove(1042,116)
                    vnc.mousePress(1)
                    time.sleep(8)
                else:
                    print("VNC_HOST_NO_QUICK_SETUP_AT_SETTLED_DESKTOP",flush=True)
                interim=out/"qemu-real-desktop-after-quick-setup.png"
                vnc.captureScreen(str(interim))

                # Some original Puppies then display a separate Welcome
                # screen (at x269..1017,y149..645). This also must be closed
                # as a real guest window, never photoshopped from a capture.
                if has_orange_header(interim,530,159):
                    print("VNC_HOST_ORIGINAL_PUPPY_WELCOME_VISIBLE",flush=True)
                    vnc.mouseMove(1004,160)
                    vnc.mousePress(1)
                    time.sleep(8)
                else:
                    print("VNC_HOST_NO_WELCOME_DIALOG_AFTER_QUICK_SETUP",flush=True)
                # venvWin opens its real YAD Control Center on first boot.
                # Close that application window for an unobstructed wallpaper
                # screenshot; do not alter pixels or fake close state.
                clear=out/"qemu-real-desktop-control-center-check.png"
                vnc.captureScreen(str(clear))
                if has_orange_header(clear,530,195):
                    print("VNC_HOST_VENVWIN_CONTROL_CENTER_VISIBLE",flush=True)
                    vnc.mouseMove(1001,195)
                    vnc.mousePress(1)
                    time.sleep(5)
                vnc.captureScreen(str(out/"qemu-real-desktop-after-setup.png"))
                if (has_orange_header(out/"qemu-real-desktop-after-setup.png",530,195)):
                    print("VNC_HOST_CONTROL_CENTER_STILL_VISIBLE_REFUSE_WALLPAPER_PROOF",flush=True)
                    return 11
                if (has_orange_header(out/"qemu-real-desktop-after-setup.png",530,116)
                    or has_orange_header(out/"qemu-real-desktop-after-setup.png",530,159)):
                    print("VNC_HOST_ORIGINAL_PUPPY_SETUP_STILL_OPEN",flush=True)
                    return 9
                print("VNC_HOST_PUPPY_SETUP_DISMISSED_VIA_REAL_INPUT",flush=True)
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
