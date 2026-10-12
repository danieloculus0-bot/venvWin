#!/usr/bin/env bash
# One strictly bounded real Puppy + live Wine/Windows compatibility experiment.
# Network is NAT in an ephemeral QEMU guest solely to fetch Debian packages.
# No host disk, USB, persistent save, guest SSH port-forwarding or ISO publishing.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/puppy-native"
ISO="$OUT/venvwin-puppy-native-10.0.12-experimental.iso"
SERIAL="$OUT/wine-lab-guest-serial.log"
MONITOR="$OUT/wine-lab-hmp.sock"
test -s "$ISO" || { echo MISSING_QEMU_PUPPY_ISO >&2; exit 1; }
mkdir -p "$OUT"
rm -f "$SERIAL" "$MONITOR" "$OUT/wine-lab-guest-desktop.png"
ACCEL=tcg
if [[ -r /dev/kvm && -w /dev/kvm ]]; then ACCEL=kvm; fi
echo "DISPOSABLE_REAL_PUPPY_WINE_GUEST_QEMU_ACCEL=$ACCEL"
qemu-system-x86_64 -accel "$ACCEL" -m 4096 -smp 2 \
  -boot order=d -cdrom "$ISO" -vga std -usb -device usb-tablet \
  -display vnc=127.0.0.1:0 -no-reboot \
  -netdev user,id=guestnet -device e1000,netdev=guestnet \
  -serial "file:$SERIAL" -monitor "unix:$MONITOR,server=on,wait=off" \
  >"$OUT/wine-lab-qemu-stderr.log" 2>&1 &
PID=$!
cleanup() {
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
  rm -f "$MONITOR"
}
trap cleanup EXIT
sleep 9
python3 "$ROOT/puppy-native/qemu-monitor-probe.py" \
  --socket "$MONITOR" --action enter \
  >"$OUT/wine-lab-grub-input.log" 2>&1 || true
echo "HMP_MENU_INPUT_IS_NOT_GUEST_PROOF"
COMPLETE=0
for cycle in $(seq 1 88); do
  sleep 15
  if [[ "$cycle" == 8 || "$cycle" == 32 || "$cycle" == 64 ]]; then
    python3 "$ROOT/puppy-native/qemu-monitor-probe.py" \
      --socket "$MONITOR" --action screen \
      --output "$OUT/wine-lab-qemu-frame-$cycle.ppm" \
      >"$OUT/wine-lab-qemu-frame-$cycle.log" 2>&1 || true
  fi
  if [[ -f "$SERIAL" ]] && grep -Fxq VENVWIN_WINE_GUEST_LAB_FINISHED "$SERIAL"; then
    echo "REAL_GUEST_REPORTED_LAB_FINISHED"
    COMPLETE=1
    break
  fi
  if [[ -f "$SERIAL" ]] && grep -q '^VENVWIN_WINE_GUEST_BLOCKER=' "$SERIAL"; then
    echo "REAL_GUEST_REPORTED_LAB_BLOCKER"
    COMPLETE=1
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "REAL_GUEST_QEMU_EXITED_EARLY"
    break
  fi
done
python3 "$ROOT/puppy-native/qemu-monitor-probe.py" \
  --socket "$MONITOR" --action screen \
  --output "$OUT/wine-lab-final.ppm" \
  >"$OUT/wine-lab-final-frame.log" 2>&1 || true
if [[ -s "$OUT/wine-lab-final.ppm" ]]; then
  python3 - "$OUT/wine-lab-final.ppm" "$OUT/wine-lab-guest-desktop.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1])
im.load()
assert im.width >= 800 and im.height >= 600, im.size
im.convert("RGB").save(sys.argv[2])
print("REAL_QEMU_FRAME_CONVERTED_TO_PNG", im.size)
PY
fi
echo "GUEST_SERIAL_RECEIPT_START"
tail -n 150 "$SERIAL" 2>/dev/null || true
echo "GUEST_SERIAL_RECEIPT_END"
if [[ "$COMPLETE" != 1 ]]; then
  echo "GUEST_WINE_TEST_NO_TERMINAL_RESULT_RECORDED" >&2
  exit 1
fi
[[ -s "$OUT/wine-lab-guest-desktop.png" ]] || {
  echo "NO_REAL_QEMU_DESKTOP_SCREENSHOT" >&2; exit 1; }
echo "GUEST_LAB_REACHED_TERMINAL_STATE_NOT_YET_PRODUCT_PASS"
