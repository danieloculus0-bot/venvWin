from __future__ import annotations

from pathlib import Path

from .capsule import Capsule, capsule_dir, save_capsule, utc_now
from .runner import get_runner


def escape_desktop_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", " ")


def desktop_file_name(name: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return f"{safe or 'app'}.desktop"


def generate_desktop_launcher(
    capsules_root: Path,
    capsule: Capsule,
    name: str,
    executable_path: str,
    output_dir: Path | None = None,
) -> Path:
    command = get_runner(capsule.profile.runner).prepare_launch(capsule, executable_path)
    env_prefix = " ".join(f'{key}="{value}"' for key, value in command.env.items())
    exec_line = f"env {env_prefix} {' '.join(command.args)}".strip()

    target_dir = output_dir or (capsule_dir(capsules_root, capsule.capsule_id) / "launchers")
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / desktop_file_name(name)

    content = f"""[Desktop Entry]
Type=Application
Name={escape_desktop_value(name)}
Comment=Launch {escape_desktop_value(capsule.app_name)} through venvWin
Exec={exec_line}
Terminal=false
Categories=Utility;
"""
    path.write_text(content, encoding="utf-8")

    capsule.launchers.append(
        {
            "name": name,
            "executable_path": executable_path,
            "desktop_file": str(path),
            "created_at": utc_now(),
        }
    )
    save_capsule(capsules_root, capsule)
    return path
