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
for cmd in curl sha256sum xorriso mksquashfs unsquashfs rsync rsvg-convert convert python3; do
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
mkdir -p "$STAGE/opt/venvwin/src" "$STAGE/root/Startup" "$STAGE/root/Desktop" "$STAGE/usr/local/bin" \
  "$STAGE/usr/share/applications" "$STAGE/usr/share/venvwin/theme" \
  "$STAGE/usr/share/backgrounds" "$STAGE/root/Choices/ROX-Filer" \
  "$STAGE/opt/bean/core" "$STAGE/usr/local/lib/venvwin" "$STAGE/usr/share/venvwin/assets"
# These are the ACTUAL artwork files installed in the Puppy boot screen and desktop,
# not merely mockups or unused assets. Their editable sources remain in art/*.svg.
rsvg-convert -w 800 -h 600 "$ROOT/puppy-native/art/venvwin-boot.svg" \
  -o "$OUT/venvwin-boot.png"
convert "$OUT/venvwin-boot.png" -quality 91 "$OUT/venvwin-boot.jpg"
rsvg-convert -w 1920 -h 1080 "$ROOT/puppy-native/art/venvwin-wallpaper.svg" \
  -o "$OUT/venvwin-wallpaper.png"
file "$OUT/venvwin-boot.png" "$OUT/venvwin-boot.jpg" "$OUT/venvwin-wallpaper.png"
install -m 0644 "$OUT/venvwin-wallpaper.png" "$STAGE/usr/share/backgrounds/venvwin-wallpaper.png"
# Bundle exact, independently maintained BEAN Core memory/identity/epistemic
# modules. Native offline startup works WITHOUT model weights or Internet.
rsync -a "$ROOT/puppy-native/bean-core/bean" "$STAGE/opt/bean/core/"
install -m 0755 "$ROOT/puppy-native/venvwin-bean" "$STAGE/usr/local/bin/venvwin-bean"
install -m 0644 "$ROOT/puppy-native/bean-mini-service.py" "$STAGE/usr/local/lib/venvwin/bean-mini-service.py"
install -m 0644 "$ROOT/puppy-native/art/bean-official.webp" "$STAGE/usr/share/venvwin/assets/bean-official.webp"
convert "$ROOT/puppy-native/art/bean-official.webp" "$STAGE/usr/share/venvwin/assets/bean-official.png"
install -m 0644 "$ROOT/puppy-native/venvwin-bean.desktop" "$STAGE/usr/share/applications/venvwin-bean.desktop"
install -m 0755 "$ROOT/puppy-native/venvwin-bean.desktop" "$STAGE/root/Desktop/venvwin-bean.desktop"

install -m 0644 "$ROOT/puppy-native/art/PuppyPin" "$STAGE/root/Choices/ROX-Filer/PuppyPin"
# Recover authentic JWM config from the checksum-verified upstream Puppy SFS.
mkdir -p "$OUT/brand-core" "$STAGE/etc/xdg/templates"
xorriso -osirrox on -indev "$BASE" \
  -extract /puppy_dpupbw64_10.0.12.sfs "$OUT/brand-core/main.sfs" \
  >"$OUT/brand-core-extract.log" 2>&1
unsquashfs -cat "$OUT/brand-core/main.sfs" etc/xdg/templates/_root_.jwmrc \
  >"$OUT/brand-core/jwmrc.upstream" 2>>"$OUT/brand-core-extract.log"
test -s "$OUT/brand-core/jwmrc.upstream"
python3 "$ROOT/puppy-native/brand-jwm-template.py" \
  --input "$OUT/brand-core/jwmrc.upstream" \
  --output "$OUT/brand-core/jwmrc.venvwin"
install -m 0644 "$OUT/brand-core/jwmrc.venvwin" \
  "$STAGE/etc/xdg/templates/_root_.jwmrc"

rsync -a --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' \
  "$ROOT/src/venvwin" "$STAGE/opt/venvwin/src/"
install -m 0755 "$ROOT/puppy-native/venvwin-launcher" "$STAGE/usr/local/bin/venvwin"
install -m 0755 "$ROOT/puppy-native/venvwin-guest-probe" "$STAGE/root/Startup/venvwin-guest-probe"
install -m 0755 "$ROOT/puppy-native/venvwin-diagnostic" "$STAGE/usr/local/bin/venvwin-diagnostic"
# Additive native startup + original Control Center, no heavy desktop replacement.
install -m 0755 "$ROOT/puppy-native/venvwin-session" "$STAGE/root/Startup/venvwin-session"
install -m 0755 "$ROOT/puppy-native/venvwin-control-center" "$STAGE/usr/local/bin/venvwin-control-center"
install -m 0755 "$ROOT/puppy-native/venvwin-wine" "$STAGE/usr/local/bin/venvwin-wine"
install -m 0755 "$ROOT/puppy-native/venvwin-theme-apply" "$STAGE/usr/local/bin/venvwin-theme-apply"
install -m 0644 "$ROOT/puppy-native/venvwin-gtk.css" "$STAGE/usr/share/venvwin/theme/gtk.css"
install -m 0644 "$ROOT/puppy-native/venvwin-app.desktop" "$STAGE/usr/share/applications/venvwin-app.desktop"
install -m 0644 "$ROOT/puppy-native/venvwin-wine.desktop" "$STAGE/usr/share/applications/venvwin-wine.desktop"
install -m 0644 "$ROOT/puppy-native/venvwin-app.desktop" "$STAGE/root/Desktop/venvwin-app.desktop"
install -m 0644 "$ROOT/puppy-native/WINE-AND-UI-INTEGRATION.md" "$STAGE/opt/venvwin/WINE-AND-UI-INTEGRATION.md"
install -m 0644 "$ROOT/puppy-native/RELEASE-STATUS.txt" "$STAGE/opt/venvwin/RELEASE-STATUS.txt"
rm -f "$SFS"
mksquashfs "$STAGE" "$SFS" -noappend -all-root -comp xz -b 1048576 \
  >"$OUT/mksquashfs.log" 2>&1
test -s "$SFS"
unsquashfs -l "$SFS" > "$OUT/venvwin-layer-inventory.txt"
grep -q 'squashfs-root/root/Startup/venvwin-guest-probe' "$OUT/venvwin-layer-inventory.txt"
for path in 'root/Startup/venvwin-session' 'usr/local/bin/venvwin-wine' \
            'usr/local/bin/venvwin-control-center' 'usr/share/venvwin/theme/gtk.css'; do
  grep -q "squashfs-root/$path" "$OUT/venvwin-layer-inventory.txt"
done
for art in "root/Choices/ROX-Filer/PuppyPin" "usr/share/backgrounds/venvwin-wallpaper.png" \
           "usr/local/bin/venvwin-bean" "usr/local/lib/venvwin/bean-mini-service.py" \
           "usr/share/venvwin/assets/bean-official.webp" "opt/bean/core/bean/memory/store.py" \
           "etc/xdg/templates/_root_.jwmrc"; do
  grep -q "squashfs-root/$art" "$OUT/venvwin-layer-inventory.txt"
done
rm -f "$OUTPUT"
# Extract exact upstream menu sources. Never synthesize or alter Linux kernel options.
mkdir -p "$OUT/brand-boot-input/boot/grub" "$OUT/brand-boot-output/boot/grub"
for item in /grub.cfg /boot/grub/grub.cfg /boot/grub/menu.lst; do
  destination="$OUT/brand-boot-input$item"
  mkdir -p "$(dirname "$destination")"
  xorriso -osirrox on -indev "$BASE" -extract "$item" "$destination" \
    >>"$OUT/brand-boot-extract.log" 2>&1
done
for item in /grub.cfg /boot/grub/grub.cfg; do
  python3 "$ROOT/puppy-native/brand-boot-menu.py" --kind grub \
    --input "$OUT/brand-boot-input$item" --output "$OUT/brand-boot-output$item"
done
python3 "$ROOT/puppy-native/brand-boot-menu.py" --kind bios \
  --input "$OUT/brand-boot-input/boot/grub/menu.lst" \
  --output "$OUT/brand-boot-output/boot/grub/menu.lst"
# Preserve upstream bootloader binaries/catalogs, kernel, initrd, normal/recovery
# entries and all boot parameters. Map only the two splash images and 3 menu texts.
xorriso -indev "$BASE" -outdev "$OUTPUT" \
  -map "$SFS" "/$MODULE" \
  -map "$OUT/venvwin-boot.png" "/boot/splash.png" \
  -map "$OUT/venvwin-boot.jpg" "/boot/splash.jpg" \
  -map "$OUT/brand-boot-output/grub.cfg" "/grub.cfg" \
  -map "$OUT/brand-boot-output/boot/grub/grub.cfg" "/boot/grub/grub.cfg" \
  -map "$OUT/brand-boot-output/boot/grub/menu.lst" "/boot/grub/menu.lst" \
  -boot_image any replay -commit >"$OUT/remaster-xorriso.log" 2>&1
test -s "$OUTPUT"
xorriso -indev "$OUTPUT" -find / -type f -exec echo -- 2>"$OUT/venvwin-iso-xorriso.log" |
  sed "s/^'//;s/'$//" > "$OUT/venvwin-iso-inventory.txt"
grep -q "/${MODULE}$" "$OUT/venvwin-iso-inventory.txt"
for branded in '/boot/splash.png' '/boot/splash.jpg' '/boot/grub/grub.cfg' '/boot/grub/menu.lst'; do
  grep -q "$branded" "$OUT/venvwin-iso-inventory.txt"
done
# Prove output ISO embeds the intended bitmap and menu text, not merely local files.
mkdir -p "$OUT/verify-brand"
xorriso -osirrox on -indev "$OUTPUT" -extract /boot/splash.png "$OUT/verify-brand/splash.png" \
  >"$OUT/verify-brand-extract.log" 2>&1
cmp "$OUT/venvwin-boot.png" "$OUT/verify-brand/splash.png"
xorriso -osirrox on -indev "$OUTPUT" -extract /boot/grub/grub.cfg "$OUT/verify-brand/grub.cfg" \
  >>"$OUT/verify-brand-extract.log" 2>&1
grep -q 'menuentry "venvWin Portable' "$OUT/verify-brand/grub.cfg"
echo VENVWIN_BRANDED_SPLASH_AND_BOOT_MENU_ISO_CONTENT_VERIFIED
for expected in 'vmlinuz' 'initrd' 'puppy_dpupbw64_10.0.12.sfs'; do
  grep -q "$expected" "$OUT/venvwin-iso-inventory.txt"
done
xorriso -indev "$OUTPUT" -report_el_torito plain >"$OUT/venvwin-boot-catalog.txt" 2>&1
grep -qi 'El Torito' "$OUT/venvwin-boot-catalog.txt"
sha256sum "$OUTPUT" "$SFS" > "$OUT/tested-sources.sha256"
stat -c 'ISO_BYTES=%s' "$OUTPUT" | tee "$OUT/iso-size.txt"
stat -c 'SFS_BYTES=%s' "$SFS" | tee -a "$OUT/iso-size.txt"
echo 'UPSTREAM_PUPPY_BOOT_STRUCTURE_PRESERVED (not guest boot proof)'
