"""Source-only contracts; passing these is NOT guest execution evidence."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def test_pinned_wow64_and_independent_sfs():
    source = read("puppy-native/build-wine-wow64-sfs.sh")
    assert "wine-${VERSION}-amd64-wow64.tar.xz" in source
    assert "a1fe858b45d12c9b16b91c7601d9b934f68430f7b6b95e240212ab6e2a198d8a" in source
    assert "sha256sum -c -" in source
    assert "mksquashfs" in source and "xorriso -as mkisofs" in source
    assert "build-puppy.sh" not in source

def test_real_guest_gates():
    source = read("puppy-native/venvwin-wine-wow64-guest-lab")
    for m in ("/dev/ttyS0", "PUPPY_GUEST_BOOT_PROVEN", "/proc/self/mountinfo",
              "mount -t squashfs", "wine --version", "venvwin open", "venvwin run",
              "REAL_WINDOWS_APPLICATION_LAUNCHED", "VENVWIN_GUEST_WINDOWS_APP_PASS="):
        assert m in source
    assert "apt-get" not in source and "dpkg --add-architecture" not in source

def test_readonly_module_and_independent_bean_import():
    guest = read("puppy-native/prove-wow64-qemu.sh")
    ci = read(".github/workflows/puppy-wow64-sfs-guest-once.yml")
    assert "readonly=on" in guest and '-serial "file:$SERIAL"' in guest
    assert "fail-on-cache-miss: true" in ci
    assert "import_guest_wine_evidence.py" in ci
    assert "build-puppy.sh" not in ci
    assert "apt-get install wine" not in ci

def test_new_fingerprint_runtime():
    source = read("puppy-native/prepare_wow64_guest_fixtures.py")
    assert "external-SFS-Kron4ek-wine-11.19-amd64-wow64" in source
    assert "venvwin-wine-wow64-guest-lab" in source
