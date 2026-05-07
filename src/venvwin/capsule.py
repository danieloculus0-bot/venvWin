from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .profile import RunnerProfile
from .state import default_filesystem_mappings, default_permission_policy, ensure_prefix_shape


def slugify_app_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", name.strip()).strip("-._")
    return cleaned.lower() or "app"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class Capsule:
    app_name: str
    capsule_id: str
    created_at: str
    updated_at: str
    profile: RunnerProfile
    prefix_path: str
    filesystem_mappings: dict[str, str] = field(default_factory=default_filesystem_mappings)
    permission_policy: dict[str, Any] = field(default_factory=default_permission_policy)
    installers: list[dict[str, Any]] = field(default_factory=list)
    launchers: list[dict[str, Any]] = field(default_factory=list)
    snapshots: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def new(cls, app_name: str, capsule_root: Path, profile: RunnerProfile) -> "Capsule":
        capsule_id = slugify_app_name(app_name)
        now = utc_now()
        return cls(
            app_name=app_name,
            capsule_id=capsule_id,
            created_at=now,
            updated_at=now,
            profile=profile,
            prefix_path=str(capsule_root / capsule_id / "prefix"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Capsule":
        return cls(
            app_name=str(data["app_name"]),
            capsule_id=str(data["capsule_id"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            profile=RunnerProfile.from_dict(dict(data["profile"])),
            prefix_path=str(data["prefix_path"]),
            filesystem_mappings=dict(data.get("filesystem_mappings", default_filesystem_mappings())),
            permission_policy=dict(data.get("permission_policy", default_permission_policy())),
            installers=list(data.get("installers", [])),
            launchers=list(data.get("launchers", [])),
            snapshots=list(data.get("snapshots", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "capsule_id": self.capsule_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "profile": self.profile.to_dict(),
            "prefix_path": self.prefix_path,
            "filesystem_mappings": self.filesystem_mappings,
            "permission_policy": self.permission_policy,
            "installers": self.installers,
            "launchers": self.launchers,
            "snapshots": self.snapshots,
        }


def capsule_dir(capsules_root: Path, capsule_id: str) -> Path:
    return capsules_root / capsule_id


def capsule_metadata_path(capsules_root: Path, capsule_id: str) -> Path:
    return capsule_dir(capsules_root, capsule_id) / "venvwin.json"


def create_capsule(capsules_root: Path, app_name: str, profile: RunnerProfile) -> Capsule:
    capsule = Capsule.new(app_name, capsules_root, profile)
    root = capsule_dir(capsules_root, capsule.capsule_id)
    metadata = capsule_metadata_path(capsules_root, capsule.capsule_id)

    if metadata.exists():
        raise FileExistsError(f"Capsule already exists: {capsule.capsule_id}")

    prefix = root / "prefix"
    prefix.mkdir(parents=True, exist_ok=False)
    ensure_prefix_shape(prefix)
    (root / "installers").mkdir(parents=True, exist_ok=True)
    (root / "launchers").mkdir(parents=True, exist_ok=True)
    (root / "snapshots").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    save_capsule(capsules_root, capsule)
    return capsule


def load_capsule(capsules_root: Path, capsule_id: str) -> Capsule:
    path = capsule_metadata_path(capsules_root, capsule_id)
    if not path.exists():
        raise FileNotFoundError(f"Capsule not found: {capsule_id}")
    return Capsule.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_capsule(capsules_root: Path, capsule: Capsule) -> Path:
    capsule.updated_at = utc_now()
    path = capsule_metadata_path(capsules_root, capsule.capsule_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(capsule.to_dict(), indent=2), encoding="utf-8")
    return path


def list_capsules(capsules_root: Path) -> list[Capsule]:
    if not capsules_root.exists():
        return []

    capsules: list[Capsule] = []
    for child in sorted(capsules_root.iterdir()):
        metadata = child / "venvwin.json"
        if child.is_dir() and metadata.exists():
            capsules.append(Capsule.from_dict(json.loads(metadata.read_text(encoding="utf-8"))))
    return capsules
