from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .persistence import persistence_report


QUICK_START_NAME = "WinUx-Quick-Start.txt"
DOCTOR_NAME = "venvwin-doctor.txt"
STORAGE_MARKER_NAME = ".winux-capsule-store"
PERSISTENCE_REPORT_NAME = ".winux-persistence-report.json"


def first_run_summary(home: Path | None = None) -> dict[str, Any]:
    user_home = home or Path.home()
    report = persistence_report(user_home)
    chosen = report["chosen"]

    if report["leave_no_trace"]:
        storage_status = "leave-no-trace-ok"
        storage_message = "Writing to WinUx-owned portable storage. Host machine stays clean."
    elif report["disposable_warning"]:
        storage_status = "disposable-warning"
        storage_message = "No WinUx-owned persistent storage found. This may be disposable. Fine for testing, terrible for keeping your work."
    elif report["host_write_warning"]:
        storage_status = "host-risk-warning"
        storage_message = "Selected storage may be a host path. Use only if you chose that on purpose."
    else:
        storage_status = "unknown-warning"
        storage_message = "Storage status is unclear. Inspect before trusting this little bastard."

    return {
        "capsule_store": chosen["path"],
        "storage_source": chosen["source"],
        "writable": chosen["writable"],
        "portable_owned": chosen["portable_owned"],
        "host_risk": chosen["host_risk"],
        "leave_no_trace": report["leave_no_trace"],
        "storage_status": storage_status,
        "storage_message": storage_message,
        "persistence": report,
    }


def write_first_run_files(home: Path | None = None) -> dict[str, Any]:
    user_home = home or Path.home()
    desktop = user_home / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)

    summary = first_run_summary(user_home)
    capsule_store = Path(summary["capsule_store"])
    capsule_store.mkdir(parents=True, exist_ok=True)

    (user_home / STORAGE_MARKER_NAME).write_text(str(capsule_store), encoding="utf-8")
    (user_home / PERSISTENCE_REPORT_NAME).write_text(json.dumps(summary["persistence"], indent=2), encoding="utf-8")

    quick_start = f"""Welcome to WinUx Portable.

Default rule:

  Write only to the WinUx USB/install drive. Leave the host machine alone.

Storage status:

  {summary['storage_message']}

Capsules live here:

  {capsule_store}

Double-click a Windows EXE/MSI, or run:

  venvwin open /path/to/app.exe

Run health check:

  venvwin doctor

Show storage status:

  venvwin storage

Private browser:

  winux-private-browser

If Windows files are being bullshit, run:

  venvwin associate
"""
    (desktop / QUICK_START_NAME).write_text(quick_start, encoding="utf-8")
    return summary


def wizard_text(home: Path | None = None) -> str:
    summary = first_run_summary(home)
    chosen = summary["capsule_store"]
    lines = [
        "WinUx First Run",
        "",
        "Where should Windows app state live?",
        "",
        f"Recommended: {chosen}",
        f"Status: {summary['storage_status']}",
        f"Message: {summary['storage_message']}",
        "",
        "Default policy: write to the WinUx USB/install drive and leave the host machine alone.",
        "",
        "Options planned for GUI:",
        "  1. Use WinUx USB storage, recommended",
        "  2. Disposable test session",
        "  3. Advanced location, explicit host-risk warning",
    ]
    return "\n".join(lines)
