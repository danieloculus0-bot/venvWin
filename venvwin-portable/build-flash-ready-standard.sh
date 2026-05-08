#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ISO="dist/venvwin-portable-alpha-standard.iso"
MANIFEST="dist/venvwin-portable-alpha-standard-manifest.txt"
SHA="${ISO}.sha256"
VERDICT="dist/venvwin-flash-ready-verdict.txt"
SQUASHFS_COPY="/tmp/venvwin-filesystem.squashfs"
SQUASHFS_LIST="/tmp/venvwin-filesystem-list.txt"
ISO_FILE_LIST="/tmp/venvwin-iso-file-list.txt"
BOOT_CONFIG_TEXT="/tmp/venvwin-boot-config-text.txt"

mkdir -p dist

cat > "${VERDICT}" <<'START'
venvWin Portable Flash-Ready Verdict
status=STARTED
START

echo "== venvWin Portable flash-ready standard build =="

echo "Step 1: Pre-ISO readiness gate"
chmod +x venvwin-portable/pre-iso-readiness.sh
./venvwin-portable/pre-iso-readiness.sh

echo "Step 2: Build standard ISO"
chmod +x venvwin-portable/build-iso.sh
VENVWIN_PORTABLE_PROFILE=standard ./venvwin-portable/build-iso.sh

echo "Step 3: Required artifact check"
test -f "${ISO}"
test -f "${SHA}"
test -f "${MANIFEST}"
sha256sum -c "${SHA}"

echo "Step 4: Required manifest flags"
grep -q '^profile=standard$' "${MANIFEST}"
grep -q '^public_product_name=venvWin Portable$' "${MANIFEST}"
grep -q '^leave_no_trace_default=true$' "${MANIFEST}"
grep -q '^boot_toram_default=false$' "${MANIFEST}"
grep -q '^live_user_autologin=true$' "${MANIFEST}"
grep -q '^first_boot_gui=true$' "${MANIFEST}"
grep -q '^dashboard=true$' "${MANIFEST}"
grep -q '^dashboard_url=http://127.0.0.1:8787$' "${MANIFEST}"
grep -q '^dashboard_bind_default=127.0.0.1$' "${MANIFEST}"
grep -q '^dashboard_lan_mode=explicit_token_required$' "${MANIFEST}"
grep -q '^first_boot_desktop_launchers=true$' "${MANIFEST}"
grep -q '^first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop$' "${MANIFEST}"
grep -q '^first_boot_proof_bundle=true$' "${MANIFEST}"
grep -q '^storage_source_marker=true$' "${MANIFEST}"
grep -q '^standard_browser=netsurf-gtk$' "${MANIFEST}"
grep -q '^privacy_browser_profile=privacy_only$' "${MANIFEST}"
grep -q '^standard_profile_policy=lean_runtime_only$' "${MANIFEST}"

echo "Step 5: Static ISO inspection"
for tool in xorriso unsquashfs qemu-system-x86_64 timeout grep sed; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "Missing required tool: ${tool}" >&2
    exit 1
  fi
done

rm -f "${SQUASHFS_COPY}" "${SQUASHFS_LIST}" "${ISO_FILE_LIST}" "${BOOT_CONFIG_TEXT}"
xorriso -indev "${ISO}" -report_el_torito as_mkisofs >/tmp/venvwin-el-torito.txt
xorriso -indev "${ISO}" -find / -type f -print > "${ISO_FILE_LIST}"

BOOT_CONFIG_PATHS="$(grep -E '/(grub|isolinux|syslinux|boot).*(grub\.cfg|live\.cfg|isolinux\.cfg|txt\.cfg|syslinux\.cfg)$|/(grub\.cfg|isolinux\.cfg|syslinux\.cfg)$' "${ISO_FILE_LIST}" || true)"
if [[ -n "${BOOT_CONFIG_PATHS}" ]]; then
  while IFS= read -r boot_cfg; do
    [[ -z "${boot_cfg}" ]] && continue
    tmp_cfg="/tmp/venvwin-boot-$(basename "${boot_cfg}").txt"
    xorriso -osirrox on -indev "${ISO}" -extract "${boot_cfg}" "${tmp_cfg}" >/tmp/venvwin-boot-extract.log 2>&1 || true
    if [[ -f "${tmp_cfg}" ]]; then
      cat "${tmp_cfg}" >> "${BOOT_CONFIG_TEXT}"
      printf '\n' >> "${BOOT_CONFIG_TEXT}"
    fi
  done <<< "${BOOT_CONFIG_PATHS}"
fi

if [[ -s "${BOOT_CONFIG_TEXT}" ]] && grep -Eq '(^|[[:space:]])toram($|[[:space:]])' "${BOOT_CONFIG_TEXT}"; then
  echo "Boot config still contains toram. Not flash-ready for low-RAM portable use." >&2
  exit 1
fi

SQUASHFS_PATH="$(grep '/filesystem.squashfs$' "${ISO_FILE_LIST}" | head -n 1 || true)"
test -n "${SQUASHFS_PATH}"
xorriso -osirrox on -indev "${ISO}" -extract "${SQUASHFS_PATH}" "${SQUASHFS_COPY}" >/tmp/venvwin-squashfs-extract.log 2>&1
test -f "${SQUASHFS_COPY}"
unsquashfs -ll "${SQUASHFS_COPY}" > "${SQUASHFS_LIST}"

xorriso -indev "${ISO}" -find / -name vmlinuz -print | head -n 1 | grep -q vmlinuz
xorriso -indev "${ISO}" -find / -name initrd.img -print | head -n 1 | grep -q initrd.img

grep -q 'squashfs-root/usr/local/bin/venvwin' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-first-run' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-first-boot-gui' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-dashboard' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-dashboard-lan' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-select-capsule-store' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/local/bin/venvwin-private-browser' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/share/applications/venvwin-dashboard.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/share/applications/venvwin-dashboard-lan.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/usr/share/applications/venvwin-private-browser.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/xdg/autostart/venvwin-dashboard.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/xdg/autostart/venvwin-first-run.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/xdg/autostart/venvwin-first-boot-gui.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/lightdm/lightdm.conf.d/50-venvwin-live-autologin.conf' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/profile.d/venvwin.sh' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/skel/Desktop/venvWin-First-Boot.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/skel/Desktop/venvWin-Dashboard.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/skel/Desktop/venvWin-Capsules.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/skel/Desktop/venvWin-Doctor.desktop' "${SQUASHFS_LIST}"
grep -q 'squashfs-root/etc/skel/Desktop/venvWin-Private-Browser.desktop' "${SQUASHFS_LIST}"

echo "Step 6: QEMU boot smoke"
set +e
timeout 150s qemu-system-x86_64 \
  -m 2048 \
  -smp 2 \
  -cdrom "${ISO}" \
  -boot d \
  -display none \
  -serial mon:stdio \
  -no-reboot \
  -net none
code=$?
set -e

if [[ "${code}" -ne 124 ]]; then
  echo "QEMU exited early with code ${code}. Not flash-ready." >&2
  cat > "${VERDICT}" <<FAIL
venvWin Portable Flash-Ready Verdict
status=NOT_READY
reason=qemu_exited_early
qemu_exit_code=${code}
iso=${ISO}
FAIL
  exit "${code}"
fi

ISO_BYTES="$(stat -c%s "${ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"

cat > "${VERDICT}" <<PASS
venvWin Portable Flash-Ready Verdict
status=FLASH_READY
profile=standard
public_product_name=venvWin Portable
iso=${ISO}
sha256=${SHA}
manifest=${MANIFEST}
size_mb=${ISO_MB}
pre_iso_readiness=pass
manifest_flags=pass
static_iso_inspection=pass
squashfs_static_inspection=pass
boot_toram_absent=pass
live_user_autologin=pass
storage_source_marker=pass
qemu_smoke=pass
leave_no_trace_default=true
first_boot_gui=true
dashboard=true
dashboard_url=http://127.0.0.1:8787
dashboard_bind_default=127.0.0.1
dashboard_lan_mode=explicit_token_required
first_boot_desktop_launchers=true
first_boot_proof_bundle=true
privacy_browser_profile=privacy_only
standard_profile_policy=lean_runtime_only
PASS

cat "${VERDICT}"
echo "FLASH READY: ${ISO}"
