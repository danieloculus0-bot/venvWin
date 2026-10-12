"""Source-only Wine64 fallback checks. These cannot establish guest execution."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(p):
    return (ROOT / p).read_text(encoding="utf-8")

def test_exact_official_bookworm_binary_family():
    s = read("puppy-native/build-bookworm-wine64-sfs.sh")
    assert "wine64_8.0~repack-4_amd64.deb" in s
    assert "libwine_8.0~repack-4_amd64.deb" in s
    assert "4ff56d97fb84c41dd450775f03ae42208f092e822f9baa742dcde951773ecb42" in s
    assert "512b715f32fccf2ebec2b63f23d9d83394d30e27cc5570a8ef92c5d3627ef305" in s
    assert "sha256sum -c -" in s and "mksquashfs" in s
    assert "build-puppy.sh" not in s

def test_actual_guest_sfs_and_windows_execution_gates():
    s = read("puppy-native/venvwin-wine-bookworm-guest-lab")
    for marker in ("/dev/ttyS0", "PUPPY_GUEST_BOOT_PROVEN", "sfs_load -qc",
                   "/proc/self/mountinfo", "wine --version", "venvwin open",
                   "venvwin run", "REAL_WINDOWS_APPLICATION_LAUNCHED",
                   "VENVWIN_GUEST_WINDOWS_APP_PASS="):
        assert marker in s
    assert "dpkg --add-architecture" not in s
    assert "apt-get install wine" not in s

def test_kvm_and_nonrelease_evidence_pipeline():
    s = read(".github/workflows/puppy-bookworm-wine64-guest-once.yml")
    assert "fail-on-cache-miss: true" in s
    assert "HOST_KVM_IOCTL_VERSION" in s
    assert "VENVWIN_REQUIRE_KVM=1" in s
    assert "import_guest_wine_evidence.py" in s
    assert "build-puppy.sh" not in s
    assert "debian-pinned-packages.log" in s

def test_separate_bean_identity():
    s = read("puppy-native/prepare_bookworm_guest_fixtures.py")
    assert "official-Debian-Bookworm-wine64-8.0-repack-4" in s
    assert "venvwin-wine-bookworm-guest-lab" in s
