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
# xorriso quotes its echoed ISO paths (e.g. '/live/vmlinuz'); normalize
# output before inspecting. A false-negative grep is NOT a failed guest boot.
sed -i "s/^'//;s/'$//" "$LIST"
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

# Both firmwares are tested against the same read-only -cdrom image.
# Capture screen images and serial data separately: graphics can diagnose a
# GRUB/firmware/UI issue, but only guest-emitted markers prove first run.
echo "Starting separate BIOS and UEFI display/serial probes of existing ISO"
python3 .github/scripts/diagnose-existing-iso.py --iso "$ISO" --out dist --seconds 100

export VENVWIN_VERIFY_STATIC="$static" VENVWIN_VERIFY_DIGEST="$actual"
python3 - <<'PY'
import datetime, json, os
from pathlib import Path
visual = json.loads(Path("dist/verify-qemu-visual-report.json").read_text())
probes = visual["bios_uefi"]
verified = [p["mode"] for p in probes if p["status"] == "verified"]
out = {
    "schema": "venvwin.verify-existing-iso.v2",
    "mode": "verification_only_no_build",
    "source_workflow_run": 38072277622,
    "source_artifact_id": 11678050410,
    "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "iso_sha256": os.environ["VENVWIN_VERIFY_DIGEST"],
    "checksum": "pass",
    "static_boot_structure": os.environ["VENVWIN_VERIFY_STATIC"],
    "guest_boot": "verified" if verified else "unverified",
    "first_run": "verified" if verified else "unverified",
    "verified_firmware_modes": verified,
    "firmware_diagnostics": probes,
    "screen_captures_are_not_boot_proof": True,
}
Path("dist/verify-existing-iso-result.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
PY

if grep -q '"guest_boot": "verified"' "$REPORT" && grep -q '"static_boot_structure": "pass"' "$REPORT"; then
    echo "EXISTING_ISO_BOOT_VERIFIED"
else
    echo "EXISTING_ISO_NOT_YET_VERIFIED"
    exit 1
fi
