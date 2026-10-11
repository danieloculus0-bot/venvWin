"""Prevent publishing a GRUB-only live ISO without a Linux kernel.

The original October 10 image had /live/filesystem.squashfs but no vmlinuz
or initrd. These tests keep the build configuration and fail-closed gates
from regressing. No ISO build is performed by this test.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "venvwin-portable" / "build-iso.sh"
RELEASE_GATE = ROOT / "venvwin-portable" / "build-flash-ready-standard.sh"


def test_bash_syntax():
    for script in (BUILDER, RELEASE_GATE):
        subprocess.run(["bash", "-n", str(script)], check=True)


def test_live_build_does_not_disable_the_kernel():
    text = BUILDER.read_text()
    assert "--linux-packages linux-image" in text
    assert "--linux-flavours amd64" in text
    assert "--linux-packages none" not in text
    assert "--linux-flavours none" not in text
    assert "linux-image-amd64" in text


def test_fail_closed_kernel_check_precedes_publishing():
    text = BUILDER.read_text()
    copy = text.index('cp "${ISO_PATH}" "${OUTPUT_ISO}"')
    for guard in ("ISO_KERNEL_MISSING", "ISO_INITRD_MISSING",
                  "ISO_SQUASHFS_MISSING", "ISO_BOOT_FILES_PRESENT"):
        assert guard in text
        assert text.index(guard) < copy
    assert "-find / -type f -exec echo --" in text
    assert "sed \"s/^'//;s/'$//\"" in text


def test_flash_ready_inspects_real_unquoted_boot_paths():
    source = RELEASE_GATE.read_text()
    assert "-find / -type f -exec echo --" in source
    assert 'sed -i "s/^' in source
    assert "STATIC_KERNEL_MISSING" in source
    assert "STATIC_INITRD_MISSING" in source
    assert "STATIC_ISO_VALID" in source
    assert source.index("STATIC_KERNEL_MISSING") < source.index("STATIC_ISO_VALID")
    assert source.index("STATIC_INITRD_MISSING") < source.index("STATIC_ISO_VALID")


def test_kernel_patterns_exclude_original_kernel_less_image():
    required = {
        "kernel": r"^/live/vmlinuz([.-].*)?$",
        "initrd": r"^/live/initrd(\.img)?([.-].*)?$",
        "squashfs": r"^/live/filesystem.squashfs$",
    }
    missing_kernel = ["/boot/grub/grub.cfg", "/live/filesystem.squashfs"]
    assert not any(re.match(required["kernel"], x) for x in missing_kernel)
    assert not any(re.match(required["initrd"], x) for x in missing_kernel)
    known_good = ["/live/vmlinuz-6.1.0-amd64",
                  "/live/initrd.img-6.1.0-amd64",
                  "/live/filesystem.squashfs"]
    assert all(any(re.match(pattern, path) for path in known_good)
               for pattern in required.values())
