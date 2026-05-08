from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .capsule import Capsule, create_capsule, load_capsule, save_capsule, slugify_app_name, utc_now
from .install import install_into_capsule
from .profile import RunnerProfile, load_profile
from .runner import get_runner

WINDOWS_SUFFIXES = {".msi", ".msix", ".exe"}
INSTALLER_NAME_HINTS = {
    "install",
    "installer",
    "setup",
    "setup64",
    "setup32",
    "update",
    "updater",
    "bootstrap",
    "bootstrapper",
}


def app_name_from_path(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip() or "Windows App"


def classify_windows_file(path: Path) -> str:
    suffix = path.suffix.lower()
    stem = path.stem.lower()

    if suffix in {".msi", ".msix"}:
        return "installer"
    if suffix == ".exe" and any(hint in stem for hint in INSTALLER_NAME_HINTS):
        return "installer"
    if suffix == ".exe":
        return "portable-exe"
    raise ValueError(f"Unsupported Windows file type: {suffix}")


def get_or_create_capsule_for_file(
    capsules_root: Path,
    profiles_root: Path,
    file_path: Path,
    profile_name: str = "default",
) -> Capsule:
    app_name = app_name_from_path(file_path)
    capsule_id = slugify_app_name(app_name)
    try:
        return load_capsule(capsules_root, capsule_id)
    except FileNotFoundError:
        profile: RunnerProfile = load_profile(profiles_root, profile_name)
        return create_capsule(capsules_root, app_name, profile)


def open_windows_file(
    capsules_root: Path,
    profiles_root: Path,
    file_path: Path,
    *,
    dry_run: bool = False,
    profile_name: str = "default",
) -> dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    file_type = classify_windows_file(file_path)
    capsule = get_or_create_capsule_for_file(capsules_root, profiles_root, file_path, profile_name)

    if file_type == "installer":
        result = install_into_capsule(capsules_root, capsule, file_path, dry_run=dry_run)
        result["action"] = "install"
        result["file_type"] = file_type
        return result

    command = get_runner(capsule.profile.runner).prepare_launch(capsule, str(file_path))
    result: dict[str, Any] = {
        "action": "open",
        "file_type": file_type,
        "capsule_id": capsule.capsule_id,
        "file_path": str(file_path),
        "command": command.args,
        "env": command.env,
        "dry_run": dry_run,
        "exit_code": None,
        "completed_at": None,
    }

    capsule.launchers.append(
        {
            "name": app_name_from_path(file_path),
            "executable_path": str(file_path),
            "opened_at": utc_now(),
            "source": "double-click-open",
        }
    )
    save_capsule(capsules_root, capsule)

    if dry_run:
        return result

    env = os.environ.copy()
    env.update(command.env)
    completed = subprocess.run(command.args, env=env, check=False)
    result["exit_code"] = completed.returncode
    result["completed_at"] = utc_now()
    return result
