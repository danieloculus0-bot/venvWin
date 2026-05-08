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


def test_build_iso_disables_toram_and_adds_live_autologin():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    assert '--bootappend-live "boot=live components quiet splash persistence"' in script
    assert " toram" not in script
    assert "lightdm-gtk-greeter" in script
    assert "50-venvwin-live-autologin.conf" in script
    assert "autologin-user=user" in script
    assert "live_user_autologin=true" in script


def test_build_iso_keeps_storage_source_visible():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    assert ".winux-capsule-store-source" in script
    assert "VENVWIN_HOME_SOURCE" in script
    assert "storage_source_marker=true" in script


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


def test_flash_ready_gate_checks_boot_and_autologin_contracts():
    script = (ROOT / "winux-portable" / "build-flash-ready-standard.sh").read_text(encoding="utf-8")

    assert "^boot_toram_default=false$" in script
    assert "BOOT_CONFIG_TEXT" in script
    assert "toram" in script
    assert "boot_toram_absent=pass" in script
    assert "squashfs-root/etc/lightdm/lightdm.conf.d/50-venvwin-live-autologin.conf" in script
    assert "live_user_autologin=pass" in script
    assert "storage_source_marker=pass" in script


def test_manifest_contract_names_visible_desktop_launchers():
    script = (ROOT / "winux-portable" / "build-iso.sh").read_text(encoding="utf-8")

    manifest_line = "first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop"
    assert manifest_line in script
