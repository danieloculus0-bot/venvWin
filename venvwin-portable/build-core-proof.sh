#!/usr/bin/env bash
# Isolated Puppy-adjacent CORE smoke. Never publish an unverified image.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
VERDICT="dist/venvwin-core-boot-verdict.txt"
SERIAL="dist/venvwin-core-qemu-serial.log"
MONITOR="/tmp/venvwin-core-qemu.sock"
LIST="dist/venvwin-core-iso-inventory.txt"
READY=0
ISO=""
PUBLISHED=0

finish() {
  if [[ "$READY" -eq 0 ]]; then
    cat > "$VERDICT" <<'FAIL'
venvWin Portable Core Boot Verdict
status=NOT_READY
reason=required_build_static_or_guest_boot_evidence_missing
no_release_iso_published=true
FAIL
    echo "CORE_BOOT_NOT_VERIFIED"
  fi
}
trap finish EXIT
rm -f "$VERDICT" "$SERIAL" "$MONITOR"
echo "Core build: isolated Debian Bookworm container"
echo "NO HOST DISK IMAGE ATTACHED TO GUEST"
echo "Step 1: existing repository readiness"
bash ./venvwin-portable/pre-iso-readiness.sh > dist/venvwin-core-preflight.log 2>&1
printf 'PRE-ISO READINESS: PASS\n' > dist/venvwin-core-preflight-pass.txt

echo "Step 2: build compact CORE only (normal 900 MiB publish guard applies)"
set +e
VENVWIN_PORTABLE_PROFILE=core bash ./venvwin-portable/build-iso.sh \
  > dist/venvwin-core-build.log 2>&1
build_code=$?
set -e
tail -n 75 dist/venvwin-core-build.log
if [[ "$build_code" -eq 0 ]]; then
  ISO="dist/venvwin-portable-alpha-core.iso"
  PUBLISHED=1
else
  # Rejected image is strictly for diagnostics and never uploaded/flashed.
  ISO="$(find build/venvwin-portable-iso -maxdepth 1 \
    \( -name 'live-image-*.iso' -o -name 'live-image-*.hybrid.iso' \) \
    -type f -print -quit || true)"
  [[ -n "$ISO" ]] || { echo "CORE_IMAGE_NOT_GENERATED; see build log" >&2; exit 1; }
  echo "BUILDER_REJECTED_CORE: exit=$build_code. Diagnostics use unpublished source ISO."
fi
test -f "$ISO"
ISO_BYTES="$(stat -c%s "$ISO")"
ISO_MIB="$(( (ISO_BYTES + 1048575) / 1048576 ))"
echo "core_iso_mib=$ISO_MIB" | tee dist/venvwin-core-size.txt
sha256sum "$ISO" > dist/venvwin-core-tested-iso.sha256
echo "core_source_build_published=$PUBLISHED" >> dist/venvwin-core-size.txt

echo "Step 3: inspect boot structure of the ACTUAL ISO"
xorriso -indev "$ISO" -find / -type f -exec echo -- 2>dist/venvwin-core-xorriso.log |
  sed "s/^'//;s/'$//" > "$LIST"
for expected in '/live/vmlinuz([.-].*)?$' '/live/initrd(\.img)?([.-].*)?$' '/live/filesystem.squashfs$'; do
  grep -Eq "^$expected" "$LIST" || {
    echo "CORE_STATIC_BOOT_MISSING=$expected" >&2
    exit 1
  }
done
echo "STATIC_CORE_BOOT_FILES_PRESENT" | tee dist/venvwin-core-static-pass.txt

echo "Step 4: guest boot probe (BIOS / isolated read-only CD / no virtual hard drive)"
ACCEL=tcg
if [[ -r /dev/kvm && -w /dev/kvm ]]; then ACCEL=kvm; fi
echo "qemu_accel=$ACCEL"
qemu-system-x86_64 -accel "$ACCEL" -m 3072 -smp 2 -boot d \
  -cdrom "$ISO" -vga std -display vnc=127.0.0.1:0 \
  -serial "file:$SERIAL" \
  -monitor "unix:$MONITOR,server=on,wait=off" \
  -no-reboot -net none \
  >dist/venvwin-core-qemu-stderr.log 2>&1 &
QEMU_PID=$!
stop_qemu() {
  kill "$QEMU_PID" 2>/dev/null || true
  wait "$QEMU_PID" 2>/dev/null || true
  rm -f "$MONITOR"
}
trap 'stop_qemu; finish' EXIT

# Screens diagnose firmware/login; only exact guest markers prove boot.
for cycle in $(seq 1 16); do
  sleep 15
  if [[ "$cycle" == 2 || "$cycle" == 6 || "$cycle" == 12 ]]; then
    SNAP="dist/venvwin-core-frame-$((cycle * 15))s.ppm"
    python3 - "$MONITOR" "$SNAP" <<'PY' || true
import socket
import sys
import time
from pathlib import Path

monitor, image = sys.argv[1:]
if not Path(monitor).exists():
    raise SystemExit("no QEMU monitor socket")
with socket.socket(socket.AF_UNIX) as channel:
    channel.settimeout(3)
    channel.connect(monitor)
    try:
        channel.recv(2048)
    except socket.timeout:
        pass
    channel.sendall(("screendump " + str(Path(image).resolve()) + "\n").encode())
    time.sleep(0.4)
    try:
        print(channel.recv(4096).decode(errors="replace")[-350:])
    except socket.timeout:
        pass
print("FRAME_EXISTS", Path(image).is_file())
PY
  fi
  if [[ -f "$SERIAL" ]] && grep -Fxq "BEAN_GUEST_READY" "$SERIAL" &&
     grep -Fxq "BEAN_GUEST_FIRST_RUN_PASS" "$SERIAL"; then
    echo "GUEST_DESKTOP_AND_FIRST_RUN_VERIFIED"
    break
  fi
  if ! kill -0 "$QEMU_PID" 2>/dev/null; then
    echo "QEMU_EXITED_EARLY" >&2
    break
  fi
done
if [[ -f "$SERIAL" ]]; then tail -n 100 "$SERIAL" || true; fi

# An unpublished diagnostic image remains NON-RELEASABLE after a size failure.
if [[ "$PUBLISHED" -ne 1 ]]; then
  echo "CORE_IMAGE_NOT_RELEASABLE: build failed size/structure publication guard" >&2
  exit 1
fi
if [[ ! -f "$SERIAL" ]] ||
   ! grep -Fxq "BEAN_GUEST_READY" "$SERIAL" ||
   ! grep -Fxq "BEAN_GUEST_FIRST_RUN_PASS" "$SERIAL"; then
  echo "CORE_GUEST_PROOF_MISSING" >&2
  exit 1
fi
cat > "$VERDICT" <<PASS
venvWin Portable Core Boot Verdict
status=CORE_GUEST_PROVEN
iso=dist/venvwin-portable-alpha-core.iso
core_iso_mib=$ISO_MIB
iso_sha256=$(sha256sum "$ISO" | cut -d' ' -f1)
static_boot=pass
guest_desktop=pass
guest_first_run=pass
host_virtual_disk=none
persistence_reboot=not_verified
copy_to_ram=not_verified
overlayfs_custom=not_verified
app_sfs_modules=not_verified
PASS
READY=1
echo "CORE_GUEST_PROVEN (NOT FULL PUPPY-READY)"
