"""Native Puppy six-gate source report must never fabricate boot evidence."""
import json
from pathlib import Path

from venvwin.puppy_evidence import build_report

ROOT = Path(__file__).resolve().parents[1]


def test_native_source_reports_two_design_checks_without_boot_claim():
    report = build_report(ROOT)
    assert report["phase"] == "puppy"
    checks = report["checks"]
    assert checks["kernel_source_guard"]["status"] == "pass"
    assert checks["lean_core_package_boundary"]["status"] == "pass"
    for key in ("runtime_overlay", "ram_copy_verified", "persistence_reboot",
                "external_app_modules"):
        assert checks[key]["status"] == "missing"
    assert checks["kernel_source_guard"]["evidence"].startswith("source:")
    assert "puppy-native/build-puppy.sh" in checks["kernel_source_guard"]["evidence"]
    assert "sha256:" in checks["lean_core_package_boundary"]["evidence"]
    assert report["source_type"] == "repository_static_inspection"


def test_missing_native_puppy_source_is_explicitly_unverified(tmp_path):
    report = build_report(tmp_path)
    assert report["checks"]["kernel_source_guard"]["status"] == "missing"
    assert report["checks"]["lean_core_package_boundary"]["status"] == "missing"
    assert all(item["status"] != "pass" for item in report["checks"].values())


def test_puppy_layer_is_distinct_and_no_debian_legacy_packages_are_claimed():
    script = (ROOT / "puppy-native/build-puppy.sh").read_text()
    assert "ydrv_dpupbw64_10.0.12.sfs" in script
    assert "REFUSE_TO_REPLACE_EXISTING_UPSTREAM_YDRV" in script
    assert "-boot_image any replay -commit" in script
    assert "UPSTREAM_SHA256=" in script
    assert "lb config" not in script and "debootstrap" not in script


def test_native_six_gate_report_json_preserves_unverified_runtime():
    report = json.loads(json.dumps(build_report(ROOT), allow_nan=False))
    assert len(report["checks"]) == 6
    assert all(item["status"] == "pass" and item["evidence"].startswith("source:")
               for item in list(report["checks"].values())[:2])
    assert all(item["status"] != "pass" for item in list(report["checks"].values())[2:])
    assert report["scope"]["source_artifacts_not_runtime_proof"] is True
