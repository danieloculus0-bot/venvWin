from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .persistence import persistence_report


PUBLIC_PRODUCT_NAME = "venvWin Portable"
INTERNAL_CODENAME = "WinUx"
QUICK_START_NAME = "venvWin-Quick-Start.txt"
FIRST_BOOT_PROOF_NAME = "venvWin-First-Boot-Proof.txt"
DASHBOARD_NAME = "venvWin-Dashboard.txt"
FIRST_BOOT_CHECKLIST_NAME = "venvWin-First-Boot-Checklist.txt"
DOCTOR_NAME = "venvwin-doctor.txt"
STORAGE_MARKER_NAME = ".winux-capsule-store"
STORAGE_SOURCE_MARKER_NAME = ".winux-capsule-store-source"
PERSISTENCE_REPORT_NAME = ".winux-persistence-report.json"
DASHBOARD_URL = "http://127.0.0.1:8787"


def first_run_summary(home: Path | None = None) -> dict[str, Any]:
    user_home = home or Path.home()
    report = persistence_report(user_home)
    chosen = report["chosen"]

    if report["leave_no_trace"]:
        storage_status = "leave-no-trace-ok"
        storage_message = "Writing to venvWin Portable storage. Host machine stays clean."
    elif report["disposable_warning"]:
        storage_status = "disposable-warning"
        storage_message = "No durable venvWin-owned persistent storage found. This may be disposable. Fine for testing, terrible for keeping your work."
    elif report["host_write_warning"]:
        storage_status = "host-risk-warning"
        storage_message = "Selected storage may be a host path. Use only if you chose that on purpose."
    else:
        storage_status = "unknown-warning"
        storage_message = "Storage status is unclear. Inspect before trusting this little bastard."

    return {
        "product_name": PUBLIC_PRODUCT_NAME,
        "internal_codename": INTERNAL_CODENAME,
        "capsule_store": chosen["path"],
        "storage_source": chosen["source"],
        "writable": chosen["writable"],
        "portable_owned": chosen["portable_owned"],
        "host_risk": chosen["host_risk"],
        "leave_no_trace": report["leave_no_trace"],
        "storage_status": storage_status,
        "storage_message": storage_message,
        "dashboard_url": DASHBOARD_URL,
        "persistence": report,
    }


def quick_start_text(summary: dict[str, Any], capsule_store: Path) -> str:
    return f"""Welcome to {PUBLIC_PRODUCT_NAME}.

Default rule:

  Write only to the venvWin Portable USB/install drive. Leave the host machine alone.

Storage status:

  {summary['storage_message']}

Capsules live here:

  {capsule_store}

Storage source:

  {summary['storage_source']}

Dashboard:

  {summary['dashboard_url']}

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

Internal codename:

  {INTERNAL_CODENAME}
"""


def dashboard_text(summary: dict[str, Any]) -> str:
    return f"""{PUBLIC_PRODUCT_NAME} Dashboard

Local dashboard:

  {summary['dashboard_url']}

Default behavior:

  Local-only dashboard on this venvWin Portable session.

Phone/LAN behavior:

  Use LAN mode only when intentionally started. LAN dashboard access requires a token.

Useful endpoints:

  {summary['dashboard_url']}/api/status
  {summary['dashboard_url']}/api/doctor

What it shows:

- capsule storage path
- storage source
- leave-no-trace state
- host write risk
- capsule list
- doctor status
- first-run state

If the dashboard is not available, run:

  winux-dashboard
"""


def checklist_text(summary: dict[str, Any], capsule_store: Path) -> str:
    return f"""{PUBLIC_PRODUCT_NAME} First Boot Checklist

Use this checklist before calling an ISO flash-ready.

[ ] Desktop loaded
[ ] venvWin First Boot GUI opened
[ ] venvWin Dashboard opens at {summary['dashboard_url']}
[ ] Capsule storage path is visible
[ ] Capsule storage source is visible: {summary['storage_source']}
[ ] Capsule storage path exists: {capsule_store}
[ ] Leave-no-trace status is visible
[ ] Host-risk status is visible
[ ] Quick Start file exists
[ ] First Boot Proof file exists
[ ] Dashboard info file exists
[ ] Storage marker exists: ~/{STORAGE_MARKER_NAME}
[ ] Storage source marker exists: ~/{STORAGE_SOURCE_MARKER_NAME}
[ ] Persistence report exists: ~/{PERSISTENCE_REPORT_NAME}
[ ] venvwin storage runs
[ ] venvwin doctor runs
[ ] EXE/MSI association setup ran or logged failure visibly
[ ] Dummy EXE dry-run routes through venvwin open

Current first-run summary:

product={PUBLIC_PRODUCT_NAME}
internal_codename={INTERNAL_CODENAME}
status={summary['storage_status']}
storage_message={summary['storage_message']}
capsule_store={capsule_store}
storage_source={summary['storage_source']}
writable={summary['writable']}
portable_owned={summary['portable_owned']}
host_risk={summary['host_risk']}
leave_no_trace={summary['leave_no_trace']}
dashboard_url={summary['dashboard_url']}
"""


def first_boot_proof_text(summary: dict[str, Any], capsule_store: Path) -> str:
    return f"""{PUBLIC_PRODUCT_NAME} First Boot Proof

This file is created by first-run setup so an alpha boot can be verified without guessing.

product={PUBLIC_PRODUCT_NAME}
internal_codename={INTERNAL_CODENAME}
engine=venvWin
status={summary['storage_status']}
storage_message={summary['storage_message']}
capsule_store={capsule_store}
storage_source={summary['storage_source']}
writable={summary['writable']}
portable_owned={summary['portable_owned']}
host_risk={summary['host_risk']}
leave_no_trace={summary['leave_no_trace']}
dashboard_url={summary['dashboard_url']}

Expected desktop proof files:

- {QUICK_START_NAME}
- {FIRST_BOOT_PROOF_NAME}
- {DASHBOARD_NAME}
- {FIRST_BOOT_CHECKLIST_NAME}
- {DOCTOR_NAME}

Expected hidden home proof files:

- {STORAGE_MARKER_NAME}
- {STORAGE_SOURCE_MARKER_NAME}
- {PERSISTENCE_REPORT_NAME}

Alpha boot acceptance:

- desktop loads
- first-run setup creates this file
- dashboard opens at {summary['dashboard_url']}
- capsule store is writable
- storage source is visible
- storage risk is visible
- venvwin doctor output exists
"""


def write_first_run_files(home: Path | None = None) -> dict[str, Any]:
    user_home = home or Path.home()
    desktop = user_home / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)

    summary = first_run_summary(user_home)
    capsule_store = Path(summary["capsule_store"])
    capsule_store.mkdir(parents=True, exist_ok=True)

    (user_home / STORAGE_MARKER_NAME).write_text(str(capsule_store), encoding="utf-8")
    (user_home / STORAGE_SOURCE_MARKER_NAME).write_text(str(summary["storage_source"]), encoding="utf-8")
    (user_home / PERSISTENCE_REPORT_NAME).write_text(json.dumps(summary["persistence"], indent=2), encoding="utf-8")
    (desktop / QUICK_START_NAME).write_text(quick_start_text(summary, capsule_store), encoding="utf-8")
    (desktop / FIRST_BOOT_PROOF_NAME).write_text(first_boot_proof_text(summary, capsule_store), encoding="utf-8")
    (desktop / DASHBOARD_NAME).write_text(dashboard_text(summary), encoding="utf-8")
    (desktop / FIRST_BOOT_CHECKLIST_NAME).write_text(checklist_text(summary, capsule_store), encoding="utf-8")
    return summary


def wizard_text(home: Path | None = None) -> str:
    summary = first_run_summary(home)
    chosen = summary["capsule_store"]
    lines = [
        f"{PUBLIC_PRODUCT_NAME} First Run",
        "",
        "Where should Windows app state live?",
        "",
        f"Recommended: {chosen}",
        f"Storage source: {summary['storage_source']}",
        f"Status: {summary['storage_status']}",
        f"Message: {summary['storage_message']}",
        f"Dashboard: {summary['dashboard_url']}",
        "",
        "Default policy: write to the venvWin Portable USB/install drive and leave the host machine alone.",
        "",
        "Options planned for GUI:",
        "  1. Use venvWin Portable USB storage, recommended",
        "  2. Disposable test session",
        "  3. Advanced location, explicit host-risk warning",
    ]
    return "\n".join(lines)
