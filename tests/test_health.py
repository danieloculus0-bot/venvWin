from pathlib import Path

from venvwin.health import health_report
from venvwin.paths import ensure_runtime_dirs


def test_health_report_warns_without_associations(tmp_path: Path):
    root = tmp_path / "runtime"
    apps = tmp_path / "applications"
    ensure_runtime_dirs(root)

    report = health_report(root, apps)

    assert report["overall"] in {"ok", "warn"}
    names = {check["name"] for check in report["checks"]}
    assert "runtime-root" in names
    assert "runner" in names
    assert "privacy-browser" in names
    assert "file-associations" in names
    assert "persistence" in names
