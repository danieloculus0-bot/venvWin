#!/usr/bin/env python3
"""Reliable QEMU HMP operator for headless diagnostics only.

Monitor responses and screenshots are never counted as *guest-origin* proof.
"""
from __future__ import annotations

import argparse
import os
import socket
import time
from pathlib import Path


def _read_hmp_prompt(client: socket.socket, deadline: float) -> str:
    """Consume one COMPLETE prompt; an initial banner is not a command ACK."""
    buf = ""
    while time.monotonic() < deadline:
        client.settimeout(max(0.05, deadline - time.monotonic()))
        try:
            chunk = client.recv(8192)
        except socket.timeout:
            break
        if not chunk:
            raise RuntimeError("QEMU closed the monitor socket before its prompt")
        buf += chunk.decode(errors="replace")
        if buf.endswith("(qemu) ") or buf.endswith("(qemu)"):
            return buf
    raise RuntimeError("QEMU HMP prompt was not fully received: " + buf[-300:])


def send_monitor_command(monitor: Path, command: str, timeout: float = 8.0) -> str:
    if not monitor.is_socket():
        raise RuntimeError("QEMU HMP Unix socket missing")
    if "\n" in command or "\r" in command:
        raise ValueError("multi-command monitor injection forbidden")
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(timeout)
        client.connect(str(monitor))
        # Do not reuse the first banner prompt as a post-command response.
        _read_hmp_prompt(client, time.monotonic() + timeout)
        client.sendall((command + "\n").encode())
        response = _read_hmp_prompt(client, time.monotonic() + timeout)
        if "unknown command" in response.lower() or "error:" in response.lower():
            raise RuntimeError("QEMU rejected command: " + response[-300:])
        return response[-700:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True, type=Path)
    parser.add_argument("--action", choices=["enter", "screen"], required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.action == "enter":
        result = send_monitor_command(args.socket, "sendkey ret")
        print("QEMU_ENTER_ACKNOWLEDGED (not proof of boot)")
        print(result)
        return 0
    if args.output is None or not args.output.is_absolute():
        parser.error("screen output requires an absolute path")
    destination = args.output.resolve()
    if not destination.parent.is_dir():
        parser.error("screenshot output directory does not exist")
    command = "screendump " + str(destination)
    print("QEMU_SCREEN_REQUEST=" + command)
    result = send_monitor_command(args.socket, command)
    for _ in range(30):
        if destination.exists() and destination.stat().st_size >= 128:
            print("QEMU_SCREEN_SAVED=" + str(destination))
            print(result)
            return 0
        time.sleep(0.1)
    raise RuntimeError("QEMU acknowledged screendump but frame was not saved: " + result)


if __name__ == "__main__":
    raise SystemExit(main())
