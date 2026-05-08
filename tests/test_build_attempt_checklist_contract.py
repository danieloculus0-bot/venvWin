from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_build_attempt_checklist_names_product_and_safe_paths():
    checklist = (ROOT / "venvwin-portable" / "build-attempt-checklist.md").read_text(encoding="utf-8")

    assert "venvWin Portable Build Attempt Checklist" in checklist
    assert "venvWin Portable" in checklist
    assert "Internal codename:" in checklist
    assert "venvWin" in checklist
    assert ".\\venvwin-portable\\run-wsl-flash-ready.ps1" in checklist
    assert "bootstrap-flash-ready-ubuntu.sh" in checklist


def test_build_attempt_checklist_requires_flash_ready_verdict_and_artifacts():
    checklist = (ROOT / "venvwin-portable" / "build-attempt-checklist.md").read_text(encoding="utf-8")

    required = [
        "status=FLASH_READY",
        "dist/venvwin-portable-alpha-standard.iso",
        "dist/venvwin-portable-alpha-standard.iso.sha256",
        "dist/venvwin-portable-alpha-standard-manifest.txt",
        "dist/venvwin-flash-ready-verdict.txt",
    ]

    for text in required:
        assert text in checklist


def test_build_attempt_checklist_requires_gate_markers():
    checklist = (ROOT / "venvwin-portable" / "build-attempt-checklist.md").read_text(encoding="utf-8")

    required = [
        "PUBLIC BRANDING AUDIT: PASS",
        "PRE-ISO READINESS: PASS",
        "squashfs_static_inspection=pass",
        "qemu_smoke=pass",
        "FLASH READY: dist/venvwin-portable-alpha-standard.iso",
    ]

    for text in required:
        assert text in checklist


def test_build_attempt_checklist_keeps_failure_capture_rules():
    checklist = (ROOT / "venvwin-portable" / "build-attempt-checklist.md").read_text(encoding="utf-8")

    assert "last visible error block" in checklist
    assert "which step failed" in checklist
    assert "contents of dist/venvwin-flash-ready-verdict.txt if it exists" in checklist
    assert "Do not start random fixes before identifying the failing step" in checklist


def test_preflight_requires_build_attempt_checklist_contract():
    preflight = (ROOT / "venvwin-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    assert '"venvwin-portable/build-attempt-checklist.md"' in preflight
    assert "Checking build attempt checklist contract" in preflight
    assert "run-wsl-flash-ready.ps1" in preflight
    assert "bootstrap-flash-ready-ubuntu.sh" in preflight
    assert "PUBLIC BRANDING AUDIT: PASS" in preflight
    assert "PRE-ISO READINESS: PASS" in preflight
    assert "status=FLASH_READY" in preflight
