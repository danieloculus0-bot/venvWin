#!/usr/bin/env bash
# Build a native Bookworm ABI Wine64 SFS from Debian Bookworm's published,
# exact SHA256 pinned binary packages. Never install host Wine or build an OS.
# Supports Win64 EXE/MSI ONLY: 32-bit compatibility remains separately gated.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${VENVWIN_BOOKWORM_WINE_OUT:-$ROOT/dist/puppy-bookworm-wine}"
MODULE=venvwin-bookworm-wine64-8.0.sfs
BASE='https://deb.debian.org/debian/pool/main/w/wine'
mkdir -p "$OUT/debs" "$OUT/stage/usr/local/bin"
for tool in curl dpkg-deb sha256sum mksquashfs unsquashfs xorriso; do
  command -v "$tool" >/dev/null || { echo "REQUIRED_HOST_TOOL_MISSING=$tool" >&2; exit 1; }
done
fetch_verified() {
  local pkg="$1" sha="$2" path="$OUT/debs/$1"
  if [[ ! -s "$path" ]]; then
    curl --fail --location --retry 3 --connect-timeout 30 --max-time 800 \
      -o "$path.partial" "$BASE/$pkg"
    mv "$path.partial" "$path"
  fi
  printf '%s  %s\n' "$sha" "$path" | sha256sum -c - | tee -a "$OUT/debian-pinned-packages.log"
  dpkg-deb -x "$path" "$OUT/stage"
}
: > "$OUT/debian-pinned-packages.log"
fetch_verified 'wine64_8.0~repack-4_amd64.deb' \
  4ff56d97fb84c41dd450775f03ae42208f092e822f9baa742dcde951773ecb42
fetch_verified 'libwine_8.0~repack-4_amd64.deb' \
  512b715f32fccf2ebec2b63f23d9d83394d30e27cc5570a8ef92c5d3627ef305
fetch_verified 'wine_8.0~repack-4_all.deb' \
  79672e2f542c450fe7e7a16a930ac8787fcfa804d29c2bf37e3d33297dbe60b0
test -x "$OUT/stage/usr/lib/wine/wine64" || { echo DEBIAN_WINE64_LOADER_MISSING >&2; exit 1; }
test -d "$OUT/stage/usr/lib/x86_64-linux-gnu/wine" || { echo DEBIAN_LIBWINE_PAYLOAD_MISSING >&2; exit 1; }
# Native Linux-side Wine drivers use DT_NEEDED entries for ntdll.so and
# win32u.so. The external SFS holds these in its private x86_64-unix directory;
# BookwormPup does not add that directory to ld.so.conf when loading an SFS.
WINE_UNIX_LIBDIR="$OUT/stage/usr/lib/x86_64-linux-gnu/wine/x86_64-unix"
for native in ntdll.so win32u.so winex11.so; do
  [[ -s "$WINE_UNIX_LIBDIR/$native" ]] || {
    echo "BOOKWORM_NATIVE_WINE_MODULE_MISSING=$native" >&2; exit 1;
  }
done
cat > "$OUT/stage/usr/local/bin/wine" <<'WINE'
#!/bin/sh
# Bookworm Wine64, with ONLY its own SFS-provided Unix-side native modules.
WINE_UNIX_LIBDIR=/usr/lib/x86_64-linux-gnu/wine/x86_64-unix
[ -s "$WINE_UNIX_LIBDIR/ntdll.so" ] && [ -s "$WINE_UNIX_LIBDIR/win32u.so" ] || {
  echo BOOKWORM_WINE_NATIVE_MODULE_MISSING >&2; exit 69;
}
export LD_LIBRARY_PATH="$WINE_UNIX_LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export WINEARCH=win64
exec /usr/lib/wine/wine64 "$@"
WINE
chmod 0755 "$OUT/stage/usr/local/bin/wine"
cat > "$OUT/stage/usr/local/bin/wineboot" <<'WINEBOOT'
#!/bin/sh
exec /usr/local/bin/wine wineboot "$@"
WINEBOOT
chmod 0755 "$OUT/stage/usr/local/bin/wineboot"
cat > "$OUT/stage/usr/share/venvwin-wine-provenance.txt" <<'META'
origin=Debian Bookworm oldstable
version=8.0~repack-4
architecture=amd64
compatibility=Win64 only, not proof of 32-bit Windows support
input_deb_sha256_wine64=4ff56d97fb84c41dd450775f03ae42208f092e822f9baa742dcde951773ecb42
input_deb_sha256_libwine=512b715f32fccf2ebec2b63f23d9d83394d30e27cc5570a8ef92c5d3627ef305
input_deb_sha256_wine=79672e2f542c450fe7e7a16a930ac8787fcfa804d29c2bf37e3d33297dbe60b0
status=unverified_in_real_puppy_until_guest_receipts
META
# No stale files in module stage; one complete checksum-pinned dependency family.
mksquashfs "$OUT/stage" "$OUT/$MODULE" -noappend -all-root -comp xz -b 1048576 \
  > "$OUT/module-build.log" 2>&1
unsquashfs -cat "$OUT/$MODULE" usr/share/venvwin-wine-provenance.txt \
  > "$OUT/module-provenance-verified.txt"
cmp "$OUT/stage/usr/share/venvwin-wine-provenance.txt" "$OUT/module-provenance-verified.txt"
unsquashfs -l "$OUT/$MODULE" > "$OUT/module-file-list.txt"
grep -Fq 'squashfs-root/usr/lib/wine/wine64' "$OUT/module-file-list.txt"
grep -Fq 'squashfs-root/usr/local/bin/wine' "$OUT/module-file-list.txt"
xorriso -as mkisofs -quiet -r -J -V VENVWIN_BKWINE64 \
  -o "$OUT/bookworm-wine64-module-media.iso" "$OUT/$MODULE" > "$OUT/module-iso.log" 2>&1
sha256sum "$OUT/$MODULE" "$OUT/bookworm-wine64-module-media.iso" \
  > "$OUT/module-hashes.sha256"
stat -c 'DEBIAN_WINE64_SFS_BYTES=%s' "$OUT/$MODULE"
echo DEBIAN_BOOKWORM_WINE64_SFS_HASH_VERIFIED_NOT_GUEST_PROOF
