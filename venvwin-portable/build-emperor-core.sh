#!/usr/bin/env bash
# Produce the Puppy-adjacent core ISO candidate; never equate source tests with boot.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p dist
ISO=dist/venvwin-portable-alpha-core.iso
MANIFEST=dist/venvwin-portable-alpha-core-manifest.txt
VERDICT=dist/venvwin-emperor-core-verdict.txt
LIST=dist/venvwin-emperor-core-squashfs-list.txt
SERIAL=dist/venvwin-emperor-core-qemu-serial.log
SQUASH=/tmp/venvwin-emperor-core-filesystem.squashfs
printf 'stage=STARTED\nstatus=NOT_VERIFIED\n' > "$VERDICT"
fail() {
  printf 'stage=%s\nstatus=NOT_VERIFIED\nreason=%s\n' "$1" "$2" > "$VERDICT"
  echo "CORE_GAME_BUILD_FAILED: $1: $2" >&2
  exit 1
}
bash ./venvwin-portable/pre-iso-readiness.sh || fail preflight "Pre-ISO readiness failed"
VENVWIN_PORTABLE_PROFILE=core bash ./venvwin-portable/build-iso.sh || fail build "Core image builder failed"
test -f "$ISO" || fail artifacts "ISO missing"
test -f "$MANIFEST" || fail artifacts "Manifest missing"
sha256sum -c "$ISO.sha256" || fail checksum "ISO checksum mismatch"
grep -Fxq 'profile=core' "$MANIFEST" || fail manifest "Not a core image"
grep -Fxq 'included_games=emperor-gauntlet' "$MANIFEST" || fail manifest "Sole game was not recorded"
grep -Fxq 'included_game_engine=offline_html5_canvas_javascript' "$MANIFEST" || fail manifest "Incorrect game type"
grep -Fxq 'standard_browser=netsurf-gtk,epiphany-browser' "$MANIFEST" || fail manifest "Missing HTML5 core browser"
grep -Fxq 'other_game_sources_excluded=venvwin/frontier_trail' "$MANIFEST" || fail manifest "Second game exclusion unspecified"
for tool in xorriso unsquashfs qemu-system-x86_64 timeout; do
  command -v "$tool" >/dev/null || fail tools "Missing $tool"
done
xorriso -indev "$ISO" -find / -type f -exec echo -- > dist/venvwin-emperor-core-iso-list.txt
sed -i "s/^'//;s/'$//" dist/venvwin-emperor-core-iso-list.txt
grep -Eq '^/live/vmlinuz([.-].*)?$' dist/venvwin-emperor-core-iso-list.txt || fail iso "Kernel absent"
grep -Eq '^/live/initrd(\.img)?([.-].*)?$' dist/venvwin-emperor-core-iso-list.txt || fail iso "Initrd absent"
grep -Fxq '/live/filesystem.squashfs' dist/venvwin-emperor-core-iso-list.txt || fail iso "SquashFS absent"
xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$SQUASH" >/tmp/venvwin-emperor-core-extract.log 2>&1 || fail iso "SquashFS extraction failed"
unsquashfs -ll "$SQUASH" > "$LIST" || fail iso "SquashFS unreadable"
for path in \
  'squashfs-root/opt/venvwin/src/venvwin/games/emperor-gauntlet/play.html' \
  'squashfs-root/usr/local/bin/venvwin-emperor-gauntlet' \
  'squashfs-root/usr/share/applications/venvwin-emperor-gauntlet.desktop' \
  'squashfs-root/usr/share/pixmaps/venvwin-emperor-gauntlet.svg' \
  'squashfs-root/etc/skel/Desktop/venvWin-Emperor-Gauntlet.desktop' \
  'squashfs-root/usr/bin/epiphany' \
  'squashfs-root/usr/local/bin/venvwin-guest-probe'
do
  grep -Fq "$path" "$LIST" || fail squashfs "Missing $path"
done
if grep -Fq 'squashfs-root/usr/share/applications/venvwin-frontier-trail.desktop' "$LIST" ||
   grep -Fq 'squashfs-root/opt/venvwin/src/venvwin/frontier_trail/' "$LIST"; then
  fail squashfs "Frontier Trail unexpectedly bundled"
fi
unsquashfs -cat "$SQUASH" opt/venvwin/src/venvwin/games/emperor-gauntlet/play.html > dist/venvwin-emperor-core-extracted-game.html || fail squashfs "Cannot extract game"
grep -Fq '<title>Emperor Gauntlet' dist/venvwin-emperor-core-extracted-game.html || fail squashfs "Wrong game HTML"
printf 'stage=STATIC_PASS\nstatus=GUEST_NOT_VERIFIED\n' > "$VERDICT"
set +e
timeout 270s qemu-system-x86_64 -m 3072 -smp 2 -cdrom "$ISO" -boot d \
  -display none -serial "file:$SERIAL" -monitor none -no-reboot -net none
qemu_status=$?
set -e
if ! test -f "$SERIAL" || ! grep -Fxq 'BEAN_GUEST_READY' "$SERIAL" ||
   ! grep -Fxq 'BEAN_GUEST_FIRST_RUN_PASS' "$SERIAL"; then
  echo "QEMU exit status: $qemu_status"
  test -f "$SERIAL" && tail -n 80 "$SERIAL"
  fail guest "Guest boot/first-run proof missing, ISO remains unverified"
fi
printf 'stage=GUEST_BOOT_PASS\nstatus=BOOT_VERIFIED_GAMEPLAY_UNTESTED\nprofile=core\nincluded_games=emperor-gauntlet\n' > "$VERDICT"
echo 'EMP EROR CORE: guest boot evidence PASS; gameplay still untested'
