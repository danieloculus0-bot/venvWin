from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PORTABLE_SOURCES = {
    "VENVWIN_HOME",
    "live-persistence",
    "persistence-root",
    "mounted-venvwin-persistence",
    "usb-label-venvwindata",
    "usb-label-venvwindata-mixed",
    "live-home-overlay",
}

HOST_RISK_SOURCES = {
    "home-fallback",
    "advanced-user-selected",
}

DISPOSABLE_SOURCES = {
    "home-fallback",
    "live-home-overlay",
}

LIVE_MEDIA_MARKERS = (
    Path("/run/live/medium"),
    Path("/run/live/persistence"),
    Path("/lib/live/mount/medium"),
    Path("/lib/live/mount/persistence"),
)


@dataclass(slots=True)
class PersistenceCandidate:
    path: Path
    source: str
    writable: bool
    portable_owned: bool
    host_risk: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "source": self.source,
            "writable": self.writable,
            "portable_owned": self.portable_owned,
            "host_risk": self.host_risk,
        }


def running_from_live_media() -> bool:
    return any(marker.exists() for marker in LIVE_MEDIA_MARKERS)


def classify_candidate(path: Path, source: str) -> tuple[bool, bool]:
    if source in PORTABLE_SOURCES:
        return True, False
    if source in HOST_RISK_SOURCES:
        return False, True
    path_text = str(path)
    if "/VENVWINDATA/" in path_text or "/venvWinData/" in path_text:
        return True, False
    return False, True


def is_writable_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".venvwin-write-test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def make_candidate(path: Path, source: str) -> PersistenceCandidate:
    portable_owned, host_risk = classify_candidate(path, source)
    return PersistenceCandidate(
        path=path,
        source=source,
        writable=is_writable_directory(path),
        portable_owned=portable_owned,
        host_risk=host_risk,
    )


def env_home_source() -> str:
    return os.environ.get("VENVWIN_HOME_SOURCE") or "VENVWIN_HOME"


def candidate_paths(home: Path | None = None) -> list[PersistenceCandidate]:
    user_home = home or Path.home()
    candidates: list[tuple[Path, str]] = []

    env_home = os.environ.get("VENVWIN_HOME")
    if env_home:
        candidates.append((Path(env_home).expanduser(), env_home_source()))

    candidates.extend(
        [
            (Path("/run/live/persistence/venvWin-Capsules"), "live-persistence"),
            (Path("/persistence/venvWin-Capsules"), "persistence-root"),
            (Path("/mnt/venvwin-persistence/venvWin-Capsules"), "mounted-venvwin-persistence"),
            (Path("/media") / user_home.name / "VENVWINDATA" / "venvWin-Capsules", "usb-label-venvwindata"),
            (Path("/media") / user_home.name / "venvWinData" / "venvWin-Capsules", "usb-label-venvwindata-mixed"),
        ]
    )

    if running_from_live_media():
        candidates.append((user_home / "venvWin-Capsules", "live-home-overlay"))

    candidates.append((user_home / "venvWin-Capsules", "home-fallback"))

    seen: set[str] = set()
    result: list[PersistenceCandidate] = []
    for path, source in candidates:
        resolved = str(path.expanduser())
        seen_key = f"{source}:{resolved}"
        if seen_key in seen:
            continue
        seen.add(seen_key)
        result.append(make_candidate(Path(resolved), source))
    return result


def choose_capsule_store(home: Path | None = None) -> PersistenceCandidate:
    candidates = candidate_paths(home)
    for candidate in candidates:
        if candidate.writable and candidate.portable_owned and not candidate.host_risk:
            return candidate
    for candidate in candidates:
        if candidate.writable and candidate.source == "home-fallback":
            return candidate
    fallback = PersistenceCandidate(
        path=(home or Path.home()) / "venvWin-Capsules",
        source="home-fallback",
        writable=False,
        portable_owned=False,
        host_risk=True,
    )
    return fallback


def persistence_report(home: Path | None = None) -> dict[str, Any]:
    candidates = candidate_paths(home)
    chosen = choose_capsule_store(home)
    disposable = chosen.source in DISPOSABLE_SOURCES
    traceable_portable_state = chosen.portable_owned and not chosen.host_risk
    return {
        "chosen": chosen.to_dict(),
        "traceable_portable_state": traceable_portable_state,
        "leave_no_trace": traceable_portable_state,
        "disposable_warning": disposable,
        "host_write_warning": chosen.host_risk,
        "candidates": [candidate.to_dict() for candidate in candidates],
    }
