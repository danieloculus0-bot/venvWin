"""A core image is real only after kernel, size, guest and BEAN evidence pass."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "venvwin-portable/build-core-proof.sh"
WRAPPER = ROOT / "venvwin-portable/build-in-bookworm.sh"
WORKFLOW = ROOT / ".github/workflows/puppy-core-boot-lab.yml"


def test_core_scripts_have_valid_bash_syntax():
    for script in (CORE, WRAPPER):
        subprocess.run(["bash", "-n", str(script)], check=True)


def test_core_build_keeps_standard_legacy_explicit():
    wrapper = WRAPPER.read_text()
    assert 'VENVWIN_BOOKWORM_BUILD_TARGET:-standard' in wrapper
    assert 'standard|core)' in wrapper
    assert 'core) bash ./venvwin-portable/build-core-proof.sh' in wrapper


def test_core_proof_never_attaches_a_guest_host_drive():
    script = CORE.read_text()
    assert 'VENVWIN_PORTABLE_PROFILE=core' in script
    assert '-cdrom "$ISO"' in script
    assert "-net none" in script
    assert "NO HOST DISK IMAGE ATTACHED TO GUEST" in script
    assert "CORE_STATIC_BOOT_MISSING" in script
    assert "BEAN_GUEST_READY" in script
    assert "BEAN_GUEST_FIRST_RUN_PASS" in script
    assert "CORE_GUEST_PROOF_MISSING" in script


def test_oversize_diagnostic_iso_cannot_pass_as_release():
    script = CORE.read_text()
    assert "BUILDER_REJECTED_CORE" in script
    assert 'PUBLISHED=0' in script
    assert 'if [[ "$PUBLISHED" -ne 1 ]]' in script
    assert "CORE_IMAGE_NOT_RELEASABLE" in script
    assert "persistence_reboot=not_verified" in script
    assert "copy_to_ram=not_verified" in script


def test_action_collects_real_evidence_but_never_uploads_a_failed_iso():
    workflow = WORKFLOW.read_text()
    assert "branches: [feat/puppy-core-boot-lab-20261010]" in workflow
    assert "VENVWIN_BOOKWORM_BUILD_TARGET=core" in workflow
    assert "v1" not in workflow  # Avoid invented local compiler.
    assert "--phase iso" in workflow
    assert "--repeat 5" in workflow
    assert "steps.core_boot.outcome == 'success' && steps.bean.outcome == 'success'" in workflow
    assert "venvwin-puppy-core-boot-proven-iso" in workflow
    assert "venvwin-core-qemu-serial.log" in workflow


def test_headless_grub_selection_is_not_mistaken_for_guest_readiness():
    script = CORE.read_text()
    assert 'channel.sendall(b"sendkey ret\\n")' in script
    assert "QEMU_BOOT_MENU_ENTER_SENT (not guest boot evidence)" in script
    assert "QEMU_BOOT_MENU_ENTER_FAILED" in script
    assert 'grep -Fxq "BEAN_GUEST_READY" "$SERIAL"' in script
    assert 'grep -Fxq "BEAN_GUEST_FIRST_RUN_PASS" "$SERIAL"' in script
    assert "status=CORE_GUEST_PROVEN" in script


def test_qemu_monitor_sends_real_enter_to_mock_grub_console(tmp_path):
    """Exercise the actual embedded HMP client; no ISO, QEMU or fake guest proof."""
    import socket
    import sys
    import threading

    script = CORE.read_text()
    client = script.split('python3 - "$MONITOR" <<\'PY\'', 1)[1].split("\n", 1)[1].split("\nPY", 1)[0]
    monitor = tmp_path / "qemu.sock"
    received = []

    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(monitor))
        server.listen(1)

        def serve():
            with server.accept()[0] as conn:
                conn.sendall(b"QEMU monitor ready\\n(qemu) ")
                received.append(conn.recv(128))
                conn.sendall(b"(qemu) ")

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        result = subprocess.run(
            [sys.executable, "-c", client, str(monitor)],
            capture_output=True, text=True, timeout=8,
        )
        thread.join(timeout=3)

    assert result.returncode == 0, result.stderr
    assert received == [b"sendkey ret\\n"]
    assert "QEMU_BOOT_MENU_ENTER_SENT" in result.stdout
    assert "BEAN_GUEST_READY" not in result.stdout
