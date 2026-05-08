from pathlib import Path

from venvwin.capsule import create_capsule
from venvwin.profile import RunnerProfile
from venvwin.snapshot import create_snapshot, reset_capsule_prefix


def test_create_snapshot(tmp_path: Path):
    capsule = create_capsule(tmp_path, "Test App", RunnerProfile.default())
    marker = Path(capsule.prefix_path) / "drive_c" / "marker.txt"
    marker.write_text("state", encoding="utf-8")

    record = create_snapshot(tmp_path, capsule, "good")

    assert record["label"] == "good"
    assert Path(record["path"]).exists()
    assert record["type"] == "prefix-and-metadata"


def test_reset_capsule_prefix(tmp_path: Path):
    capsule = create_capsule(tmp_path, "Test App", RunnerProfile.default())
    marker = Path(capsule.prefix_path) / "drive_c" / "marker.txt"
    marker.write_text("state", encoding="utf-8")

    record = reset_capsule_prefix(tmp_path, capsule)

    assert Path(record["previous_prefix_backup"]).exists()
    assert (Path(capsule.prefix_path) / "drive_c" / "Program Files").is_dir()
    assert not marker.exists()
