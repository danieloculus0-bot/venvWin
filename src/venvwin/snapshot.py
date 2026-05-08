from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path
from typing import Any

from .capsule import Capsule, capsule_dir, load_capsule, save_capsule, utc_now


def snapshot_name(label: str | None = None) -> str:
    stamp = utc_now().replace(":", "-")
    clean_label = ""
    if label:
        clean_label = "-" + "".join(ch.lower() if ch.isalnum() else "-" for ch in label).strip("-")
    return f"snapshot-{stamp}{clean_label}.tar.gz"


def create_snapshot(capsules_root: Path, capsule: Capsule, label: str | None = None) -> dict[str, Any]:
    root = capsule_dir(capsules_root, capsule.capsule_id)
    prefix = Path(capsule.prefix_path)
    snapshots = root / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)

    if not prefix.exists():
        raise FileNotFoundError(f"Prefix not found: {prefix}")

    target = snapshots / snapshot_name(label)
    metadata_path = root / "venvwin.json"

    with tarfile.open(target, "w:gz") as tar:
        tar.add(prefix, arcname="prefix")
        if metadata_path.exists():
            tar.add(metadata_path, arcname="venvwin.json")

    record = {
        "name": target.name,
        "path": str(target),
        "label": label,
        "created_at": utc_now(),
        "type": "prefix-and-metadata",
    }
    capsule.snapshots.append(record)
    save_capsule(capsules_root, capsule)
    return record


def restore_snapshot(capsules_root: Path, capsule_id: str, snapshot_file: Path) -> dict[str, Any]:
    capsule = load_capsule(capsules_root, capsule_id)
    root = capsule_dir(capsules_root, capsule.capsule_id)
    prefix = Path(capsule.prefix_path)

    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_file}")

    backup_dir = root / "restore-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_prefix = backup_dir / f"prefix-before-restore-{utc_now().replace(':', '-') }"

    if prefix.exists():
        shutil.move(str(prefix), str(backup_prefix))

    with tarfile.open(snapshot_file, "r:gz") as tar:
        members = [member for member in tar.getmembers() if member.name.startswith("prefix/")]
        tar.extractall(root, members=members)

    restored = {
        "snapshot": str(snapshot_file),
        "restored_at": utc_now(),
        "previous_prefix_backup": str(backup_prefix) if backup_prefix.exists() else None,
    }
    capsule.snapshots.append({"restore": restored})
    save_capsule(capsules_root, capsule)
    return restored


def reset_capsule_prefix(capsules_root: Path, capsule: Capsule) -> dict[str, Any]:
    from .state import ensure_prefix_shape

    root = capsule_dir(capsules_root, capsule.capsule_id)
    prefix = Path(capsule.prefix_path)
    backup_dir = root / "reset-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_prefix = backup_dir / f"prefix-before-reset-{utc_now().replace(':', '-') }"

    if prefix.exists():
        shutil.move(str(prefix), str(backup_prefix))

    prefix.mkdir(parents=True, exist_ok=True)
    ensure_prefix_shape(prefix)

    record = {
        "reset_at": utc_now(),
        "previous_prefix_backup": str(backup_prefix) if backup_prefix.exists() else None,
        "protect_user_documents": capsule.permission_policy.get("protect_user_documents_on_reset", True),
    }
    capsule.snapshots.append({"reset": record})
    save_capsule(capsules_root, capsule)
    return record
