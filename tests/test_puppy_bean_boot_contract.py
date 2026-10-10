"""Regressions discovered when testing venvWin under BEAN's root build lab."""
from pathlib import Path

from venvwin.persistence import make_candidate


def test_absent_external_mount_is_not_fabricated(tmp_path: Path):
    parent = tmp_path / "not-mounted" / "VENVWINDATA"
    requested = parent / "venvWin-Capsules"
    result = make_candidate(requested, "usb-label-venvwindata")
    assert result.writable is False
    assert requested.exists() is False
    assert parent.exists() is False


def test_implicit_persistence_directory_is_not_created(tmp_path: Path):
    path = tmp_path / "missing-persistence" / "venvWin-Capsules"
    candidate = make_candidate(path, "mounted-venvwin-persistence")
    assert not candidate.writable
    assert not path.exists()


def test_explicit_venvwin_home_can_initialize_storage(tmp_path: Path):
    path = tmp_path / "explicit" / "venvWin-Capsules"
    candidate = make_candidate(path, "VENVWIN_HOME")
    assert candidate.writable
    assert path.is_dir()


def test_guest_boot_requires_real_serial_proof():
    root = Path(__file__).resolve().parents[1]
    build = (root / "venvwin-portable" / "build-flash-ready-standard.sh").read_text()
    iso = (root / "venvwin-portable" / "build-iso.sh").read_text()
    workflow = (root / ".github" / "workflows" / "flash-ready-standard.yml").read_text()
    assert "BEAN_GUEST_READY" in build
    assert "BEAN_GUEST_FIRST_RUN_PASS" in build
    assert 'grep -Fxq "BEAN_GUEST_READY"' in build
    assert "qemu_smoke=guest_side_proven" in build
    assert "BEAN_GUEST_NOT_READY" in iso
    assert "xfce4-session" in iso
    assert "ezbean.smoke_lab" in workflow
    assert "--repeat 5" in workflow
