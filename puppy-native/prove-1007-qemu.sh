#!/usr/bin/env bash
# Real KVM-accelerated Puppy guest evidence. Never claim boot from framebuffer alone.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/puppy-1007-baseline"
ISO="$OUT/venvwin-bookwormpup-1007-wine80-isolated-lab.iso"
SERIAL="$OUT/real-guest-serial.log"
MONITOR="$OUT/qemu-monitor.sock"
test -s "$ISO"
test -c /dev/kvm || { echo 'BLOCKER_KVM_UNAVAILABLE_DO_NOT_BURN_20_MINUTES_TCG'; exit 2; }
test -r /dev/kvm && test -w /dev/kvm || { echo BLOCKER_KVM_PERMISSIONS; exit 2; }
rm -f "$SERIAL" "$MONITOR"
qemu-system-x86_64 -accel kvm -m 4096 -smp 2 \
  -boot order=d -cdrom "$ISO" -vga std -display vnc=127.0.0.1:0 \
  -serial "file:$SERIAL" -monitor "unix:$MONITOR,server=on,wait=off" \
  -no-reboot -net none >"$OUT/qemu-stderr.log" 2>&1 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; rm -f "$MONITOR"; }
trap cleanup EXIT
monitor_cmd() {
  local command="$1"
  python3 - "$MONITOR" "$command" <<'PY'
import socket, sys, time
with socket.socket(socket.AF_UNIX) as s:
    s.settimeout(8)
    s.connect(sys.argv[1])
    s.recv(4096)
    s.sendall((sys.argv[2] + "\n").encode())
    time.sleep(.3)
PY
}
sleep 12
monitor_cmd 'sendkey ret' || echo 'BOOT_MENU_ENTER_FAILED'
for attempt in $(seq 1 38); do
  sleep 15
  if (( attempt % 5 == 0 )); then
    monitor_cmd "screendump $OUT/real-guest-frame-$attempt.ppm" || true
  fi
  if [[ -f "$SERIAL" ]] && grep -Fxq PUPPY1007_REAL_GUEST_STARTUP "$SERIAL" &&
      grep -Fxq PUPPY1007_OVERLAY_MOUNT_OBSERVED "$SERIAL" &&
      grep -Fxq PUPPY1007_WINEBOOT_PREFIX_PASS "$SERIAL" &&
      grep -Fxq PUPPY1007_WINDOWS64_EXE_PASS "$SERIAL" &&
      grep -Fxq PUPPY1007_WINDOWS32_EXE_PASS "$SERIAL" &&
      grep -Fxq PUPPY1007_REAL_GUEST_32_AND_64_PASS "$SERIAL"; then
    sha256sum "$ISO" > "$OUT/iso-test-hash.txt"
    printf 'result=GUEST_PROOF_PASS\nwin32=pass\nwin64=pass\npersistence=not_tested\nram_copy=not_tested\ninstaller_exe_msi=not_tested\n' > "$OUT/verdict.txt"
    echo 'PUPPY1007_GUEST_BOOT_WINE8_32_64_PROVEN_NOT_SIX_GATE_RELEASE'
    exit 0
  fi
  if ! kill -0 "$PID" 2>/dev/null; then echo QEMU_EXITED_EARLY; break; fi
done
monitor_cmd "screendump $OUT/real-guest-final.ppm" || true
if [[ -f "$SERIAL" ]]; then tail -n 100 "$SERIAL"; fi
printf 'result=NOT_PROVEN\n' > "$OUT/verdict.txt"
echo PUPPY1007_REAL_GUEST_EVIDENCE_NOT_COMPLETE
exit 1
