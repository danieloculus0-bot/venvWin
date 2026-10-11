"""BEAN Puppy evidence must not turn planned features into observed runtime facts."""
import json
from pathlib import Path

from venvwin.puppy_evidence import build_report, _heredoc_packages


ROOT = Path(__file__).resolve().parents[1]


def test_real_source_reports_exactly_what_is_implemented():
    report = build_report(ROOT)
    assert report["phase"] == "puppy"
    checks = report["checks"]
    assert checks["kernel_source_guard"]["status"] == "pass"
    assert checks["lean_core_package_boundary"]["status"] == "pass"
    for name in ("runtime_overlay", "ram_copy_verified", "persistence_reboot",
                 "external_app_modules"):
        assert checks[name]["status"] == "missing"
    assert "source:" in checks["kernel_source_guard"]["evidence"]
    assert "sha256:" in checks["lean_core_package_boundary"]["evidence"]
    assert report["source_type"] == "repository_static_inspection"


def test_no_kernel_guard_is_not_claimed_as_pass(tmp_path: Path):
    report = build_report(tmp_path)
    assert report["checks"]["kernel_source_guard"]["status"] == "missing"
    assert report["checks"]["lean_core_package_boundary"]["status"] == "missing"


def test_existing_standard_packages_retained_outside_lean_core():
    script = (ROOT / "venvwin-portable" / "build-iso.sh").read_text()
    core = _heredoc_packages(script, "00-venvwin-core.list.chroot")
    extra = _heredoc_packages(script, "05-venvwin-utilities.list.chroot")
    assert core and extra
    assert core.isdisjoint(extra)
    assert len(core | extra) == 89
    assert "libreoffice-calc" in extra
    assert "firefox-esr" in extra
    assert "ffmpeg" in extra
    assert "linux-image-amd64" in core
    assert "xfce4-session" in core


def test_bean_report_serializable_and_has_no_synthetic_passes():
    text = json.dumps(build_report(ROOT), allow_nan=False)
    parsed = json.loads(text)
    assert all(record["status"] == "pass" and record["evidence"].startswith("source:")
               for record in list(parsed["checks"].values())[:2])
    assert all(record["status"] != "pass" for record in
               list(parsed["checks"].values())[2:])
