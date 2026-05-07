from __future__ import annotations

import os
from pathlib import Path


def default_root() -> Path:
    """Return the default venvWin data root.

    Uses VENVWIN_HOME when set. Otherwise uses ~/.local/share/venvwin.
    """

    override = os.environ.get("VENVWIN_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".local" / "share" / "venvwin"


def capsules_dir(root: Path) -> Path:
    return root / "capsules"


def profiles_dir(root: Path) -> Path:
    return root / "profiles"


def logs_dir(root: Path) -> Path:
    return root / "logs"


def ensure_runtime_dirs(root: Path) -> None:
    for path in (capsules_dir(root), profiles_dir(root), logs_dir(root)):
        path.mkdir(parents=True, exist_ok=True)
