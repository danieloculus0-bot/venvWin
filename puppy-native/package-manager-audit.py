#!/usr/bin/env python3
"""Verify native Puppy package-manager stack in ORIGINAL split SquashFS layers.

Source inventory only; a functioning Synaptic/APT transaction and DB persistence
require a real graphical Puppy guest, network access, writable save and reboot.
Never run apt/dpkg inside a host masquerading as the Puppy guest.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

REQUIRED_TOOLS = {
    "apt_binary": ["usr/bin/apt", "usr/bin/apt-get"],
    "dependency_resolver": ["usr/bin/apt-cache"],
    "dpkg_binary": ["usr/bin/dpkg", "usr/bin/dpkg-query"],
    "synaptic_gui": ["usr/sbin/synaptic", "usr/bin/synaptic-pkexec",
                     "usr/share/applications/synaptic.desktop"],
    "puppy_pet_gui": ["usr/local/petget/pkg_chooser.sh",
                      "usr/share/applications/Puppy-package-manager.desktop"],
    "sfs_gui": ["usr/share/applications/SFS-Load.desktop"],
}
PACKAGE_DATA = {
    "dpkg_status": "var/lib/dpkg/status",
    "dpkg_available": "var/lib/dpkg/available",
    "apt_sources": "etc/apt/sources.list",
    "apt_sources_d": "etc/apt/sources.list.d/",
    "apt_lists": "var/lib/apt/lists/",
    "puppy_database": "root/.packages/",
    "puppy_metadata": "var/local/petget/",
    "python_sqlite3": "usr/lib/python3.11/sqlite3/__init__.py",
    "sqlite3_binary": "usr/bin/sqlite3",
    "sqlite3_python_dynamic_extension": "usr/lib/python3.11/lib-dynload/_sqlite3.cpython-311-x86_64-linux-gnu.so",
    "petget_binary": "usr/local/petget/pkg_chooser.sh",
    "sfs_loader_script": "usr/sbin/sfs_load",
    "apt_frontend_gdebi": "usr/share/applications/gdebi.desktop",
}

def extract_index(layer: Path) -> set[str]:
    result = subprocess.run(["unsquashfs", "-ll", str(layer)], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    paths = set()
    for line in result.stdout.splitlines():
        if "squashfs-root/" in line:
            rel = line.partition("squashfs-root/")[2].split(" -> ",1)[0].strip()
            if rel: paths.add(rel)
    return paths

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("extracted_iso",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    layers=sorted(args.extracted_iso.glob("*.sfs"))
    if not layers or not any(x.name=="puppy_dpupbw64_10.0.12.sfs" for x in layers):
        raise SystemExit("PACKAGE_AUDIT_WRONG_OR_MISSING_PUPPY_SYSTEM")
    allpaths = {layer.name:extract_index(layer) for layer in layers}
    def found(paths):
        return {path:[layer for layer,items in allpaths.items() if path in items]
                for path in paths}
    # Check original dpkg package records for app binaries we intend to strip.
    # The package DB belongs to the bdrv, which must remain unmodified.
    tracked_trim_apps = ("deadbeef", "mhwaveedit", "easytag", "qwinff",
        "simplescreenrecorder", "celluloid", "hexalate", "iqpuzzle",
        "picpuz", "rubix", "simsu")
    tracked_status = {}
    db_layers=[layer for layer in layers
               if "var/lib/dpkg/status" in allpaths[layer.name]]
    if db_layers:
        z=subprocess.run(["unsquashfs","-cat",str(db_layers[0]),
                          "var/lib/dpkg/status"],
                          text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,check=True)
        for entry in z.stdout.split("\\n\\n"):
            values={}
            for line in entry.splitlines():
                if line.startswith("Package: "): values["name"]=line[9:].strip()
                elif line.startswith("Status: "): values["status"]=line[8:].strip()
            if values.get("name") in tracked_trim_apps:
                tracked_status[values["name"]]=values.get("status","UNKNOWN")
    required={name:found(paths) for name,paths in REQUIRED_TOOLS.items()}
    metadata={name:found([path]) if not path.endswith("/") else {
            path:[layer for layer,items in allpaths.items()
                  if any(item.startswith(path) for item in items)]}
            for name,path in PACKAGE_DATA.items()}
    report={
        "schema":"venvwin.puppy1012.native_package_stack.v1",
        "source":"verified upstream BookwormPup64 10.0.12 ISO SFS inventory",
        "evidence_level":"file-presence-NOT-GUI-install-or-persistent-database-proof",
        "required_software":required,
        "package_db_and_optional_tools":metadata,
        "installed_dpkg_status_for_proposed_trim_apps":tracked_status,
        "dpkg_owners_of_removed_files":"NOT_CHECKED_REQUIRES_INFO_LISTS",
        "Wine_impact":"NO_BASE_SFS_MODIFICATION_THIS_AUDIT",
        "gui_installation_test":"NOT_TESTED",
        "dependency_resolution_test":"NOT_TESTED",
        "package_database_write_and_readback":"NOT_TESTED",
        "package_database_persistence_after_reboot":"NOT_TESTED",
        "sqlite_runtime_test":"NOT_TESTED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    for name,paths in required.items():
        hits=sum(bool(locations) for locations in paths.values())
        print(f"PACKAGE_STACK {name} FOUND={hits}/{len(paths)}")
        for path,locations in paths.items():
            print("  ",path,locations or "NOT_IN_ORIGINAL_SFS")
    print("DPKG_REGISTERED_TRIM_CANDIDATES",tracked_status)
    for name,paths in metadata.items():
        print(f"PACKAGE_DB {name} "+repr(paths))
    print("PACKAGE_STACK_SOURCE_INVENTORY_ONLY_NOT_INSTALL_TEST")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
