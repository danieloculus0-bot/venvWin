from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PREFLIGHT_FILES = [
    "winux-portable/audit-public-branding.sh",
    "winux-portable/bootstrap-flash-ready-ubuntu.sh",
    "winux-portable/build-all-profiles.sh",
    "winux-portable/build-flash-ready-standard.sh",
    "winux-portable/build-iso.sh",
    "winux-portable/compare-profiles.sh",
    "winux-portable/test-iso-qemu.sh",
    "winux-portable/test-persistence-qemu.sh",
    "winux-portable/windows-wsl-build-command.md",
    "winux-portable/workflow-contract.json",
    "winux-portable/local-flash-ready-build.md",
    "winux-portable/run-flash-ready-from-phone.md",
]


def test_preflight_requires_flash_ready_build_spine():
    script = (ROOT / "winux-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    for required in REQUIRED_PREFLIGHT_FILES:
        assert f'"{required}"' in script


def test_preflight_checks_flash_ready_squashfs_contract():
    script = (ROOT / "winux-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    required_checks = [
        "unsquashfs -ll",
        "squashfs_static_inspection=pass",
        "squashfs-root/etc/skel/Desktop/venvWin-First-Boot.desktop",
        "venvwin-portable-alpha-standard.iso",
        "venvwin-flash-ready-verdict.txt",
    ]

    for check in required_checks:
        assert check in script


def test_preflight_runs_public_branding_audit_and_pytest():
    script = (ROOT / "winux-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    assert "./winux-portable/audit-public-branding.sh" in script
    assert "python3 -m pytest -q" in script
    assert "PRE-ISO READINESS: PASS" in script
