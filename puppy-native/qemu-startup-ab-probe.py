#!/usr/bin/env python3
"""Differential, read-only QEMU startup diagnostic for one cached Puppy ISO.

Never constructs distro images or executes a Windows installer. Compares actual
QEMU configurations using guest serial, host framebuffer and manual, read-only
VNC diagnostics. Manual diagnostics do NOT count as automatic startup proof.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MONITOR_TOOL = ROOT / "puppy-native" / "qemu-monitor-probe.py"
VNC_TOOL = ROOT / "puppy-native" / "qemu-desktop-guest-proof.py"


def monitor(socket_path: Path, action: str, output: Path | None = None) -> dict:
    argv = [sys.executable, str(MONITOR_TOOL), "--socket", str(socket_path),
            "--action", action]
    if output is not None:
        argv += ["--output", str(output.resolve())]
    try:
        result = subprocess.run(argv, text=True, capture_output=True, timeout=18)
        return {"action": action, "exit": result.returncode,
                "stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]}
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"action": action, "error": str(exc)[:220]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--network", choices=["none", "user"], required=True)
    ap.add_argument("--duration", type=int, default=390)
    args = ap.parse_args()
    if not args.iso.is_file() or args.iso.stat().st_size < 500_000_000:
        raise ValueError("missing genuine remastered Puppy ISO")
    if not 180 <= args.duration <= 450:
        raise ValueError("must use a bounded diagnostic")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    serial = out / "guest-serial.log"
    hmp = out / "hmp.sock"
    for path in (serial, hmp):
        path.unlink(missing_ok=True)
    net = (["-net", "none"] if args.network == "none" else
           ["-netdev", "user,id=guestnet", "-device", "e1000,netdev=guestnet"])
    cmd = ["qemu-system-x86_64", "-accel", "tcg", "-m", "3072", "-smp", "2",
           "-boot", "order=d", "-cdrom", str(args.iso.resolve()), "-vga", "std",
           "-usb", "-device", "usb-tablet", "-display", "vnc=127.0.0.1:0",
           "-serial", f"file:{serial}", "-monitor",
           f"unix:{hmp},server=on,wait=off", "-no-reboot", *net]
    journal = {"network": args.network, "iso_bytes": args.iso.stat().st_size,
               "qemu_cmd": cmd, "frames": [], "monitor_results": [],
               "helper": "not_started", "guest_serial_bytes": 0,
               "auto_guest_marker_seen": False, "manual_terminal_marker_seen": False}
    helper = None
    qemu_err = (out / "qemu-stderr.log").open("w")
    qemu = subprocess.Popen(cmd, stdout=qemu_err, stderr=subprocess.STDOUT)
    try:
        time.sleep(10)
        journal["monitor_results"].append(monitor(hmp, "enter"))
        helper_log = (out / "manual-vnc-diagnostic.log").open("w")
        try:
            helper = subprocess.Popen([sys.executable, str(VNC_TOOL),
                "--output", str(out), "--wait-seconds", str(args.duration - 75)],
                stdout=helper_log, stderr=subprocess.STDOUT)
            journal["helper"] = "running"
        finally:
            helper_log.close()
        started = time.monotonic()
        deadline = started + args.duration
        next_frame = started + 40
        while time.monotonic() < deadline and qemu.poll() is None:
            time.sleep(5)
            now = time.monotonic()
            if now >= next_frame:
                index = len(journal["frames"]) + 1
                ppm = out / f"frame-{index:02d}.ppm"
                status = monitor(hmp, "screen", ppm)
                journal["monitor_results"].append(status)
                if status.get("exit") == 0 and ppm.is_file():
                    try:
                        with Image.open(ppm) as image:
                            image.load()
                            png = out / f"frame-{index:02d}.png"
                            image.convert("RGB").save(png)
                            journal["frames"].append({"name": png.name, "size": image.size,
                                                      "seconds": round(now - started)})
                    except (OSError, ValueError) as exc:
                        journal["frames"].append({"name": ppm.name, "error":str(exc)[:200]})
                    finally:
                        ppm.unlink(missing_ok=True)
                next_frame = now + 65
            if serial.is_file():
                content = serial.read_text(errors="replace")
                journal["guest_serial_bytes"] = serial.stat().st_size
                journal["auto_guest_marker_seen"] = "PUPPY_GUEST_BOOT_PROVEN" in content.splitlines()
                journal["manual_terminal_marker_seen"] = (
                    "VENVWIN_INTERACTIVE_GUEST_TERMINAL_CONFIRMED" in content.splitlines())
            if helper is not None and helper.poll() is not None:
                journal["helper"] = f"exited_{helper.returncode}"
                if journal["manual_terminal_marker_seen"]:
                    break
        journal["qemu_exited_early"] = qemu.poll() is not None
        if helper is not None and helper.poll() is None:
            helper.terminate()
            try:
                helper.wait(timeout=6)
            except subprocess.TimeoutExpired:
                helper.kill()
                helper.wait()
        if helper is not None:
            journal["helper_returncode"] = helper.returncode
        journal["guest_serial_bytes"] = serial.stat().st_size if serial.is_file() else 0
        if serial.is_file():
            content = serial.read_text(errors="replace")
            journal["auto_guest_marker_seen"] = "PUPPY_GUEST_BOOT_PROVEN" in content.splitlines()
            journal["manual_terminal_marker_seen"] = (
                "VENVWIN_INTERACTIVE_GUEST_TERMINAL_CONFIRMED" in content.splitlines())
        return 0
    finally:
        qemu.terminate()
        try:
            qemu.wait(timeout=8)
        except subprocess.TimeoutExpired:
            qemu.kill()
            qemu.wait()
        qemu_err.close()
        (out / "diagnosis.json").write_text(json.dumps(journal, indent=2, sort_keys=True) + "\n")
        print("HOST_DIAGNOSTIC_ONLY", json.dumps({
            "network": journal["network"], "qemu_exited_early":journal.get("qemu_exited_early"),
            "frames":len(journal["frames"]), "serial_bytes":journal["guest_serial_bytes"],
            "real_auto_guest_boot_marker":journal["auto_guest_marker_seen"],
            "real_manual_terminal_marker":journal["manual_terminal_marker_seen"],
            "vnc_helper":journal["helper"],
        }, sort_keys=True), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
