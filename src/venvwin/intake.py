"""Actual EXE/MSI intake: detect real install targets and create working shortcuts.

An installer exit code alone is not evidence that an application will launch.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .capsule import Capsule, capsule_dir, save_capsule, utc_now
from .runner import get_runner, require_command_runner

_SKIP_EXE = ("unins", "uninstall", "setup", "install", "update", "repair",
             "crashreport", "vc_redist", "redist", "regsvr32")


def discover_application_exes(prefix_path: str, limit: int = 24) -> list[Path]:
    """Only actual installed application directories, never Windows system EXEs."""
    drive_c = Path(prefix_path) / "drive_c"
    found: list[Path] = []
    for dirname in ("Program Files", "Program Files (x86)"):
        home = drive_c / dirname
        if not home.is_dir():
            continue
        for candidate in sorted(home.rglob("*")):
            if not candidate.is_file() or candidate.suffix.lower() != ".exe":
                continue
            if candidate.name.lower().startswith(_SKIP_EXE):
                continue
            if any(part.lower() in {"common files", "windows", "microsoft shared"}
                   for part in candidate.parts):
                continue
            found.append(candidate)
            if len(found) >= limit:
                return found
    return found


def _desktop_quote(value: str) -> str:
    # Desktop Entry Specification: double quotes plus reserved-character escapes.
    # Double % to avoid expanding placeholders in arbitrary Windows filenames.
    value = value.replace("%", "%%")
    for char in ("\\", '"', "$", "`"):
        value = value.replace(char, "\\" + char)
    return '"' + value.replace("\n", " ") + '"'


def create_application_shortcut(capsules_root: Path, capsule: Capsule,
                                executable: Path, desktop_dir: Path | None = None) -> Path:
    from .desktop import desktop_file_name

    output = desktop_dir or (Path.home() / "Desktop")
    output.mkdir(parents=True, exist_ok=True)
    path = output / desktop_file_name(capsule.app_name)
    runtime_root = capsules_root.parent
    cmd = " ".join((
        "venvwin", "--root", _desktop_quote(str(runtime_root)),
        "run", _desktop_quote(capsule.capsule_id), _desktop_quote(str(executable))
    ))
    label = capsule.app_name.replace("\n", " ").replace("\r", " ")
    content = (
        "[Desktop Entry]\nType=Application\nVersion=1.0\n"
        f"Name={label}\nComment=Launch via isolated venvWin capsule\n"
        f"Exec={cmd}\nTerminal=false\nIcon=applications-other\n"
        "Categories=Utility;\n"
    )
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    record = {"name": capsule.app_name, "executable_path": str(executable),
              "desktop_file": str(path), "source": "verified-intake-target",
              "created_at": utc_now()}
    if not any(x.get("executable_path") == str(executable) for x in capsule.launchers):
        capsule.launchers.append(record)
    save_capsule(capsules_root, capsule)
    return path


def launch_from_capsule(capsules_root: Path, capsule: Capsule,
                        executable: Path, *, dry_run: bool = False) -> dict[str, Any]:
    if not executable.is_file():
        raise FileNotFoundError(f"Windows app executable not found: {executable}")
    command = get_runner(capsule.profile.runner).prepare_launch(capsule, str(executable))
    if dry_run:
        return {"capsule_id": capsule.capsule_id, "action": "run",
                "dry_run": True, "command": command.args, "env": command.env,
                "exit_code": None}
    require_command_runner(command)
    env = os.environ.copy()
    env.update(command.env)
    result = subprocess.run(command.args, env=env, check=False)
    return {"capsule_id": capsule.capsule_id, "action": "run",
            "dry_run": False, "command": command.args, "env": command.env,
            "exit_code": result.returncode,
            "status": "windows_binary_executed" if result.returncode == 0 else "failed"}
