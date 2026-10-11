"""Source contract for native BookwormPup64 boot; NOT a replacement for a VM test."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "puppy-native/build-puppy.sh"
PROBE = ROOT / "puppy-native/venvwin-guest-probe"
BOOT = ROOT / "puppy-native/prove-puppy-qemu.sh"
LAUNCH = ROOT / "puppy-native/venvwin-launcher"
UPSTREAM_SHA = "ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f"


def test_scripts_are_actual_posix_and_bash_syntax():
    for path in (BUILDER, BOOT):
        subprocess.run(["bash", "-n", str(path)], check=True)
    for path in (PROBE, LAUNCH):
        subprocess.run(["sh", "-n", str(path)], check=True)


def test_official_puppy_checksum_is_immutable_and_enforced():
    text = BUILDER.read_text()
    assert f'UPSTREAM_SHA256="{UPSTREAM_SHA}"' in text
    assert len(UPSTREAM_SHA) == 64 and all(c in "0123456789abcdef" for c in UPSTREAM_SHA)
    assert "sha256sum -c -" in text
    assert "BookwormPup64_10.0.12.iso" in text
    assert "distro.ibiblio.org/puppylinux/puppy-bookwormpup/" in text
    assert "UPSTREAM_PUPPY_PAYLOAD_MISSING" in text


def test_true_upstream_puppy_iso_not_repackaged_debian():
    text = BUILDER.read_text()
    assert "xorriso -indev" in text
    assert 'xorriso -indev "$BASE" -outdev "$OUTPUT"' in text
    assert "-boot_image any replay -commit" in text
    for forbidden in ("lb config", "live-build", "debootstrap", "apt-get install"):
        assert forbidden not in text


def test_native_sfs_layer_cannot_overwrite_original_upstream_component():
    text = BUILDER.read_text()
    assert 'MODULE="ydrv_dpupbw64_10.0.12.sfs"' in text
    assert "REFUSE_TO_REPLACE_EXISTING_UPSTREAM_YDRV" in text
    assert 'mksquashfs "$STAGE" "$SFS"' in text
    assert "-map \"$SFS\" \"/$MODULE\"" in text
    assert '"$ROOT/src/venvwin"' in text
    assert "unsquashfs -l" in text
    assert "venvwin-guest-probe" in text
    assert "test -s \"$OUTPUT\"" in text


def test_guest_proof_is_real_puppy_autostart_and_overlay_detection():
    script = PROBE.read_text()
    assert 'LOG="/tmp/venvwin-puppy-guest-proof.log"' in script
    assert "/dev/ttyS0" in script
    assert 'DISPLAY' in script
    assert 'awk ' in script and '/proc/mounts' in script
    assert '"overlay"' in script and '"aufs"' in script
    assert "PUPPY_GUI_AND_OVERLAY_PRESENT" in script
    assert "PUPPY_VENVWIN_CAPSULE_CLI_PASS" in script
    assert "PUPPY_GUEST_BOOT_PROVEN" in script
    assert "/usr/local/bin/venvwin --root" in script


def test_qemu_has_no_host_storage_or_net_and_requires_exact_guest_markers():
    script = BOOT.read_text()
    assert '-cdrom "$ISO"' in script
    assert "-net none" in script
    assert "-boot order=d" in script
    for forbidden in ("-hda ", "-drive ", "-virtfs ", "BEAN_GUEST_READY"):
        assert forbidden not in script
    for marker in ("PUPPY_GUI_AND_OVERLAY_PRESENT", "PUPPY_VENVWIN_CAPSULE_CLI_PASS",
                   "PUPPY_GUEST_BOOT_PROVEN"):
        assert f"grep -Fxq '{marker}'" in script
    assert "persistence_after_reboot=not_tested" in script
    assert "ram_copy=not_tested" in script
    assert "windows_runner_in_guest=not_tested" in script


def test_qemu_monitor_input_simulated_without_guest_proof(tmp_path):
    import socket
    import threading
    monitor = tmp_path / "monitor.sock"
    received = []
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(monitor))
        server.listen(1)

        def recv_command():
            with server.accept()[0] as socket_client:
                socket_client.sendall(b"QEMU HMP ready\n(qemu) ")
                received.append(socket_client.recv(128))
                socket_client.sendall(b"\r\n(qemu) ")

        thread = threading.Thread(target=recv_command, daemon=True)
        thread.start()
        result = subprocess.run(
            [sys.executable, str(ROOT / "puppy-native/qemu-monitor-probe.py"),
             "--socket", str(monitor), "--action", "enter"],
            text=True, capture_output=True, timeout=10,
        )
        thread.join(timeout=3)
    assert result.returncode == 0, result.stderr
    assert received == [b"sendkey ret\n"]
    assert "QEMU_ENTER_ACKNOWLEDGED" in result.stdout
    assert "PUPPY_GUEST_BOOT_PROVEN" not in result.stdout


def test_qemu_screendump_never_counts_as_saved_without_real_frame(tmp_path):
    import socket
    import threading
    monitor = tmp_path / "monitor.sock"
    received = []
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(monitor))
        server.listen(1)

        def serve():
            with server.accept()[0] as client:
                client.sendall(b"QEMU monitor ready\n(qemu) ")
                received.append(client.recv(512))
                client.sendall(b"\r\n(qemu) ")

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        result = subprocess.run(
            [sys.executable, str(ROOT / "puppy-native/qemu-monitor-probe.py"),
             "--socket", str(monitor), "--action", "screen",
             "--output", str(tmp_path / "frame.ppm")],
            text=True, capture_output=True, timeout=10,
        )
        thread.join(timeout=3)
    assert received and received[0].startswith(b"screendump ")
    assert result.returncode != 0
    assert "frame was not saved" in result.stderr
    assert not (tmp_path / "frame.ppm").exists()


def test_application_engine_still_available_from_repo_source(tmp_path):
    from venvwin.cli import main
    import contextlib
    import io
    root = tmp_path / "capsules"
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["--root", str(root), "init"]) == 0
        assert main(["--root", str(root), "list"]) == 0
    assert root.exists()


def test_hmp_split_banner_must_finish_before_command_ack(tmp_path):
    import socket
    import threading
    import time
    monitor = tmp_path / "split.sock"
    received = []
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(monitor))
        server.listen(1)
        def serve():
            with server.accept()[0] as peer:
                peer.sendall(b"QEMU host monitor banner\n")
                time.sleep(0.03)
                peer.sendall(b"(qemu) ")
                received.append(peer.recv(256))
                time.sleep(0.05)
                peer.sendall(b"\r\n(qemu) ")
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        result = subprocess.run(
            [sys.executable, str(ROOT / "puppy-native/qemu-monitor-probe.py"),
             "--socket", str(monitor), "--action", "enter"],
            text=True, capture_output=True, timeout=10)
        thread.join(timeout=3)
    assert result.returncode == 0, result.stderr
    assert received == [b"sendkey ret\n"]
    assert "QEMU_ENTER_ACKNOWLEDGED" in result.stdout


def test_hmp_screenshot_requires_actual_file_after_full_command_response(tmp_path):
    import socket
    import threading
    output = tmp_path / "proof.ppm"
    monitor = tmp_path / "screen.sock"
    received = []
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(monitor))
        server.listen(1)
        def serve():
            with server.accept()[0] as peer:
                peer.sendall(b"QEMU host monitor\n(qemu) ")
                command = peer.recv(4096)
                received.append(command)
                output.write_bytes(b"P6\n1 1\n255\n" + b"\x00" * 200)
                peer.sendall(b"\r\n(qemu) ")
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        result = subprocess.run(
            [sys.executable, str(ROOT / "puppy-native/qemu-monitor-probe.py"),
             "--socket", str(monitor), "--action", "screen",
             "--output", str(output)],
            text=True, capture_output=True, timeout=10)
        thread.join(timeout=3)
    assert result.returncode == 0, result.stderr
    assert received == [("screendump " + str(output) + "\n").encode()]
    assert "QEMU_SCREEN_SAVED" in result.stdout
    assert output.stat().st_size >= 128
    assert "PUPPY_GUEST_BOOT_PROVEN" not in result.stdout
