#!/usr/bin/env python3
"""Import true QEMU guest-origin EXE/MSI evidence into pinned BEAN memory.

No generated pass: success requires raw ttyS0 output from the Puppy guest,
independent QEMU capture, correct staged fixture digests and actual Wine
capsule outputs. Missing evidence becomes blocked, never silently passing.
"""
import argparse
import base64
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from bean_install_memory import Memory, SCHEMA, file_hash

CASES = ("nsis-exe", "wix-msi")
RECEIPTS = ("install", "launch", "marker")

def extract(lines, case, kind):
    begin = f"VENVWIN_WINE_GUEST_RECEIPT_BEGIN={case}:{kind}"
    end = f"VENVWIN_WINE_GUEST_RECEIPT_END={case}:{kind}"
    positions = [i for i, line in enumerate(lines) if line == begin]
    if len(positions) != 1:
        raise ValueError("missing or repeated guest receipt start: " + begin)
    i = positions[0]
    if i + 2 >= len(lines) or lines[i + 2] != end:
        raise ValueError("incomplete guest receipt: " + begin)
    result = base64.b64decode(lines[i + 1], validate=True)
    if not result:
        raise ValueError("empty actual guest receipt")
    return result

def real_png(path):
    if not path.is_file():
        return False
    with path.open("rb") as stream:
        return stream.read(8) == b"\x89PNG\r\n\x1a\n" and path.stat().st_size > 1024

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--serial", type=Path, required=True)
    p.add_argument("--screenshot", type=Path, required=True)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--db", type=Path, required=True)
    args = p.parse_args()
    if not args.serial.is_file():
        raise ValueError("QEMU did not emit any guest serial")
    raw = args.serial.read_bytes()
    lines = [x.strip() for x in raw.decode("utf-8", errors="replace").replace("\r", "").splitlines()]
    if "VENVWIN_WINE_GUEST_LAB_STARTED" not in lines:
        raise ValueError("test did not execute inside Puppy guest")
    boot = "PUPPY_GUEST_BOOT_PROVEN" in lines
    screenshot = real_png(args.screenshot)
    any_failed = False
    selected = (args.fixture_dir / "selected-cases.txt").read_text().splitlines()
    if not selected or len(selected) != len(set(selected)) or any(c not in CASES for c in selected):
        raise ValueError("invalid or empty BEAN-selected real guest cases")
    for case in selected:
        out = args.evidence / case
        out.mkdir(parents=True, exist_ok=True)
        fingerprint = (args.fixture_dir / f"{case}.fingerprint").read_text().strip()
        if len(fingerprint) != 64:
            raise ValueError("malformed test identity")
        shutil.copy2(args.serial, out / "guest-serial.log")
        receipts_ok = True
        marker = f"VENVWIN_GUEST_WINDOWS_APP_PASS={case}:{fingerprint}"
        if boot and screenshot and marker in lines:
            try:
                for name, filename in (("install", "install.json"), ("launch", "launch.json"),
                                       ("marker", "marker.txt")):
                    (out / filename).write_bytes(extract(lines, case, name))
                shutil.copy2(args.screenshot, out / "guest-desktop.png")
            except (ValueError, OSError) as exc:
                receipts_ok = False
                (out / "error.txt").write_text("incomplete_guest_receipt:" + str(exc)[:180])
        else:
            receipts_ok = False
            candidates = [x for x in lines if x.startswith((
                "VENVWIN_WINE_GUEST_BLOCKER=", "VENVWIN_WINE_GUEST_INSTALL_FAILED=",
                "VENVWIN_WINE_GUEST_LAUNCH_FAILED=", "VENVWIN_WINE_GUEST_APP_MISSING="))]
            note = candidates[-1] if candidates else "guest_wine_case_unverified"
            if not boot: note = "guest_boot_witness_absent"
            if not screenshot: note = "guest_screenshot_absent"
            (out / "error.txt").write_text(note[:220])
        item = dict(schema=SCHEMA, scope="puppy-guest", case=case,
                    fingerprint=fingerprint, source_sha=os.environ["GITHUB_SHA"],
                    run_id=os.environ["GITHUB_RUN_ID"],
                    observed_at=datetime.now(timezone.utc).isoformat(),
                    serial_sha=file_hash(out / "guest-serial.log"))
        if receipts_ok:
            for key, filename in (("install_sha","install.json"), ("launch_sha","launch.json"),
                                  ("marker_sha","marker.txt")):
                item[key] = file_hash(out / filename)
        else:
            item["error_sha"] = file_hash(out / "error.txt")
        (out / "receipt.json").write_text(json.dumps(item, indent=2, sort_keys=True) + "\n")
        with Memory(args.db) as mem:
            observed = mem.record(out / "receipt.json")
            print("REAL_GUEST_BEAN_RECEIPT", case, json.dumps(observed, sort_keys=True), flush=True)
            if observed["state"] != "passed":
                any_failed = True
    if any_failed:
        print("GUEST_WINDOWS_EXECUTION_UNVERIFIED_OR_FAILED", flush=True)
        return 1
    print("BOTH_WINDOWS_INSTALLERS_VERIFIED_IN_REAL_PUPPY_GUEST_NOT_FULL_OS_READINESS", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
