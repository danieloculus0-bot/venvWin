from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .associate import default_applications_dir
from .capsule import list_capsules
from .paths import capsules_dir, profiles_dir
from .persistence import persistence_report


@dataclass(slots=True)
class HealthCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }


def check_path_exists(name: str, path: Path, required: bool = True) -> HealthCheck:
    if path.exists():
        return HealthCheck(name, "ok", f"Found: {path}")
    status = "error" if required else "warn"
    return HealthCheck(name, status, f"Missing: {path}. Not fatal yet, but this little goblin needs a home.")


def runner_status(runner: str = "wine") -> HealthCheck:
    found = shutil.which(runner)
    if found:
        return HealthCheck("runner", "ok", f"Found {runner}: {found}")
    return HealthCheck(
        "runner",
        "warn",
        f"Runner not found on PATH: {runner}. venvWin can manage capsules, but Windows apps will not launch until the runner exists. Plumbing yes, engine no.",
    )


def privacy_browser_status() -> HealthCheck:
    tor_browser_launcher = shutil.which("torbrowser-launcher")
    tor_browser = shutil.which("tor-browser")
    torsocks = shutil.which("torsocks")
    firefox = shutil.which("firefox-esr") or shutil.which("firefox")
    tor = shutil.which("tor")

    if tor_browser_launcher:
        return HealthCheck("privacy-browser", "ok", f"Tor Browser Launcher found: {tor_browser_launcher}")
    if tor_browser:
        return HealthCheck("privacy-browser", "ok", f"Tor Browser found: {tor_browser}")
    if tor and torsocks and firefox:
        return HealthCheck(
            "privacy-browser",
            "warn",
            "Tor Browser missing, but torsocks + Firefox fallback exists. Useful for testing, not hardened anonymity. Calling that anonymous would be bullshit.",
        )
    return HealthCheck(
        "privacy-browser",
        "warn",
        "Tor privacy browser path is missing. Install Tor Browser/torbrowser-launcher for real private browser mode.",
    )


def association_status(applications_dir: Path) -> HealthCheck:
    exe = applications_dir / "venvwin-open-exe.desktop"
    msi = applications_dir / "venvwin-open-msi.desktop"
    if exe.exists() and msi.exists():
        return HealthCheck("file-associations", "ok", f"EXE/MSI handlers found in {applications_dir}")
    return HealthCheck(
        "file-associations",
        "warn",
        "EXE/MSI handlers are missing. Run `venvwin associate` so double-clicking Windows files stops being bullshit.",
    )


def persistence_status(root: Path) -> HealthCheck:
    report = persistence_report()
    chosen = report["chosen"]
    if os.environ.get("VENVWIN_HOME"):
        return HealthCheck("persistence", "ok", f"VENVWIN_HOME is set: {os.environ['VENVWIN_HOME']}")
    if chosen["writable"] and chosen["source"] != "home-fallback":
        return HealthCheck("persistence", "ok", f"Persistent capsule store found: {chosen['path']}")
    return HealthCheck(
        "persistence",
        "warn",
        f"No dedicated persistent capsule store found. Using default root: {root}. Fine for testing, sketchy for venvWin Portable. Disposable-session goblin risk is active.",
    )


def capsule_count_status(root: Path) -> HealthCheck:
    found = list_capsules(capsules_dir(root))
    if found:
        return HealthCheck("capsules", "ok", f"Capsules found: {len(found)}")
    return HealthCheck("capsules", "ok", "Capsules found: 0. Empty cave, no disasters yet.")


def health_report(root: Path, applications_dir: Path | None = None) -> dict[str, Any]:
    apps_dir = applications_dir or default_applications_dir()
    persist = persistence_report()
    checks = [
        check_path_exists("runtime-root", root, required=False),
        check_path_exists("profiles-dir", profiles_dir(root), required=False),
        check_path_exists("capsules-dir", capsules_dir(root), required=False),
        runner_status("wine"),
        privacy_browser_status(),
        association_status(apps_dir),
        persistence_status(root),
        capsule_count_status(root),
    ]

    status_order = {"error": 3, "warn": 2, "ok": 1}
    worst = max(checks, key=lambda check: status_order[check.status]).status if checks else "ok"

    return {
        "overall": worst,
        "root": str(root),
        "applications_dir": str(apps_dir),
        "persistence": persist,
        "checks": [check.to_dict() for check in checks],
    }
