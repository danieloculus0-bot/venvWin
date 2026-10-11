#!/usr/bin/env bash
# Native BookwormPup64 remix; NEVER release without actual guest boot evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/dist/puppy-native"
BASE="$OUT/BookwormPup64_10.0.12.iso"
OUTPUT="$OUT/venvwin-puppy-native-10.0.12-experimental.iso"
MODULE="ydrv_dpupbw64_10.0.12.sfs"
SFS="$OUT/$MODULE"
URL="https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.12/BookwormPup64_10.0.12.iso"
UPSTREAM_SHA256="ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f"
mkdir -p "$OUT"
for cmd in curl sha256sum xorriso mksquashfs unsquashfs rsync; do
  command -v "$cmd" >/dev/null || { echo "MISSING_TOOL=$cmd" >&2; exit 1; }
done
if [[ ! -f "$BASE" ]]; then
  curl --fail --location --retry 3 --connect-timeout 30 --max-time 1200 \
    --output "$BASE.partial" "$URL"
  mv "$BASE.partial" "$BASE"
fi
printf '%s  %s\n' "$UPSTREAM_SHA256" "$BASE" | sha256sum -c - |
  tee "$OUT/upstream-checksum.log"
echo "Inspecting authenticated upstream Puppy ISO"
xorriso -indev "$BASE" -find / -type f -exec echo -- 2>"$OUT/upstream-xorriso.log" |
  sed "s/^'//;s/'$//" > "$OUT/upstream-inventory.txt"
for expected in 'vmlinuz' 'initrd' 'puppy_dpupbw64_10.0.12.sfs'; do
  grep -q "$expected" "$OUT/upstream-inventory.txt" || {
    echo "UPSTREAM_PUPPY_PAYLOAD_MISSING=$expected" >&2; exit 1;
  }
done
if grep -Eq "/${MODULE}$" "$OUT/upstream-inventory.txt"; then
  echo "REFUSE_TO_REPLACE_EXISTING_UPSTREAM_YDRV=$MODULE" >&2
  exit 1
fi
# Native ydrv SFS layer; original bootloader, main SFS and firmware remain untouched.
STAGE="$OUT/module-stage"
rm -rf "$STAGE"
mkdir -p "$STAGE/opt/venvwin/src" "$STAGE/root/Startup" "$STAGE/usr/local/bin"
rsync -a --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' \
  "$ROOT/src/venvwin" "$STAGE/opt/venvwin/src/"
install -m 0755 "$ROOT/puppy-native/venvwin-launcher" "$STAGE/usr/local/bin/venvwin"
install -m 0755 "$ROOT/puppy-native/venvwin-guest-probe" "$STAGE/root/Startup/venvwin-guest-probe"
install -m 0644 "$ROOT/puppy-native/RELEASE-STATUS.txt" "$STAGE/opt/venvwin/RELEASE-STATUS.txt"
rm -f "$SFS"
mksquashfs "$STAGE" "$SFS" -noappend -all-root -comp xz -b 1048576 \
  >"$OUT/mksquashfs.log" 2>&1
test -s "$SFS"
unsquashfs -l "$SFS" > "$OUT/venvwin-layer-inventory.txt"
grep -q 'squashfs-root/root/Startup/venvwin-guest-probe' "$OUT/venvwin-layer-inventory.txt"
rm -f "$OUTPUT"
# Replay exact El Torito/EFI settings AFTER mapping additional layer.
xorriso -indev "$BASE" -outdev "$OUTPUT" -map "$SFS" "/$MODULE" \
  -boot_image any replay -commit >"$OUT/remaster-xorriso.log" 2>&1
test -s "$OUTPUT"
xorriso -indev "$OUTPUT" -find / -type f -exec echo -- 2>"$OUT/venvwin-iso-xorriso.log" |
  sed "s/^'//;s/'$//" > "$OUT/venvwin-iso-inventory.txt"
grep -q "/${MODULE}$" "$OUT/venvwin-iso-inventory.txt"
for expected in 'vmlinuz' 'initrd' 'puppy_dpupbw64_10.0.12.sfs'; do
  grep -q "$expected" "$OUT/venvwin-iso-inventory.txt"
done
xorriso -indev "$OUTPUT" -report_el_torito plain >"$OUT/venvwin-boot-catalog.txt" 2>&1
grep -qi 'El Torito' "$OUT/venvwin-boot-catalog.txt"
sha256sum "$OUTPUT" "$SFS" > "$OUT/tested-sources.sha256"
stat -c 'ISO_BYTES=%s' "$OUTPUT" | tee "$OUT/iso-size.txt"
stat -c 'SFS_BYTES=%s' "$SFS" | tee -a "$OUT/iso-size.txt"
echo 'UPSTREAM_PUPPY_BOOT_STRUCTURE_PRESERVED (not guest boot proof)'
