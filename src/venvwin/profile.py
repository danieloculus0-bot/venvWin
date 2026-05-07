from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RunnerProfile:
    name: str
    runner: str = "wine"
    arch: str = "win64"
    env: dict[str, str] = field(default_factory=dict)
    args: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def default(cls) -> "RunnerProfile":
        return cls(
            name="default",
            runner="wine",
            arch="win64",
            env={},
            args=[],
            notes="Default isolated venvWin runner profile.",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunnerProfile":
        return cls(
            name=str(data.get("name", "default")),
            runner=str(data.get("runner", "wine")),
            arch=str(data.get("arch", "win64")),
            env=dict(data.get("env", {})),
            args=list(data.get("args", [])),
            notes=str(data.get("notes", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "runner": self.runner,
            "arch": self.arch,
            "env": self.env,
            "args": self.args,
            "notes": self.notes,
        }


def profile_path(profiles_root: Path, name: str) -> Path:
    return profiles_root / f"{name}.json"


def load_profile(profiles_root: Path, name: str) -> RunnerProfile:
    path = profile_path(profiles_root, name)
    if not path.exists():
        if name == "default":
            profile = RunnerProfile.default()
            save_profile(profiles_root, profile)
            return profile
        raise FileNotFoundError(f"Profile not found: {path}")
    return RunnerProfile.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_profile(profiles_root: Path, profile: RunnerProfile) -> Path:
    profiles_root.mkdir(parents=True, exist_ok=True)
    path = profile_path(profiles_root, profile.name)
    path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
    return path
