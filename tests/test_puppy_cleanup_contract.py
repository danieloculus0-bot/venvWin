"""Reject the known departures from the Lucid Puppy-adjacent specification.

No compiled ISO is produced by these regression tests.
"""
from pathlib import Path

from venvwin.puppy_evidence import build_report

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "venvwin-portable" / "build-iso.sh"
HEAVY_WORKFLOW = ROOT / ".github" / "workflows" / "flash-ready-standard.yml"


def test_disposable_session_by_default_not_automatic_usb_persistence():
    text = BUILDER.read_text()
    assert '--bootappend-live "boot=live components console=tty0 console=ttyS0,115200n8"' in text
    assert '--bootappend-live "boot=live components persistence ' not in text
    assert "persistence_default=none" in text
    assert "persistence_opt_in=true" in text
    assert "boot_toram_default=false" in text


def test_release_default_is_lean_puppy_core():
    text = BUILDER.read_text()
    assert 'PROFILE="${VENVWIN_PORTABLE_PROFILE:-core}"' in text
    assert 'VENVWIN_PORTABLE_PROFILE:-standard' not in text
    assert "CORE_SIZE_BUDGET_FAIL" in text
    assert "CORE_SIZE_WARNING" in text
    assert text.index("CORE_SIZE_BUDGET_FAIL") < text.index('cp "${ISO_PATH}" "${OUTPUT_ISO}"')


def test_dev_repository_is_not_embedded_in_live_os():
    text = BUILDER.read_text()
    assert '"${ROOT_DIR}/src/" "config/includes.chroot/opt/venvwin/src/"' in text
    assert '"${ROOT_DIR}/" "config/includes.chroot/opt/venvwin/"' not in text
    assert "packaged_payload=app_source_only" in text
    assert '--exclude \'__pycache__/\'' in text
    assert "README-PORTABLE.md" in text


def test_full_legacy_iso_never_rebuilds_automatically():
    workflow = HEAVY_WORKFLOW.read_text()
    assert "workflow_dispatch:" in workflow
    assert "  push:" not in workflow
    assert "build-in-bookworm.sh" in workflow


def test_bean_refuses_to_certify_unbuilt_puppy_runtime():
    report = build_report(ROOT)
    assert report["checks"]["kernel_source_guard"]["status"] == "pass"
    assert report["checks"]["lean_core_package_boundary"]["status"] == "pass"
    for key in ("runtime_overlay", "ram_copy_verified", "persistence_reboot",
                "external_app_modules"):
        assert report["checks"][key]["status"] != "pass"

def test_manifest_does_not_claim_unbundled_core_applications():
    text = BUILDER.read_text()
    for entry in (
        'VENVWIN_MANIFEST_STANDARD_BROWSER="netsurf-gtk,epiphany-browser"',
        'VENVWIN_MANIFEST_OFFICE_TOOLS="abiword,gnumeric"',
        'VENVWIN_MANIFEST_PDF_VIEWER="not_bundled"',
        'VENVWIN_MANIFEST_SOFTWARE_CENTER="not_bundled"',
        'VENVWIN_MANIFEST_PRIVACY_BROWSER_PROFILE="not_bundled"',
    ):
        assert entry in text
    assert "optional_launchers_may_require_modules=true" in text


def test_keep_useful_puppy_style_apps_and_hardware_drivers_in_core():
    from venvwin.puppy_evidence import _heredoc_packages
    script = BUILDER.read_text()
    core = _heredoc_packages(script, "00-venvwin-core.list.chroot")
    extra = _heredoc_packages(script, "05-venvwin-utilities.list.chroot")
    assert core and extra
    required_core = {"abiword", "gnumeric", "mtpaint", "ristretto", "xarchiver",
                     "galculator", "alsa-utils", "pipewire", "ntfs-3g",
                     "firmware-realtek", "firmware-iwlwifi", "pciutils", "usbutils"}
    assert required_core <= core
    required_extra = {"libreoffice-writer", "libreoffice-calc",
                      "firefox-esr", "ffmpeg"}
    assert required_extra <= extra
    assert not required_extra & core
    assert len(core | extra) == 89
