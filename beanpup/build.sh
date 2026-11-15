#!/usr/bin/env bash
# BEANpup minimal, non-release Puppy Linux remaster. Original venvWin remains untouched.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/beanpup dist
upstream="https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.12/BookwormPup64_10.0.12.iso"
base="build/beanpup/BookwormPup64_10.0.12.iso"
expected="ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f"
out="dist/beanpup-candidate.iso"
for tool in curl sha256sum xorriso mksquashfs; do
  command -v "$tool" >/dev/null || { echo "MISSING_BUILD_TOOL:$tool"; exit 1; }
done
if [ ! -s "$base" ]; then
  curl --fail --location --silent --show-error --retry 3 --max-time 1200 "$upstream" -o "$base.part"
  mv "$base.part" "$base"
fi
printf '%s  %s\n' "$expected" "$base" | sha256sum -c -
xorriso -indev "$base" -find / -type f -exec echo -- > dist/beanpup-base-files.txt 2>&1
slot=""
for candidate in adrv_dpupbw64_10.0.12.sfs ydrv_dpupbw64_10.0.12.sfs; do
  if ! grep -Fq "/$candidate" dist/beanpup-base-files.txt; then slot="$candidate"; break; fi
done
[ -n "$slot" ] || { echo "NO_FREE_PUPPY_ADDON_SFS_SLOT"; exit 1; }
stage="build/beanpup/staging"
rm -rf "$stage"
mkdir -p "$stage/usr/local/bin" "$stage/usr/share/applications" "$stage/root/Startup"
cat > "$stage/usr/local/bin/beanpup" <<'SCRIPT'
#!/bin/sh
case "${1:-}" in
  --version) echo "BEANpup 0.1 experimental (BookwormPup64 10.0.12)";;
  --diagnose)
    echo "BEANpup base diagnostics"
    uname -a
    echo "Mounts:"
    mount | grep -E 'aufs|overlay|squashfs' || :
    echo "Memory:"
    free -h
    ;;
  *)
    echo "BEANpup base is available. BEAN Core is NOT installed in this candidate."
    echo "Run: beanpup --diagnose"
    ;;
esac
SCRIPT
cat > "$stage/usr/share/applications/beanpup.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=BEANpup Diagnostics
Comment=Lightweight portable Linux candidate
Exec=urxvt -e /usr/local/bin/beanpup --diagnose
Terminal=false
Categories=System;
DESKTOP
# Emit proof only from a booted guest after the windowing session starts.
cat > "$stage/root/Startup/beanpup-guest-proof" <<'PROBE'
#!/bin/sh
[ -x /usr/local/bin/beanpup ] || exit 1
[ -f /usr/share/applications/beanpup.desktop ] || exit 1
/usr/local/bin/beanpup --version >/dev/null 2>&1 || exit 1
[ -n "${DISPLAY:-}" ] || exit 1
mount | grep -Eq 'aufs|overlay' || exit 1
printf '%s\n' BEANPUP_GUEST_GUI_STARTUP_PASS >> /root/beanpup-guest-proof.log
if [ -c /dev/ttyS0 ]; then
  printf '%s\n' BEANPUP_GUEST_GUI_STARTUP_PASS > /dev/ttyS0 || :
fi
PROBE
chmod +x "$stage/usr/local/bin/beanpup" "$stage/root/Startup/beanpup-guest-proof"
mksquashfs "$stage" "build/beanpup/$slot" -noappend -comp xz -no-progress
xorriso -indev "$base" -outdev "$out" -map "build/beanpup/$slot" "/$slot" \
  -boot_image any replay -commit -end > dist/beanpup-repack.log 2>&1
test -s "$out"
xorriso -indev "$out" -find "/$slot" -type f -exec echo -- > dist/beanpup-layer-list.txt 2>&1
grep -Fq "$slot" dist/beanpup-layer-list.txt
xorriso -indev "$out" -report_el_torito plain > dist/beanpup-boot-records.txt 2>&1
grep -Eiq 'boot|eltorito|isolinux|grub|efi' dist/beanpup-boot-records.txt
sha256sum "$out" > "$out.sha256"
echo "BEANPUP_STATIC_REPACK_PASS"
echo "NOT_RELEASE_READY: guest boot, persistence and physical hardware not fully verified"
