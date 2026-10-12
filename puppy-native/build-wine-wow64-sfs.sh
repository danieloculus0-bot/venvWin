#!/usr/bin/env bash
# Prepare a separately mountable, pinned Wine WoW64 SFS. Never install host Wine.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${VENVWIN_WOW64_OUT:-$ROOT/dist/puppy-wow64}"
VERSION=11.19
ARCHIVE="wine-${VERSION}-amd64-wow64.tar.xz"
SHA=a1fe858b45d12c9b16b91c7601d9b934f68430f7b6b95e240212ab6e2a198d8a
URL="https://github.com/Kron4ek/Wine-Builds/releases/download/${VERSION}/${ARCHIVE}"
MODULE="venvwin-wine-wow64-${VERSION}.sfs"
mkdir -p "$OUT"
for exe in curl sha256sum tar mksquashfs unsquashfs xorriso python3; do
  command -v "$exe" >/dev/null || { echo "MISSING_BUILD_TOOL=$exe" >&2; exit 1; }
done
if [[ ! -s "$OUT/$ARCHIVE" ]]; then
  curl --fail --location --retry 3 --connect-timeout 25 --max-time 900 \
    --output "$OUT/$ARCHIVE.partial" "$URL"
  mv "$OUT/$ARCHIVE.partial" "$OUT/$ARCHIVE"
fi
printf '%s  %s\n' "$SHA" "$OUT/$ARCHIVE" | sha256sum -c - | tee "$OUT/upstream-wine-sha256.log"
rm -rf "$OUT/extracted" "$OUT/stage"
mkdir -p "$OUT/extracted" "$OUT/stage/opt/venvwin/wine"
tar -xJf "$OUT/$ARCHIVE" -C "$OUT/extracted" --no-same-owner
mapfile -t candidates < <(find "$OUT/extracted" -type f -path '*/bin/wine' -print)
[[ "${#candidates[@]}" -eq 1 ]] || { echo "WINE_ARCHIVE_LAYOUT_AMBIGUOUS=${#candidates[@]}" >&2; exit 1; }
WINE_ROOT="$(dirname "$(dirname "${candidates[0]}")")"
[[ -d "$WINE_ROOT/lib" || -d "$WINE_ROOT/lib64" ]] || { echo WINE_RUNTIME_LIBRARIES_MISSING >&2; exit 1; }
cp -a "$WINE_ROOT/." "$OUT/stage/opt/venvwin/wine/"
cat > "$OUT/stage/opt/venvwin/WINE-WOW64-PROVENANCE.txt" <<META
upstream=Kron4ek/Wine-Builds
upstream_tag=$VERSION
archive=$ARCHIVE
archive_sha256=$SHA
source_url=$URL
architecture=amd64-wow64
status=precompiled_external_runtime_unverified_inside_puppy_until_guest_smoke
META
[[ -s "$OUT/stage/opt/venvwin/wine/bin/wine" ]]
find "$OUT/stage/opt/venvwin/wine" \( -name 'wine' -o -name 'wineserver' -o -name 'msiexec' \) -print > "$OUT/wine-binary-inventory.txt"
mksquashfs "$OUT/stage" "$OUT/$MODULE" -noappend -all-root -comp xz -b 1048576 > "$OUT/wine-squashfs-build.log" 2>&1
unsquashfs -cat "$OUT/$MODULE" opt/venvwin/WINE-WOW64-PROVENANCE.txt > "$OUT/module-provenance-verified.txt"
cmp "$OUT/stage/opt/venvwin/WINE-WOW64-PROVENANCE.txt" "$OUT/module-provenance-verified.txt"
unsquashfs -l "$OUT/$MODULE" > "$OUT/module-file-inventory.txt"
grep -Fq 'squashfs-root/opt/venvwin/wine/bin/wine' "$OUT/module-file-inventory.txt"
xorriso -as mkisofs -quiet -r -J -V VENVWIN_WOW64 \
  -o "$OUT/venvwin-wow64-module-media.iso" "$OUT/$MODULE" > "$OUT/module-iso-build.log" 2>&1
sha256sum "$OUT/$MODULE" "$OUT/venvwin-wow64-module-media.iso" > "$OUT/module-checksums.sha256"
stat -c 'MODULE_SFS_BYTES=%s' "$OUT/$MODULE"
stat -c 'MODULE_MEDIA_BYTES=%s' "$OUT/venvwin-wow64-module-media.iso"
echo 'WOW64_PINNED_ARCHIVE_VALIDATED_AND_SFS_BUILT_NOT_GUEST_PROOF'
