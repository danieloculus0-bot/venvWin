"""Fail-closed static contract for the Puppy-native venvWin migration."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "puppy-native/build.sh"
WORKFLOW = ROOT / ".github/workflows/puppy-native-boot.yml"


def test_build_script_is_real_and_syntactically_valid():
    subprocess.run(["bash", "-n", str(BUILD)], check=True)


def test_official_puppy_base_is_immutable_and_checksum_pinned():
    source = BUILD.read_text()
    assert "BookwormPup64_10.0.12.iso" in source
    assert "ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f" in source
    assert "sha256sum -c -" in source
    assert "curl -fLsS" in source
    assert 'rm -f "$base"' not in source


def test_real_puppy_bootloader_and_optional_sfs_are_preserved():
    source = BUILD.read_text()
    assert "-boot_image any replay" in source
    assert "mksquashfs" in source
    assert "adrv_dpupbw64_10.0.12.sfs" in source
    assert "ydrv_dpupbw64_10.0.12.sfs" in source
    assert 'PUPPY_SFS_SLOTS_OCCUPIED' in source
    assert "-map " in source
    assert "live-build" not in source
    assert "lb build" not in source


def test_puppy_guest_not_host_must_emit_boot_proof():
    source = BUILD.read_text()
    workflow = WORKFLOW.read_text()
    assert "root/Startup/venvwin-puppy-guest-probe" in source
    assert "PUPPY_GUEST_DESKTOP_STARTUP_PASS" in source
    assert "PUPPY_GUEST_VENVWIN_CLI_PASS" in source
    assert 'if [ -c /dev/ttyS0 ]' in source
    assert "qemu-system-x86_64" in workflow
    assert "-cdrom " in workflow
    assert "-net none" in workflow
    assert "grep -Fxq PUPPY_GUEST_DESKTOP_STARTUP_PASS dist/puppy-guest-serial.log" in workflow
    assert "grep -Fxq PUPPY_GUEST_VENVWIN_CLI_PASS dist/puppy-guest-serial.log" in workflow


def test_original_venvwin_application_is_copied_not_rewritten():
    source = BUILD.read_text()
    assert 'cp -a src/. "$stage/opt/venvwin/src/"' in source
    assert "python3 -m venvwin.cli" in source
    assert "PUPPY_VENVWIN_NEEDS_PYTHON3" in source
    assert "PUPPY_GUEST_VENVWIN_RUNTIME_BLOCKED" in source


def test_build_ci_refuses_release_claim():
    workflow = WORKFLOW.read_text()
    assert "RELEASE_READY=NO" in workflow
    assert "PERSISTENCE_REBOOT=UNVERIFIED" in workflow
    assert "TORAM_OPTION=UNVERIFIED" in workflow
    assert "WINDOWS_CAPSULE_INSIDE_PUPPY=UNVERIFIED" in workflow
    assert "never publish an unverified ISO" in workflow
    assert "timeout-minutes: 55" in workflow
