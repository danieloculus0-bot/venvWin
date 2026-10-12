#!/usr/bin/env bash
# Real Puppy guest, read-only external SFS module CD, no host writable disk.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/puppy-native"
ISO="$OUT/venvwin-puppy-native-10.0.12-experimental.iso"
MODULE="$ROOT/dist/puppy-wow64/venvwin-wow64-module-media.iso"
SERIAL="$OUT/wine-lab-guest-serial.log"
MONITOR="$OUT/wine-lab-hmp.sock"
[[ -s "$ISO" && -s "$MODULE" ]] || { echo MISSING_VERIFIED_ISO_OR_WOW64_MODULE >&2; exit 1; }
rm -f "$SERIAL" "$MONITOR" "$OUT/wine-lab-guest-desktop.png"
ACCEL=tcg
if [[ -r /dev/kvm && -w /dev/kvm ]]; then ACCEL=kvm; fi
if [[ "${VENVWIN_REQUIRE_KVM:-0}" == 1 && "$ACCEL" != kvm ]]; then
  echo "REFUSE_TCG_FALLBACK_VERIFIED_KVM_REQUIRED" >&2
  exit 1
fi
echo "PUPPY_WOW64_GUEST_ACCEL=$ACCEL"
qemu-system-x86_64 -accel "$ACCEL" -m 4096 -smp 2 -boot order=d \
  -cdrom "$ISO" -drive "file=$MODULE,media=cdrom,if=ide,index=3,readonly=on" \
  -vga std -usb -device usb-tablet -display vnc=127.0.0.1:0 -no-reboot \
  -netdev user,id=guestnet -device e1000,netdev=guestnet -serial "file:$SERIAL" \
  -monitor "unix:$MONITOR,server=on,wait=off" >"$OUT/wine-lab-qemu-stderr.log" 2>&1 &
PID=$!
cleanup() {
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
  rm -f "$MONITOR"
}
trap cleanup EXIT
sleep 9
python3 "$ROOT/puppy-native/qemu-monitor-probe.py" --socket "$MONITOR" --action enter \
  >"$OUT/wine-lab-grub-input.log" 2>&1 || true
echo QEMU_MENU_ACK_IS_NOT_GUEST_EVIDENCE
COMPLETE=0
for cycle in $(seq 1 120); do
  sleep 15
  if [[ "$cycle" == 16 || "$cycle" == 48 || "$cycle" == 90 ]]; then
    python3 "$ROOT/puppy-native/qemu-monitor-probe.py" --socket "$MONITOR" \
      --action screen --output "$OUT/wine-lab-qemu-frame-$cycle.ppm" \
      >"$OUT/wine-lab-qemu-frame-$cycle.log" 2>&1 || true
  fi
  # QEMU's 16550 UART serial file uses CRLF. Grepping Unix-exact lines
  # against raw bytes misses terminal guest markers and wastes ~20 min of CI.
  # Normalize ONLY while checking; preserve raw guest bytes for BEAN evidence.
  if [[ -s "$SERIAL" ]] && tr -d '\r' <"$SERIAL" | grep -Fxq VENVWIN_WINE_GUEST_LAB_FINISHED; then
    echo "REAL_GUEST_REPORTED_FINISHED_AT_CYCLE=$cycle"; COMPLETE=1; break
  fi
  if [[ -s "$SERIAL" ]] && tr -d '\r' <"$SERIAL" | grep -q '^VENVWIN_WINE_GUEST_BLOCKER='; then
    echo "REAL_GUEST_REPORTED_BLOCKER_AT_CYCLE=$cycle"; COMPLETE=1; break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then echo QEMU_EXITED_EARLY; break; fi
done
python3 "$ROOT/puppy-native/qemu-monitor-probe.py" --socket "$MONITOR" \
  --action screen --output "$OUT/wine-lab-final.ppm" >"$OUT/wine-lab-final-frame.log" 2>&1 || true
if [[ -s "$OUT/wine-lab-final.ppm" ]]; then
  python3 - "$OUT/wine-lab-final.ppm" "$OUT/wine-lab-guest-desktop.png" <<'PY'
from PIL import Image
import sys
im=Image.open(sys.argv[1]); im.load()
assert im.size[0]>=800 and im.size[1]>=600
im.convert('RGB').save(sys.argv[2])
print('QEMU_FRAME_CAPTURED_NOT_GUEST_PROOF', im.size)
PY
fi
echo GUEST_SERIAL_START
tail -n 120 "$SERIAL" 2>/dev/null || true
echo GUEST_SERIAL_END
[[ "$COMPLETE" == 1 ]] || { echo NO_REAL_GUEST_TERMINAL_RECEIPT >&2; exit 1; }
[[ -s "$OUT/wine-lab-guest-desktop.png" ]] || { echo NO_REAL_QEMU_FRAME >&2; exit 1; }
echo ACTUAL_GUEST_TERMINAL_RECEIPT_READY_FOR_INDEPENDENT_BEAN_IMPORT
