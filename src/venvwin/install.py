from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .capsule import Capsule, capsule_dir, save_capsule, utc_now
from .runner import get_runner, require_command_runner


def record_installer(
    capsules_root: Path,
    capsule: Capsule,
    installer_path: Path,
    *,
    copy_installer: bool = True,
) -> dict[str, Any]:
    if not installer_path.exists():
        raise FileNotFoundError(f"Installer not found: {installer_path}")
    if not installer_path.is_file():
        raise ValueError(f"Installer path is not a file: {installer_path}")

    stored_path: str | None = None
    if copy_installer:
        target_dir = capsule_dir(capsules_root, capsule.capsule_id) / "installers"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / installer_path.name
        shutil.copy2(installer_path, target)
        stored_path = str(target)

    record = {
        "source_path": str(installer_path),
        "stored_path": stored_path,
        "recorded_at": utc_now(),
    }
    capsule.installers.append(record)
    save_capsule(capsules_root, capsule)
    return record


def install_into_capsule(
    capsules_root: Path,
    capsule: Capsule,
    installer_path: Path,
    *,
    dry_run: bool = False,
    copy_installer: bool = True,
) -> dict[str, Any]:
    command = get_runner(capsule.profile.runner).prepare_install(capsule, str(installer_path))

    if not dry_run:
        require_command_runner(command)

    record = record_installer(
        capsules_root,
        capsule,
        installer_path,
        copy_installer=copy_installer,
    )

    install_record = {
        **record,
        "command": command.args,
        "env": command.env,
        "dry_run": dry_run,
        "runner_available": dry_run or True,
        "exit_code": None,
        "completed_at": None,
    }

    if dry_run:
        capsule.installers[-1] = install_record
        save_capsule(capsules_root, capsule)
        return install_record

    env = os.environ.copy()
    env.update(command.env)
    completed = subprocess.run(command.args, env=env, check=False)

    install_record["exit_code"] = completed.returncode
    install_record["completed_at"] = utc_now()
    capsule.installers[-1] = install_record
    save_capsule(capsules_root, capsule)
    return install_record
