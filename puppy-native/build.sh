#!/usr/bin/env bash
# Experimental remaster of the official Puppy ISO, without replacing its bootloader.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/puppy-native dist
base="build/puppy-native/BookwormPup64_10.0.12.iso"
upstream="https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.12/BookwormPup64_10.0.12.iso"
expected="ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f"
out="dist/venvwin-puppy-native-candidate.iso"
for command in curl sha256sum xorriso mksquashfs; do
  command -v "$command" >/dev/null || { echo "MISSING_BUILDER_TOOL: $command"; exit 1; }
done
if [ ! -f "$base" ]; then
  curl -fLsS --retry 3 --max-time 1200 "$upstream" -o "$base.part"
  mv "$base.part" "$base"
fi
printf '%s  %s\n' "$expected" "$base" | sha256sum -c -
echo "OFFICIAL_PUPPY_CHECKSUM_PASS"
xorriso -indev "$base" -report_el_torito plain > dist/puppy-original-boot.txt 2>&1
xorriso -indev "$base" -find / -type f -exec echo -- > dist/puppy-original-files.txt 2>&1
grep -Eiq 'boot|eltorito|isolinux|grub|efi' dist/puppy-original-boot.txt
slot=""
for candidate in adrv_dpupbw64_10.0.12.sfs ydrv_dpupbw64_10.0.12.sfs; do
  if ! grep -Fq "/$candidate" dist/puppy-original-files.txt; then
    slot="$candidate"
    break
  fi
done
[ -n "$slot" ] || { echo "PUPPY_SFS_SLOTS_OCCUPIED"; exit 1; }
echo "PUPPY_LAYER_SLOT=$slot"
stage="build/puppy-native/staging"
rm -rf "$stage"
mkdir -p "$stage/opt/venvwin/src" "$stage/usr/local/bin" "$stage/root/Startup" \
  "$stage/root/Desktop" "$stage/usr/share/applications"
cp -a src/. "$stage/opt/venvwin/src/"
find "$stage/opt/venvwin/src" -name __pycache__ -type d -prune -exec rm -rf {} +
cat > "$stage/usr/local/bin/venvwin" <<'EOF'
#!/bin/sh
export PYTHONPATH="/opt/venvwin/src"
command -v python3 >/dev/null 2>&1 || {
  echo "PUPPY_VENVWIN_NEEDS_PYTHON3"; exit 2;
}
exec python3 -m venvwin.cli "$@"
EOF
cat > "$stage/root/Startup/venvwin-puppy-guest-probe" <<'EOF'
#!/bin/sh
# Guest-side proof, never emitted by QEMU host or ISO builder.
emit() {
  printf '%s\n' "$1" >> /root/venvwin-puppy-proof.log
  if [ -c /dev/ttyS0 ]; then printf '%s\n' "$1" > /dev/ttyS0 || :; fi
}
[ -e /opt/venvwin/src/venvwin/cli.py ] || { emit PUPPY_GUEST_ADDON_MISSING; exit 1; }
mount | grep -Eq 'aufs|overlay' || { emit PUPPY_GUEST_LAYER_NOT_DETECTED; exit 1; }
emit PUPPY_GUEST_DESKTOP_STARTUP_PASS
if command -v python3 >/dev/null 2>&1 && /usr/local/bin/venvwin --help >/dev/null 2>&1; then
  emit PUPPY_GUEST_VENVWIN_CLI_PASS
else
  emit PUPPY_GUEST_VENVWIN_RUNTIME_BLOCKED
fi
EOF
cat > "$stage/usr/share/applications/venvwin-puppy.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Puppy Capsules
Exec=urxvt -e /usr/local/bin/venvwin --help
Terminal=false
Categories=Utility;
EOF
cp "$stage/usr/share/applications/venvwin-puppy.desktop" "$stage/root/Desktop/venvwin-puppy.desktop"
chmod +x "$stage/usr/local/bin/venvwin" "$stage/root/Startup/venvwin-puppy-guest-probe"
layer="build/puppy-native/$slot"
rm -f "$layer"
mksquashfs "$stage" "$layer" -noappend -comp xz -no-progress
test -s "$layer"
rm -f "$out"
xorriso -indev "$base" -outdev "$out" -map "$layer" "/$slot" \
  -boot_image any replay -commit -end > dist/puppy-repack.log 2>&1
test -s "$out"
xorriso -indev "$out" -find "/$slot" -type f -exec echo -- \
  > dist/puppy-repacked-files.txt 2>&1
grep -Fq "$slot" dist/puppy-repacked-files.txt
xorriso -indev "$out" -report_el_torito plain > dist/puppy-repacked-boot.txt 2>&1
grep -Eiq 'boot|eltorito|isolinux|grub|efi' dist/puppy-repacked-boot.txt
sha256sum "$out" > "$out.sha256"
echo "PUPPY_NATIVE_STATIC_REPACK_PASS"
stat -c 'PUPPY_ISO_BYTES=%s' "$out"
echo "NOT_RELEASE_READY: requires independent QEMU desktop proof and Puppy capability gates"
