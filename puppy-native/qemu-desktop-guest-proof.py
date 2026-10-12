#!/usr/bin/env python3
"""Evidence-first VNC inspection of actual Puppy desktop, without OCR or fake guest facts.

QEMU VNC input is NOT guest proof. The independent /dev/ttyS0 log is.
Never manually execute /root/Startup/venvwin-guest-probe; that is the automatic
boot acceptance marker and must come only from /root/Startup.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from PIL import Image, ImageChops
from vncdotool import api


def fraction_changed(first: Path, second: Path, region=(180, 90, 1180, 750)) -> float:
    a=Image.open(first).convert("RGB").crop(region)
    b=Image.open(second).convert("RGB").crop(region)
    bbox=ImageChops.difference(a,b)
    hist=bbox.convert("L").point(lambda v: 255 if v > 12 else 0).histogram()
    return sum(hist[1:])/max(1,sum(hist))


def send_text(client, text: str) -> None:
    # vncdotool 1.4.2 has keyPress, NOT typeText.
    for char in text:
        if char.isascii() and char.isalnum():
            client.keyPress("shift-"+char.lower() if char.isupper() else char)
        elif char == "-":
            client.keyPress("minus")
        else:
            raise ValueError("refuse complex command injection via GUI")
    client.keyPress("enter")


def looks_like_running_desktop(image: Path) -> bool:
    im=Image.open(image).convert("RGB")
    if im.size[0] < 1200 or im.size[1] < 760:
        return False
    # Most text-mode boot screens are black in the last pixel row. The
    # upstream JWM taskbar spans the bottom edge at a clear luminance > 30.
    def luminance(x,y):
        r,g,b=im.getpixel((x,y))
        return (r+g+b)/3
    return luminance(1130,783)>32 and luminance(12,783)>32


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--wait-seconds",default=480,type=int)
    args=ap.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    with api.connect("127.0.0.1::5900",timeout=30) as client:
        client.timeout=30
        before=out/"live-puppy-desktop-before.png"
        deadline=time.monotonic()+args.wait_seconds
        frame=0
        while time.monotonic()<deadline:
            client.captureScreen(str(before))
            frame+=1
            if looks_like_running_desktop(before):
                print("HOST_OBSERVED_REAL_PUPPY_GRAPHICAL_DESKTOP",flush=True)
                break
            if frame % 4 == 1:
                print("HOST_WAITING_FOR_LIVE_DESKTOP",frame,flush=True)
            time.sleep(15)
        else:
            print("HOST_COULD_NOT_OBSERVE_GUEST_DESKTOP",flush=True)
            return 7

        # Puppy may display the actual branded desktop for 10-25 seconds
        # BEFORE its delayed Quick Setup steals keyboard focus. Wait for it.
        time.sleep(28)
        delayed=out/"live-puppy-first-run-settled.png"
        client.captureScreen(str(delayed))
        def setup_visible(path):
            im=Image.open(path).convert("RGB")
            r,g,b=im.getpixel((540,171))
            return min(r,g,b)>170
        print("HOST_LATE_QUICK_SETUP_VISIBLE="+str(setup_visible(delayed)),flush=True)
        setup=out/"live-puppy-after-quicksetup-dismiss.png"
        if setup_visible(delayed):
            # The actual upstream window-close button is x1042,y116 at
            # 1280x800. It dismisses the guest wizard without picking storage.
            client.mouseMove(1042,116)
            client.mousePress(1)
            time.sleep(5)
            client.captureScreen(str(setup))
            if setup_visible(setup):
                print("HOST_QUICK_SETUP_CLOSE_CLICK_INEFFECTIVE_TRY_ALT_F4",flush=True)
                client.keyPress("alt-f4")
                time.sleep(4)
                client.captureScreen(str(setup))
            if setup_visible(setup):
                print("HOST_LATE_QUICK_SETUP_STILL_PRESENT_DO_NOT_TYPE",flush=True)
                return 8
            print("HOST_SETUP_DISMISSED_ACTUAL_GUEST",flush=True)
        else:
            # When the first-run helper was already dismissed or did not
            # spawn, its absence is a separate observed state, not a failure.
            client.captureScreen(str(setup))
            print("HOST_NO_FIRST_RUN_DIALOG_AT_SETTLED_DESKTOP",flush=True)

        # Stock BookwormPup64 terminal icon is x32,y122; the wallpaper/desktop
        # integration itself may be missing; rely on screenshots and serial.
        client.mouseMove(32,122)
        client.mousePress(1)
        time.sleep(10)
        terminal=out/"live-puppy-terminal-open.png"
        client.captureScreen(str(terminal))
        winchange=fraction_changed(setup,terminal)
        print(f"HOST_TERMINAL_CLICK_SCREEN_DIFFERENCE={winchange:.4f}",flush=True)
        if winchange < 0.02:
            print("HOST_TERMINAL_WINDOW_UNOBSERVED_DO_NOT_TYPE",flush=True)
            return 9

        # It is safe to type the preinstalled *read-only* diagnostic manually.
        # This is not an autostart check. The utility writes guest findings to
        # /dev/ttyS0, independently collected by QEMU in CI.
        # Explicitly foreground the real LXTerminal titlebar; Quick Setup
        # may otherwise retain the keyboard even after the terminal opens.
        client.mouseMove(121,36)
        client.mousePress(1)
        time.sleep(3)
        client.captureScreen(str(out/"live-puppy-terminal-focused.png"))
        if setup_visible(out/"live-puppy-terminal-focused.png"):
            print("HOST_SETUP_REOPENED_TERMINAL_NOT_FOCUSED",flush=True)
            return 10
        print("HOST_TERMINAL_FOCUS_REQUESTED",flush=True)
        send_text(client,"venvwin-diagnostic")
        time.sleep(15)
        client.captureScreen(str(out/"live-puppy-diagnostic-response.png"))
        print("HOST_SENT_MANUAL_DIAGNOSTIC_COMMAND_WAIT_FOR_GUEST_SERIAL",flush=True)
        return 0


if __name__=="__main__":
    raise SystemExit(main())
