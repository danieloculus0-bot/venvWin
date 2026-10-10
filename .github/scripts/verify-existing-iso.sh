#!/usr/bin/env bash
# Verify an already-built ISO from a downloaded GitHub Actions artifact.
# There is deliberately NO invocation of build-iso.sh or live-build.
set -euo pipefail

ISO="dist/venvwin-portable-alpha-standard.iso"
SHA="${ISO}.sha256"
MANIFEST="dist/venvwin-portable-alpha-standard-manifest.txt"
REPORT="dist/verify-existing-iso-result.json"
QEMU_LOG="dist/verify-existing-iso-qemu-serial.log"
LIST="dist/verify-existing-iso-file-list.txt"
ELTORITO="dist/verify-existing-iso-eltorito.txt"
mkdir -p dist
rm -f "$REPORT" "$QEMU_LOG" "$LIST" "$ELTORITO"

echo "VERIFY ONLY: existing ISO (no ISO build or modification)"
test -s "$ISO" || { echo "EXISTING_ISO_MISSING"; exit 2; }
test -s "$SHA" || { echo "EXISTING_SHA256_MISSING"; exit 2; }
test -s "$MANIFEST" || { echo "EXISTING_MANIFEST_MISSING"; exit 2; }

# The builder's checksum embeds an absolute /workspace/dist source path.
# Read the original digest, compare it to exactly this retrieved ISO file.
expected="$(awk 'NR==1 { print $1 }' "$SHA")"
[[ "$expected" =~ ^[0-9a-fA-F]{64}$ ]] || { echo "BAD_CHECKSUM_FORMAT"; exit 2; }
actual="$(sha256sum "$ISO" | awk '{ print $1 }')"
[[ "${expected,,}" == "${actual,,}" ]] || { echo "CHECKSUM_MISMATCH"; exit 2; }
printf 'SOURCE_ISO_SHA256=%s\n' "$actual"
printf 'SOURCE_ISO_BYTES=%s\n' "$(stat -c%s "$ISO")"

# Independent ISO structural check using the supported xorriso -find echo action.
xorriso -indev "$ISO" -report_el_torito as_mkisofs >"$ELTORITO" 2>&1
xorriso -indev "$ISO" -find / -type f -exec echo -- >"$LIST" 2>dist/verify-existing-iso-xorriso-stderr.log
echo "ISO inventory lines: $(wc -l < "$LIST")"
echo "Boot-related paths:"
grep -Ei '(grub|isolinux|syslinux|initrd|vmlinuz|filesystem.squashfs)' "$LIST" | head -n 35 || true
if grep -Eq '/filesystem.squashfs$' "$LIST" &&
   grep -Eq '/vmlinuz($|[.-])' "$LIST" &&
   grep -Eq '/initrd(\.img)?($|[.-])' "$LIST"; then
  static="pass"
else
  static="unverified"
fi
printf 'STATIC_BOOT_STRUCTURE=%s\n' "$static"

# Always attempt guest boot: do not equate a missing static marker with an
# observed kernel failure. QEMU reads but never writes the source ISO.
echo "Starting QEMU with the already-generated ISO"
set +e
timeout 270s qemu-system-x86_64 -m 3072 -smp 2 \
  -cdrom "$ISO" -boot d -display none \
  -serial "file:$QEMU_LOG" -monitor none -no-reboot -net none
qemu_code=$?
set -e
printf 'QEMU_EXIT_CODE=%s\n' "$qemu_code"
[[ ! -f "$QEMU_LOG" ]] || tail -n 80 "$QEMU_LOG"

guest="unverified"
first_run="unverified"
if [[ -f "$QEMU_LOG" ]] && grep -Fxq 'BEAN_GUEST_READY' "$QEMU_LOG"; then guest="pass"; fi
if [[ -f "$QEMU_LOG" ]] && grep -Fxq 'BEAN_GUEST_FIRST_RUN_PASS' "$QEMU_LOG"; then first_run="pass"; fi

# Report exactly what was proven; unknown stays N/A, never fabricated zero.
export VENVWIN_VERIFY_STATIC="$static" VENVWIN_VERIFY_GUEST="$guest" \
  VENVWIN_VERIFY_FIRST="$first_run" VENVWIN_VERIFY_QEMU_CODE="$qemu_code" \
  VENVWIN_VERIFY_DIGEST="$actual"
python3 - <<'PY'
import datetime, json, os
from pathlib import Path
out = {
    "schema": "venvwin.verify-existing-iso.v1",
    "mode": "verification_only_no_build",
    "source_workflow_run": 38072277622,
    "source_artifact_id": 11678050410,
    "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "iso_sha256": os.environ["VENVWIN_VERIFY_DIGEST"],
    "checksum": "pass",
    "static_boot_structure": os.environ["VENVWIN_VERIFY_STATIC"],
    "guest_boot": os.environ["VENVWIN_VERIFY_GUEST"],
    "first_run": os.environ["VENVWIN_VERIFY_FIRST"],
    "qemu_exit_code": int(os.environ["VENVWIN_VERIFY_QEMU_CODE"]),
}
Path("dist/verify-existing-iso-result.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
PY
if [[ "$static" == "pass" && "$guest" == "pass" && "$first_run" == "pass" ]]; then
  echo "EXISTING_ISO_BOOT_VERIFIED"
else
  echo "EXISTING_ISO_NOT_YET_VERIFIED"
  exit 1
fi
