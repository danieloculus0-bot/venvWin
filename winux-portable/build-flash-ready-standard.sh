#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ISO="dist/winux-portable-alpha-standard.iso"
MANIFEST="dist/winux-portable-alpha-standard-manifest.txt"
SHA="${ISO}.sha256"
VERDICT="dist/winux-flash-ready-verdict.txt"

mkdir -p dist

cat > "${VERDICT}" <<'START'
WinUx Portable Flash-Ready Verdict
status=STARTED
START

echo "== WinUx flash-ready standard build =="

echo "Step 1: Pre-ISO readiness gate"
chmod +x winux-portable/pre-iso-readiness.sh
./winux-portable/pre-iso-readiness.sh

echo "Step 2: Build standard ISO"
chmod +x winux-portable/build-iso.sh
WINUX_PROFILE=standard ./winux-portable/build-iso.sh

echo "Step 3: Required artifact check"
test -f "${ISO}"
test -f "${SHA}"
test -f "${MANIFEST}"
sha256sum -c "${SHA}"

echo "Step 4: Required manifest flags"
grep -q '^profile=standard$' "${MANIFEST}"
grep -q '^leave_no_trace_default=true$' "${MANIFEST}"
grep -q '^first_boot_gui=true$' "${MANIFEST}"

echo "Step 5: Static ISO inspection"
for tool in xorriso qemu-system-x86_64 timeout; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "Missing required tool: ${tool}" >&2
    exit 1
  fi
done

xorriso -indev "${ISO}" -report_el_torito as_mkisofs >/tmp/winux-el-torito.txt
xorriso -indev "${ISO}" -find / -name filesystem.squashfs -print | grep -q filesystem.squashfs
xorriso -indev "${ISO}" -find / -name vmlinuz -print | head -n 1 | grep -q vmlinuz
xorriso -indev "${ISO}" -find / -name initrd.img -print | head -n 1 | grep -q initrd.img

echo "Step 6: QEMU boot smoke"
set +e
timeout 150s qemu-system-x86_64 \
  -m 2048 \
  -smp 2 \
  -cdrom "${ISO}" \
  -boot d \
  -display none \
  -serial mon:stdio \
  -no-reboot \
  -net none
code=$?
set -e

if [[ "${code}" -ne 124 ]]; then
  echo "QEMU exited early with code ${code}. Not flash-ready." >&2
  cat > "${VERDICT}" <<FAIL
WinUx Portable Flash-Ready Verdict
status=NOT_READY
reason=qemu_exited_early
qemu_exit_code=${code}
iso=${ISO}
FAIL
  exit "${code}"
fi

ISO_BYTES="$(stat -c%s "${ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"

cat > "${VERDICT}" <<PASS
WinUx Portable Flash-Ready Verdict
status=FLASH_READY
profile=standard
iso=${ISO}
sha256=${SHA}
manifest=${MANIFEST}
size_mb=${ISO_MB}
pre_iso_readiness=pass
static_iso_inspection=pass
qemu_smoke=pass
leave_no_trace_default=true
first_boot_gui=true
PASS

cat "${VERDICT}"
echo "FLASH READY: ${ISO}"
