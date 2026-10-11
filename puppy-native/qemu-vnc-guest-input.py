#!/usr/bin/env python3
"""Diagnostic GUI input only; never an autostart proof or boot acceptance."""
from __future__ import annotations
import argparse
import time
from pathlib import Path
from PIL import Image
from vncdotool import api

def type_guest(client, command: str) -> None:
    for char in command:
        if char == "-":
            client.keyPress("minus")
        elif char.isupper():
            client.keyPress("shift-" + char.lower())
        else:
            client.keyPress(char)
    client.keyPress("enter")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    with api.connect("127.0.0.1::5900", timeout=20) as client:
        client.timeout = 20
        client.captureScreen(str(out / "qemu-vnc-before.png"))
        size = Image.open(out / "qemu-vnc-before.png").size
        print("VNC_SCREEN_OBSERVED=", size, flush=True)
        if size[0] < 1100 or size[1] < 700:
            print("VNC_GUEST_DESKTOP_NOT_LARGE_ENOUGH_FOR_KNOWN_COORDS", flush=True)
            return 3
        for attempt in (1, 2):
            if attempt == 2:
                time.sleep(45)
            # Coordinates recovered from actual 1280x800 guest screenshot.
            client.mouseMove(1017, 694)
            client.mousePress(1)
            time.sleep(8)
            client.captureScreen(str(out / ("qemu-vnc-after-setup-%s.png" % attempt)))
            client.mouseMove(32, 122)
            client.mousePress(1)
            time.sleep(9)
            client.captureScreen(str(out / ("qemu-vnc-terminal-%s.png" % attempt)))
            type_guest(client, "venvwin-diagnostic")
            time.sleep(6)
            client.captureScreen(str(out / ("qemu-vnc-diagnostic-%s.png" % attempt)))
            print("VNC_GUEST_DIAGNOSTIC_INPUT_ATTEMPT=%s" % attempt, flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
