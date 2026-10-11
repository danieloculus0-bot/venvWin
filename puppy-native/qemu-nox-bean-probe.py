#!/usr/bin/env python3
"""QEMU no-X guest evidence probe; guest serial output is the only proof.

This automation selects stock Puppy's 5th boot entry (No X) and types into
the actual guest console. QEMU key events and screenshots never count as proof.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import time
from PIL import Image
from vncdotool import api
from importlib.machinery import SourceFileLoader

ROOT=Path(__file__).resolve().parent
monitor=SourceFileLoader("qemu_monitor_probe",str(ROOT/"qemu-monitor-probe.py")).load_module()

COMMANDS=[
    "echo VENVWIN_GUEST_NOX_SHELL_RESPONSIVE >/dev/ttyS0",
    "test -f /opt/bean/core/bean/memory/store.py && echo VENVWIN_BEAN_SFS_PRESENT >/dev/ttyS0 || echo VENVWIN_BEAN_SFS_MISSING >/dev/ttyS0",
    "command -v python3 >/dev/ttyS0 2>&1",
    "PYTHONPATH=/opt/bean/core python3 /usr/local/lib/venvwin/bean-mini-service.py --self-test >/dev/ttyS0 2>&1",
]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--socket",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    # QEMU is already running at the GRUB4DOS boot menu, 5th item is No X.
    for _ in range(4):
        print("HOST_NOX_DOWN_KEY_ACK",monitor.send_monitor_command(args.socket,"sendkey down").strip(),flush=True)
        time.sleep(0.6)
    print("HOST_NOX_BOOT_SELECT_ACK",monitor.send_monitor_command(args.socket,"sendkey ret").strip(),flush=True)
    time.sleep(145)
    with api.connect("127.0.0.1::5900",timeout=30) as guest:
        guest.timeout=30
        guest.captureScreen(str(args.out/"puppy-nox-before-input.png"))
        print("HOST_QEMU_NOX_SCREEN_OBSERVED",Image.open(args.out/"puppy-nox-before-input.png").size,flush=True)
        for attempt in (1,2):
            for command in COMMANDS:
                guest.typeText(command)
                guest.keyPress("enter")
                time.sleep(2.5)
            time.sleep(5)
            guest.captureScreen(str(args.out/("puppy-nox-after-input-%d.png"%attempt)))
            print("HOST_TYPED_COMMANDS_ATTEMPTED_NOT_PROOF",attempt,flush=True)
            time.sleep(30)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
