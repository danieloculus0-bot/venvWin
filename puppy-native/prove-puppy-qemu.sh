#!/usr/bin/env bash
# One isolated native Puppy guest boot attempt. No host disk, no networking.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/dist/puppy-native"
ISO="$OUT/venvwin-puppy-native-10.0.12-experimental.iso"
SERIAL="$OUT/qemu-guest-serial.log"
MONITOR="$OUT/qemu-human-monitor.sock"
VERDICT="$OUT/puppy-guest-verdict.txt"
test -s "$ISO"
rm -f "$SERIAL" "$MONITOR" "$VERDICT"
printf 'status=NOT_PROVEN\nno_release=true\n' > "$VERDICT"
ACCEL=tcg
if [[ -r /dev/kvm && -w /dev/kvm ]]; then ACCEL=kvm; fi
echo "ISOLATED_PUPPY_QEMU_ACCEL=$ACCEL"
qemu-system-x86_64 -accel "$ACCEL" -m 3072 -smp 2 \
  -boot order=d -cdrom "$ISO" -vga std -display vnc=127.0.0.1:0 \
  -serial "file:$SERIAL" -monitor "unix:$MONITOR,server=on,wait=off" \
  -no-reboot -net none >"$OUT/qemu-stderr.log" 2>&1 &
PID=$!
cleanup() {
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
  rm -f "$MONITOR"
}
trap cleanup EXIT
sleep 10
# Drive the EXISTING upstream Puppy ISO boot menu; not a proof of guest startup.
python3 "$ROOT/puppy-native/qemu-monitor-probe.py" --socket "$MONITOR" \
  --action enter > "$OUT/qemu-grub-input.log" 2>&1 || true
cat "$OUT/qemu-grub-input.log" || true
for cycle in $(seq 1 32); do
  sleep 15
  if [[ "$cycle" == 4 || "$cycle" == 12 || "$cycle" == 24 ]]; then
    DEST="$OUT/qemu-frame-$((cycle * 15))s.ppm"
    python3 "$ROOT/puppy-native/qemu-monitor-probe.py" --socket "$MONITOR" \
      --action screen --output "$DEST" || true
  fi
  if [[ -f "$SERIAL" ]] &&
     grep -Fxq 'PUPPY_GUI_AND_OVERLAY_PRESENT' "$SERIAL" &&
     grep -Fxq 'PUPPY_VENVWIN_CAPSULE_CLI_PASS' "$SERIAL" &&
     grep -Fxq 'PUPPY_GUEST_BOOT_PROVEN' "$SERIAL"; then
    cat > "$VERDICT" <<EOF
status=PUPPY_CORE_GUEST_PROVEN
iso=$(basename "$ISO")
sha256=$(sha256sum "$ISO" | cut -d' ' -f1)
boot=pass
gui=pass
sfs_module=pass
overlay_mount=pass
capsule_cli=pass
persistence_after_reboot=not_tested
ram_copy=not_tested
windows_runner_in_guest=not_tested
EOF
    echo 'PUPPY_CORE_GUEST_PROVEN (NOT SIX-GATE PRODUCT RELEASE)'
    exit 0
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo 'PUPPY_QEMU_EXITED_EARLY' >&2
    break
  fi
done
if [[ -f "$SERIAL" ]]; then tail -n 120 "$SERIAL" || true; fi
echo 'PUPPY_GUEST_EVIDENCE_MISSING: boot or app integration is not proven' >&2
exit 1
