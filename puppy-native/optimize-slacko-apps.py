#!/usr/bin/env python3
"""Conservative, explicit BookwormPup64 main-SFS app trimmer.

This script ONLY modifies an unpacked *test copy* of the main Puppy SFS.
No Linux ABI, shared libraries, graphics stacks, network tools, package manager,
Wine/WoW64 files, browser, office files or other system components are removed.
Do not claim Wine compatible until both PE32/PE32+ run in the guest afterwards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

# Exact known app targets observed in original 10.0.12 image.
# Be deliberately conservative: DO NOT include shared libraries, sound servers,
# codecs, glibc, ffmpeg, X11, Gtk, GStreamer, or OS/module boot components.
REMOVAL_TARGETS = {
    "audio_editor": [
        "usr/bin/mhwaveedit",
        "usr/share/applications/mhwaveedit.desktop",
        "usr/share/mhwaveedit",
        "usr/share/doc/mhwaveedit",
        "usr/share/man/man1/mhwaveedit.1.gz",
    ],
    "duplicate_audio_player": [
        "opt/deadbeef",
        "usr/bin/deadbeef",
        "usr/share/applications/deadbeef.desktop",
        "usr/share/deadbeef",
        "usr/share/doc/deadbeef",
        "usr/share/man/man1/deadbeef.1.gz",
    ],
    "redundant_menu_entry": [
        "usr/share/applications/smplayer_enqueue.desktop",
    ],
}
# Explicitly retain these, including symlinks and their targets.
PROTECTED_BINARIES = [
    "usr/bin/abiword",
    "usr/bin/gnumeric",
    "usr/bin/ssconvert",
    "usr/bin/mtpaint",
    "usr/bin/jwm",
    "usr/local/bin/rox",
    "usr/local/bin/frisbee",
    "usr/bin/connman-gtk",
    "usr/bin/mpv",
    "usr/bin/smplayer",
    "usr/bin/aplay",
    "usr/bin/pipewire",
]
PROTECTED_MENU = [
    "usr/share/applications/abiword.desktop",
    "usr/share/applications/gnumeric.desktop",
    "usr/share/applications/frisbee.desktop",
    "usr/share/applications/mpv.desktop",
    "usr/share/applications/smplayer.desktop",
    "usr/share/applications/mtpaint.desktop",
]
# All removal targets are exact file paths / app-specific directories only.
PROTECTED_PREFIXES = (
    "boot/", "etc/", "lib/", "lib32/", "lib64/", "usr/lib/",
    "usr/lib32/", "usr/lib64/", "usr/local/lib/", "usr/share/alsa/",
    "usr/share/pipewire/", "usr/share/gnumeric/",
    "usr/share/abiword/", "usr/share/applications/abiword",
    "usr/share/applications/gnumeric", "usr/share/applications/frisbee",
    "usr/share/applications/mpv", "usr/share/applications/smplayer.desktop",
    "usr/share/applications/mtpaint", "usr/share/applications/firefox",
    "root/", "opt/FirefoxESR", "usr/share/locale/",
)

def exists_or_link(path: Path) -> bool:
    return path.exists() or path.is_symlink()

def token(path: Path) -> str:
    """Detect mutation of protected resources without following links out of root."""
    if path.is_symlink():
        return "link:" + os.readlink(path)
    if not path.exists():
        return "absent"
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(block)
        return "sha256:" + digest.hexdigest()
    return "directory"

def safe_manifest(root: Path) -> dict[str,str]:
    for name in ("usr/bin/gnumeric", "usr/bin/abiword", "usr/bin/ssconvert",
                 "usr/bin/jwm", "usr/local/bin/rox", "usr/local/bin/frisbee",
                 "usr/bin/connman-gtk", "usr/bin/mpv", "usr/bin/smplayer"):
        if not exists_or_link(root / name):
            raise SystemExit("STOP_MISSING_PROTECTED_COMPONENT:" + name)
    return {rel: token(root / rel) for rel in (PROTECTED_BINARIES + PROTECTED_MENU)}

def stat_targets(root: Path) -> list[dict]:
    planned = []
    for group, targets in REMOVAL_TARGETS.items():
        for rel in targets:
            if rel.startswith(PROTECTED_PREFIXES) or "/../" in rel or rel.startswith("/"):
                raise SystemExit("STOP_TARGET_NOT_APP_SCOPED:" + rel)
            path = root / rel
            if not exists_or_link(path):
                continue
            if path.is_dir() and not path.is_symlink():
                raw_bytes = sum(p.lstat().st_size for p in path.rglob("*") if p.is_file())
                count = sum(1 for p in path.rglob("*") if p.is_file())
            else:
                raw_bytes = path.lstat().st_size
                count = 1
            planned.append({"group": group, "relative_path": rel,
                            "raw_size_bytes": raw_bytes, "file_count": count})
    return planned

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path, help="TEMPORARY root extracted from official puppy_dpupbw64_10.0.12.sfs")
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true",
                   help="Modify temporary extracted copy ONLY; never operates on original SFS")
    args = p.parse_args()
    root = args.root.absolute()
    if root == Path("/") or root == Path.home() or "dist/" not in str(root):
        raise SystemExit("STOP_UNSAFE_OPTIMIZER_ROOT_NOT_TEMP_DIST")
    if not (root / "etc/puppyversion").exists():
        # Original Puppy system includes /etc/puppyversion.
        raise SystemExit("STOP_NOT_IDENTIFIED_AS_PUPPY_MAIN_SFS")
    protected_before = safe_manifest(root)
    planned = stat_targets(root)
    if not planned:
        raise SystemExit("STOP_NO_KNOWN_SAFE_REDUNDANT_APPLICATIONS")
    if args.apply:
        for entry in planned:
            path = root / entry["relative_path"]
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
    protected_after = safe_manifest(root)
    if protected_before != protected_after:
        raise SystemExit("STOP_PROTECTED_COMPONENT_CHANGED_RESTORE_ORIGINAL_SFS")
    report = {
        "schema": "venvwin.slacko_trim.v1",
        "status": "TEST_COPY_MUTATED" if args.apply else "PLAN_ONLY",
        "root": str(root),
        "removed": planned if args.apply else [],
        "candidates": planned,
        "raw_file_bytes_candidate": sum(x["raw_size_bytes"] for x in planned),
        "protected_files_verified_unmodified": len(protected_before),
        "library_or_wine_components_removed": 0,
        "compressed_savings_bytes": "MEASURE_SEPARATELY_AFTER_SFS_RECOMPRESSION",
        "guest_puppy_boot": "NOT_TESTED_BY_THIS_SCRIPT",
        "guest_wine_32_and_64": "NOT_TESTED_BY_THIS_SCRIPT",
        "office_xlsx_roundtrip": "NOT_TESTED_BY_THIS_SCRIPT",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print("SAFE_APP_TRIM_"+("APPLIED_TO_TEST_COPY_NOT_BOOT_PROOF" if args.apply else "PLAN_ONLY_NOT_APPLIED"))
    for entry in planned:
        print("APP_CANDIDATE", entry["group"], entry["relative_path"], entry["raw_size_bytes"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
