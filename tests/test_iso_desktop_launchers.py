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


def test_flash_ready_gate_requires_visible_desktop_launchers_inside_squashfs():
    script = (ROOT / "winux-portable" / "build-flash-ready-standard.sh").read_text(encoding="utf-8")

    assert "^first_boot_desktop_launchers=true$" in script
    assert "unsquashfs -ll" in script
    assert "SQUASHFS_LIST" in script
    assert "squashfs_static_inspection=pass" in script

    for launcher in EXPECTED_DESKTOP_LAUNCHERS:
        assert f"squashfs-root/etc/skel/Desktop/{launcher}" in script


def test_flash_ready_gate_does_not_assume_chroot_files_live_at_iso_root():
    script = (ROOT / "winux-portable" / "build-flash-ready-standard.sh").read_text(encoding="utf-8")

    bad_direct_checks = [
        'xorriso -indev "${ISO}" -find / -path /usr/local/bin/venvwin',
        'xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-First-Boot.desktop',
    ]

    for bad in bad_direct_checks:
        assert bad not in script


def test_manifest_contract_names_visible_desktop_launchers():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    manifest_line = "first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop"
    assert manifest_line in script
