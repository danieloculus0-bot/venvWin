from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_usb_flash_guide_is_gated_by_flash_ready_verdict():
    guide = (ROOT / "venvwin-portable" / "usb-flash-guide.md").read_text(encoding="utf-8")

    assert "venvWin Portable USB Flash Guide" in guide
    assert "status=FLASH_READY" in guide
    assert "dist/venvwin-flash-ready-verdict.txt" in guide
    assert "dist/venvwin-portable-alpha-standard.iso" in guide
    assert "dist/venvwin-portable-alpha-standard.iso.sha256" in guide
    assert "(cd dist && sha256sum -c venvwin-portable-alpha-standard.iso.sha256)" in guide


def test_usb_flash_guide_warns_about_whole_device_writes():
    guide = (ROOT / "venvwin-portable" / "usb-flash-guide.md").read_text(encoding="utf-8")

    assert "Do not select a work drive" in guide
    assert "Flashing writes the whole device" in guide
    assert "whole USB device" in guide
    assert "not a partition like `/dev/sdX1`" in guide


def test_usb_flash_guide_requires_first_boot_visual_product_checks():
    guide = (ROOT / "venvwin-portable" / "usb-flash-guide.md").read_text(encoding="utf-8")

    required = [
        "venvWin-First-Boot.desktop",
        "venvWin-Dashboard.desktop",
        "venvWin-Capsules.desktop",
        "venvWin-Doctor.desktop",
        "venvWin-Private-Browser.desktop",
        "Start panel",
        "Control Panel section",
        "System Status section",
        "Dashboard URL",
        "Capsule storage path",
        "Leave-no-trace status",
        "Host write risk",
        "http://127.0.0.1:8787",
    ]

    for text in required:
        assert text in guide


def test_preflight_requires_usb_flash_guide_contract():
    preflight = (ROOT / "venvwin-portable" / "pre-iso-readiness.sh").read_text(encoding="utf-8")

    assert '"venvwin-portable/usb-flash-guide.md"' in preflight
    assert "Checking USB flash guide contract" in preflight
    assert "status=FLASH_READY" in preflight
    assert "(cd dist && sha256sum -c venvwin-portable-alpha-standard.iso.sha256)" in preflight
    assert "dist/venvwin-portable-alpha-standard.iso" in preflight
    assert "dist/venvwin-flash-ready-verdict.txt" in preflight
