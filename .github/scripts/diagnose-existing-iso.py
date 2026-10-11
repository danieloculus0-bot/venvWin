#!/usr/bin/env python3
"""Observe the SAME prebuilt ISO in BIOS and UEFI QEMU without modifying it.

Only guest serial markers prove guest-ready/first-run. Framebuffer screenshots,
firmware state and serial logs are diagnostics; they never count as boot success.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import socket
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageStat


def monitor_command(socket_path: Path, cmd: str) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(3)
        sock.connect(str(socket_path))
        sock.sendall((cmd + "\n").encode("ascii"))
        time.sleep(0.25)
        try:
            return sock.recv(8192).decode("utf-8", errors="replace")
        except socket.timeout:
            return "monitor_response_timeout"


def capture(socket_path: Path, target: Path) -> dict:
    raw = target.with_suffix(".ppm")
    try:
        if raw.exists():
            raw.unlink()
        response = monitor_command(socket_path, "screendump " + str(raw))
        for _ in range(25):
            if raw.is_file() and raw.stat().st_size > 1024:
                break
            time.sleep(0.1)
        if not raw.is_file() or raw.stat().st_size <= 1024:
            return {"capture": "unavailable", "monitor": response[-400:]}
        with Image.open(raw) as im:
            image = im.convert("RGB")
            image.save(target, optimize=True)
            stat = ImageStat.Stat(image)
            hist = image.convert("L").histogram()
            n = sum(hist)
            entropy = -sum((v / n) * math.log2(v / n) for v in hist if v)
            return {
                "capture": "saved", "file": str(target), "dimensions": list(image.size),
                "rgb_mean": [round(v, 2) for v in stat.mean],
                "grayscale_entropy": round(entropy, 3),
                "meaning": "diagnostic_screen_only_not_guest_proof",
            }
    except Exception as exc:
        return {"capture": "error", "message": str(exc)[:400]}
    finally:
        if raw.exists():
            raw.unlink()


def firmware_files() -> tuple[Path, Path] | None:
    root = Path("/usr/share/OVMF")
    candidates = [
        ("OVMF_CODE_4M.fd", "OVMF_VARS_4M.fd"),
        ("OVMF_CODE.fd", "OVMF_VARS.fd"),
        ("OVMF_CODE_4M.secboot.fd", "OVMF_VARS_4M.fd"),
    ]
    for code, variables in candidates:
        if (root / code).is_file() and (root / variables).is_file():
            return root / code, root / variables
    return None


def simulate(mode: str, iso: Path, out: Path, seconds: int) -> dict:
    socket_file = Path(tempfile.gettempdir()) / ("venvwin-qemu-" + mode + ".sock")
    if socket_file.exists():
        socket_file.unlink()
    serial = out / ("verify-" + mode + "-serial.log")
    qemu_log = out / ("verify-" + mode + "-qemu-stderr.log")
    probes = [12, 40, seconds - 5] if seconds > 50 else [10, seconds - 5]
    result: dict = {
        "mode": mode, "status": "unverified", "serial_file": str(serial),
        "screenshots": [], "guest_ready": False, "first_run": False,
        "qemu_exit_code": None, "qemu_command_excludes_writable_iso_drive": True,
    }
    command = [
        "qemu-system-x86_64", "-accel", "tcg", "-m", "3072", "-smp", "2",
        "-cdrom", str(iso), "-boot", "d",
        "-vga", "std", "-display", "vnc=127.0.0.1:0",
        "-monitor", "unix:" + str(socket_file) + ",server,nowait",
        "-serial", "file:" + str(serial),
        "-no-reboot", "-net", "none",
    ]
    with tempfile.TemporaryDirectory(prefix="venvwin-ovmf-") as tmp:
        if mode == "uefi":
            firmware = firmware_files()
            if firmware is None:
                result["error"] = "OVMF firmware not found"
                return result
            code, variable_template = firmware
            vars_copy = Path(tmp) / variable_template.name
            shutil.copyfile(variable_template, vars_copy)
            command.extend([
                "-drive", "if=pflash,format=raw,readonly=on,file=" + str(code),
                "-drive", "if=pflash,format=raw,file=" + str(vars_copy),
            ])
            result["firmware"] = str(code)
        with qemu_log.open("wb") as err:
            proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=err)
            start = time.monotonic()
            captured = set()
            try:
                while proc.poll() is None and time.monotonic() - start < seconds:
                    elapsed = time.monotonic() - start
                    for point in probes:
                        if elapsed >= point and point not in captured:
                            captured.add(point)
                            screenshot = out / ("verify-" + mode + "-screen-" + str(point) + "s.png")
                            result["screenshots"].append({
                                "elapsed_seconds": point, **capture(socket_file, screenshot)
                            })
                    time.sleep(1)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=5)
                result["qemu_exit_code"] = proc.returncode
                result["duration_seconds"] = round(time.monotonic() - start, 2)
    if serial.exists():
        data = serial.read_text(errors="replace")
        # Only exact serial lines from guest code count, never text from host command.
        result["serial_bytes"] = serial.stat().st_size
        result["guest_started"] = "BEAN_GUEST_STARTED" in data.splitlines()
        result["guest_ready"] = "BEAN_GUEST_READY" in data.splitlines()
        result["first_run"] = "BEAN_GUEST_FIRST_RUN_PASS" in data.splitlines()
        result["guest_not_ready"] = "BEAN_GUEST_NOT_READY" in data.splitlines()
    else:
        result["serial_bytes"] = 0
    if result["guest_ready"] and result["first_run"]:
        result["status"] = "verified"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seconds", type=int, default=100)
    args = parser.parse_args()
    if args.seconds < 30 or args.seconds > 240:
        parser.error("--seconds needs 30..240")
    iso = Path(args.iso).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for mode in ("bios", "uefi"):
        print("Starting " + mode.upper() + " screen+serial diagnostics", flush=True)
        results.append(simulate(mode, iso, out, args.seconds))
        print(json.dumps(results[-1], indent=2), flush=True)
    record = {
        "schema": "venvwin.qemu-visual-diagnostics.v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "iso_unchanged": True,
        "bios_uefi": results,
        "interpretation": "Framebuffer screens are observations, not guest boot proof",
    }
    (out / "verify-qemu-visual-report.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
