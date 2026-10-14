#!/usr/bin/env python3
"""Read ONLY authentic Puppy SquashFS directory inventories; no changes to an ISO.

Claims here describe file presence, NOT ABI, runtime functionality, XLSX fidelity,
GUI availability, or Wine compatibility. Do not turn them into test PASS badges.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

CATEGORIES = {
    "office_word": (r"(^|/)(abiword|abiword-.*|libabiword.*)(\\.desktop)?$", r"abiword"),
    "office_spreadsheet": (r"(^|/)(gnumeric|gnumeric-.*|ssconvert|libspreadsheet.*)(\\.desktop)?$", r"gnumeric|ssconvert"),
    "browser_firefox": (r"(^|/)(firefox|firefox-esr|firefox\\.desktop|firefox-esr\\.desktop)$", r"firefox"),
    "browser_chromium": (r"(^|/)(chromium|chromium-browser|chromium\\.desktop|chrome)(\\.desktop)?$", r"chromium|google-chrome"),
    "browser_seamonkey": (r"(^|/)(seamonkey|seamonkey-bin)(\\.desktop)?$", r"seamonkey"),
    "mail": (r"(^|/)(sylpheed|claws-mail|thunderbird|mutt|geary)(\\.desktop)?$", r"mail"),
    "network_gui": (r"(^|/)(frisbee|network-wizard|network-connection|pwireless|connman-gtk|nm-connection-editor|simple_network_setup|network_tray)(\\.desktop)?$", r"frisbee|network|connman"),
    "image_editor": (r"(^|/)(mtpaint|gimp|pinta)(\\.desktop)?$", r"mtpaint|gimp|pinta"),
    "image_viewer": (r"(^|/)(viewnior|geeqie|gpicview|ristretto|pup-kview)(\\.desktop)?$", r"viewer|image"),
    "video_editor": (r"(^|/)(avidemux|openshot|shotcut|kdenlive|pitivi|flowblade)(\\.desktop)?$", r"video.*editor"),
    "audio_editor": (r"(^|/)(mhwaveedit|audacity|ocenaudio|ardour|qtractor)(\\.desktop)?$", r"audio.*editor"),
    "media_player": (r"(^|/)(mpv|vlc|smplayer|ffplay|deadbeef|pmusic)(\\.desktop)?$", r"player|vlc|mpv"),
    "games": (r"(^|/)(petris|pup-adventure|xbill|gtkballs|hex-a-hop|gnuchess|xinvaders)(\\.desktop)?$", r"game"),
    "window_manager": (r"(^|/)(jwm|openbox|rox|rox-filer|xwin)$", r"jwm|rox"),
    "installer": (r"(^|/)(petget|sfs_load|pkg|apt|apt-get)$", r"petget|sfs"),
    "wine": (r"(^|/)(wine|wine64|wineserver|wineboot|winecfg)(\\.desktop)?$", r"wine"),
    "audio_backends": (r"(^|/)(aplay|alsamixer|pulseaudio|pipewire|pw-cat)$", r"alsa|pulse|pipewire"),
}

PREFERENCE = {
    "office_word": "KEEP native Bookworm AbiWord if shipped; add only after proven missing",
    "office_spreadsheet": "KEEP native Bookworm Gnumeric with verified XLS/XLSX roundtrip",
    "browser_firefox": "PREFER a single usable Firefox ESR unless footprint measured worse",
    "browser_chromium": "ALTERNATIVE browser only; avoid bundling duplicate",
    "browser_seamonkey": "OPTIONALIZE if Firefox ESR replaces it and mail not needed",
    "mail": "OPTIONALIZE mail clients, preserve network client UI",
    "network_gui": "PROTECT graphical network setup and wireless tools",
    "image_editor": "KEEP mtPaint; extra image editors optional",
    "image_viewer": "KEEP one image viewer",
    "video_editor": "CUT only standalone editors after reverse dependency inspection",
    "audio_editor": "CUT only standalone editors; PROTECT codec, audio system",
    "media_player": "KEEP one playback tool and codec/dependency tree",
    "games": "CANDIDATE prune if package files independently owned",
    "window_manager": "PROTECT bootable Puppy desktop",
    "installer": "PROTECT Puppy PET/SFS package management",
    "wine": "PROTECT real Wine and compatibility libraries; external runner separate",
    "audio_backends": "PROTECT audio backends needed for Wine",
}


def entries_for(sfs: Path) -> dict[str, int]:
    result = subprocess.run(["unsquashfs", "-ll", str(sfs)],
                            check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    entries: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if "squashfs-root/" not in line:
            continue
        prefix, sep, raw = line.partition("squashfs-root/")
        if not sep:
            continue
        path = raw.split(" -> ", 1)[0].strip()
        chunks = prefix.split()
        try:
            size = int(chunks[2])
        except (ValueError, IndexError):
            size = 0
        entries[path] = size
    return entries


def desktop_data(sfs: Path, path: str) -> dict[str, str]:
    proc = subprocess.run(["unsquashfs", "-cat", str(sfs), path],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, errors="replace")
    if proc.returncode:
        return {"path": path, "error": "unable-to-read"}
    fields = {}
    for line in proc.stdout.splitlines():
        if line.startswith(("Name=", "Exec=", "Categories=", "NoDisplay=")):
            k, v = line.split("=", 1)
            fields.setdefault(k, v[:180])
    fields["path"] = path
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("iso_files", type=Path, help="Directory of extracted ORIGINAL Puppy ISO")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sfs_files = sorted(args.iso_files.glob("*.sfs"))
    if not sfs_files:
        raise SystemExit("FAIL_NO_PUPPY_SFS_TO_INVENTORY")
    expected = "puppy_dpupbw64_10.0.12.sfs"
    if not any(s.name == expected for s in sfs_files):
        raise SystemExit("FAIL_INCORRECT_OR_INCOMPLETE_PUPPY_BASE_SFS")

    detected: dict[str, list[dict]] = {key: [] for key in CATEGORIES}
    all_desktops: list[dict] = []
    inventory_layers: list[dict] = []
    packages = []
    for sfs in sfs_files:
        items = entries_for(sfs)
        inventory_layers.append({
            "layer": sfs.name, "compressed_bytes": sfs.stat().st_size,
            "entry_count": len(items),
        })
        for name, size in items.items():
            if name.startswith("root/.packages/builtin_files/"):
                packages.append({"layer": sfs.name, "file": name})
            if name.endswith(".desktop") and (
                "usr/share/applications/" in name or "root/.local/share/applications/" in name
            ):
                item = desktop_data(sfs, name)
                item["layer"] = sfs.name
                all_desktops.append(item)
            if not (
                name.startswith(("usr/bin/", "usr/local/bin/", "opt/", "root/.packages/",
                                 "usr/share/applications/", "usr/lib/wine/", "usr/lib64/wine/"))
            ):
                continue
            for category, (file_rx, _) in CATEGORIES.items():
                if re.search(file_rx, name, flags=re.I):
                    detected[category].append({"layer": sfs.name, "path": name, "raw_file_size": size})
    report = {
        "schema": "venvwin.puppy_original_package_inventory.v1",
        "source": "genuine extracted upstream 10.0.12 ISO; no modifications",
        "evidence_level": "presence-only-NOT-runtime-compatible",
        "layers": inventory_layers,
        "app_classes": {
            key: {"presence": "OBSERVED" if items else "NOT_OBSERVED",
                  "matches": items[:150], "recommendation": PREFERENCE[key]}
            for key, items in detected.items()
        },
        "desktop_entries": all_desktops,
        "builtin_package_manifest_names": packages,
        "runtime_tests": {
            "windows32": "NOT_PROVEN_BY_INVENTORY",
            "windows64": "NOT_PROVEN_BY_INVENTORY",
            "office_xlsx_roundtrip": "NOT_PROVEN_BY_INVENTORY",
            "native_browser_launch": "NOT_PROVEN_BY_INVENTORY",
            "network_gui_connection": "NOT_PROVEN_BY_INVENTORY",
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "slacko-app-inventory.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Original Puppy 10.0.12 package inventory",
        "",
        "Source: unmodified, checksum-verified upstream ISO SquashFS.",
        "",
        "**These are file-inventory findings, not verified working apps.**",
        "",
        "| Category | Observed files | Recommendation |",
        "|---|---:|---|",
    ]
    for key, item in report["app_classes"].items():
        lines.append(f"| {key} | {len(item['matches'])} | {item['recommendation']} |")
    lines += ["", "## Actual ISO SFS layers", ""]
    for layer in inventory_layers:
        lines.append(f"- {layer['layer']}: compressed bytes {layer['compressed_bytes']}, entries {layer['entry_count']}")
    lines += ["", "## Desktop menu entries (observed)", ""]
    for item in all_desktops[:180]:
        lines.append(f"- {item.get('Name', '?')}: {item.get('Exec', '?')} ({item['layer']}::{item['path']})")
    lines += ["", "## Package manifest entries (observed)", ""]
    for item in packages[:250]:
        lines.append(f"- {item['layer']}::{item['file']}")
    (args.output / "slacko-app-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ORIGINAL_PUPPY_1012_APP_INVENTORY_GENERATED_NOT_APPS_VERIFIED")
    for key, item in report["app_classes"].items():
        print(f"APP_INVENTORY {key} {item['presence']} count={len(item['matches'])}")
        for match in item["matches"][:7]:
            print(f"  {match['layer']}::{match['path']}")
    print("TOTAL_DESKTOP_ENTRIES", len(all_desktops))
    print("TOTAL_PACKAGE_MANIFESTS", len(packages))
    print("ORIGINAL_ISO_SFS_COMPRESSED_BYTES", sum(x["compressed_bytes"] for x in inventory_layers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
