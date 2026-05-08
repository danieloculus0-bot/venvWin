from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DESKTOP_LAUNCHERS = [
    "venvWin-First-Boot.desktop",
    "venvWin-Dashboard.desktop",
    "venvWin-Capsules.desktop",
    "venvWin-Doctor.desktop",
    "venvWin-Private-Browser.desktop",
]


def test_build_iso_creates_visible_desktop_launchers():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    assert "config/includes.chroot/etc/skel/Desktop" in script
    assert "first_boot_desktop_launchers=true" in script
    assert "first_boot_desktop_launchers_list=" in script

    for launcher in EXPECTED_DESKTOP_LAUNCHERS:
        assert f"/etc/skel/Desktop/{launcher}" in script
        assert launcher in script


def test_flash_ready_gate_requires_visible_desktop_launchers():
    script = (ROOT / "winux-portable" / "build-flash-ready-standard.sh").read_text(encoding="utf-8")

    assert "^first_boot_desktop_launchers=true$" in script

    for launcher in EXPECTED_DESKTOP_LAUNCHERS:
        assert f"/etc/skel/Desktop/{launcher}" in script


def test_manifest_contract_names_visible_desktop_launchers():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    manifest_line = "first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop"
    assert manifest_line in script
