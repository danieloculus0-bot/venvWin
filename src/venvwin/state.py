from __future__ import annotations

from pathlib import Path


def default_filesystem_mappings(home: Path | None = None) -> dict[str, str]:
    base = home or Path.home()
    return {
        r"C:\\users\\venvwin\\Desktop": str(base / "Desktop"),
        r"C:\\users\\venvwin\\Documents": str(base / "Documents"),
        r"C:\\users\\venvwin\\Downloads": str(base / "Downloads"),
        r"C:\\users\\venvwin\\Pictures": str(base / "Pictures"),
        r"C:\\users\\venvwin\\Music": str(base / "Music"),
        r"C:\\users\\venvwin\\Videos": str(base / "Videos"),
    }


def default_permission_policy() -> dict[str, object]:
    return {
        "run_as_root": False,
        "allow_system_writes": False,
        "allow_user_home_mappings": True,
        "protect_user_documents_on_reset": True,
        "network_access": "inherit-user-session",
        "notes": "Default venvWin policy uses normal Linux user privileges and keeps app state inside the capsule.",
    }


def ensure_prefix_shape(prefix_path: Path) -> None:
    drive_c = prefix_path / "drive_c"
    user_root = drive_c / "users" / "venvwin"

    for path in (
        drive_c / "Program Files",
        drive_c / "Program Files (x86)",
        drive_c / "windows",
        user_root / "Desktop",
        user_root / "Documents",
        user_root / "Downloads",
        user_root / "Pictures",
        user_root / "Music",
        user_root / "Videos",
        user_root / "AppData" / "Local",
        user_root / "AppData" / "Roaming",
    ):
        path.mkdir(parents=True, exist_ok=True)
