#!/usr/bin/env python3
"""BEAN decides whether a real Puppy Wine test is NEW before building any ISO.

Small fixture compilation is okay. Large remaster/QEMU is refused when
previous evidence already passed or identified an unchanged blocker.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from bean_install_memory import Memory, fingerprint, file_hash
from windows_install_smoke import build

RUNTIME = "official-BookwormPup64-10.0.12|kernel-6.1.148|debian-bookworm-multiarch-wine32|isolated-qemu-nat-v1"
SOURCES = (
    "puppy-native/build-puppy.sh",
    "puppy-native/venvwin-wine-guest-lab",
    "puppy-native/prove-puppy-wine-qemu.sh",
    "puppy-native/windows_install_smoke.py",
    "src/venvwin/cli.py",
    "src/venvwin/install.py",
    "src/venvwin/open.py",
    "src/venvwin/runner.py",
    "src/venvwin/capsule.py",
    "src/venvwin/intake.py",
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    stage = args.stage.resolve()
    if not all((root / p).is_file() for p in SOURCES):
        raise ValueError("real source missing, refuse building")
    build(stage)
    hash_lines = []
    for name in ("Setup.exe", "SimpleMsi.msi", "SmokeApp.exe"):
        hash_lines.append(file_hash(stage / name) + "  " + name)
    (stage / "manifest.sha256").write_text("\n".join(hash_lines) + "\n")
    selected = []
    decisions = {}
    with Memory(args.db) as memory:
        for case in ("nsis-exe", "wix-msi"):
            identity = fingerprint("puppy-guest", [root / p for p in SOURCES], RUNTIME + "|" + case)
            (stage / (case + ".fingerprint")).write_text(identity + "\n")
            verdict = memory.plan("puppy-guest", case, identity)
            decisions[case] = verdict
            if verdict["decision"] == "run":
                selected.append(case)
    (stage / "selected-cases.txt").write_text("\n".join(selected) + "\n")
    print("BEAN_REAL_GUEST_INSTALL_DECISIONS", json.dumps(decisions, sort_keys=True), flush=True)
    print("BEAN_REAL_GUEST_SELECTED_CASES", json.dumps(selected), flush=True)
    if not selected:
        print("BEAN_REFUSED_IDENTICAL_GUEST_WINE_RERUN", flush=True)
        return 75
    return 0

if __name__ == "__main__":
    sys.exit(main())
