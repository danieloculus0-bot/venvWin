#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ISO="dist/venvwin-portable-alpha-standard.iso"
MANIFEST="dist/venvwin-portable-alpha-standard-manifest.txt"
SHA="${ISO}.sha256"
VERDICT="dist/venvwin-flash-ready-verdict.txt"

mkdir -p dist

cat > "${VERDICT}" <<'START'
venvWin Portable Flash-Ready Verdict
status=STARTED
START

echo "== venvWin Portable flash-ready standard build =="

echo "Step 1: Pre-ISO readiness gate"
chmod +x winux-portable/pre-iso-readiness.sh
./winux-portable/pre-iso-readiness.sh

echo "Step 2: Build standard ISO"
chmod +x winux-portable/build-iso.sh
WINUX_PROFILE=standard ./winux-portable/build-iso.sh

echo "Step 3: Required artifact check"
test -f "${ISO}"
test -f "${SHA}"
test -f "${MANIFEST}"
sha256sum -c "${SHA}"

echo "Step 4: Required manifest flags"
grep -q '^profile=standard$' "${MANIFEST}"
grep -q '^public_product_name=venvWin Portable$' "${MANIFEST}"
grep -q '^internal_codename=WinUx$' "${MANIFEST}"
grep -q '^leave_no_trace_default=true$' "${MANIFEST}"
grep -q '^first_boot_gui=true$' "${MANIFEST}"
grep -q '^dashboard=true$' "${MANIFEST}"
grep -q '^dashboard_url=http://127.0.0.1:8787$' "${MANIFEST}"
grep -q '^dashboard_bind_default=127.0.0.1$' "${MANIFEST}"
grep -q '^dashboard_lan_mode=explicit_token_required$' "${MANIFEST}"
grep -q '^first_boot_desktop_launchers=true$' "${MANIFEST}"
grep -q '^first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop$' "${MANIFEST}"
grep -q '^first_boot_proof_bundle=true$' "${MANIFEST}"
grep -q '^privacy_browser_profile=privacy_only$' "${MANIFEST}"
grep -q '^standard_profile_policy=lean_runtime_only$' "${MANIFEST}"

echo "Step 5: Static ISO inspection"
for tool in xorriso qemu-system-x86_64 timeout; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "Missing required tool: ${tool}" >&2
    exit 1
  fi
done

xorriso -indev "${ISO}" -report_el_torito as_mkisofs >/tmp/venvwin-el-torito.txt
xorriso -indev "${ISO}" -find / -name filesystem.squashfs -print | grep -q filesystem.squashfs
xorriso -indev "${ISO}" -find / -name vmlinuz -print | head -n 1 | grep -q vmlinuz
xorriso -indev "${ISO}" -find / -name initrd.img -print | head -n 1 | grep -q initrd.img
xorriso -indev "${ISO}" -find / -path /usr/local/bin/venvwin -print | grep -q /usr/local/bin/venvwin
xorriso -indev "${ISO}" -find / -path /usr/local/bin/winux-first-run -print | grep -q /usr/local/bin/winux-first-run
xorriso -indev "${ISO}" -find / -path /usr/local/bin/winux-first-boot-gui -print | grep -q /usr/local/bin/winux-first-boot-gui
xorriso -indev "${ISO}" -find / -path /usr/local/bin/winux-dashboard -print | grep -q /usr/local/bin/winux-dashboard
xorriso -indev "${ISO}" -find / -path /usr/local/bin/winux-dashboard-lan -print | grep -q /usr/local/bin/winux-dashboard-lan
xorriso -indev "${ISO}" -find / -path /usr/share/applications/winux-dashboard.desktop -print | grep -q /usr/share/applications/winux-dashboard.desktop
xorriso -indev "${ISO}" -find / -path /usr/share/applications/winux-dashboard-lan.desktop -print | grep -q /usr/share/applications/winux-dashboard-lan.desktop
xorriso -indev "${ISO}" -find / -path /etc/xdg/autostart/winux-dashboard.desktop -print | grep -q /etc/xdg/autostart/winux-dashboard.desktop
xorriso -indev "${ISO}" -find / -path /etc/xdg/autostart/winux-first-boot-gui.desktop -print | grep -q /etc/xdg/autostart/winux-first-boot-gui.desktop
xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-First-Boot.desktop -print | grep -q /etc/skel/Desktop/venvWin-First-Boot.desktop
xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-Dashboard.desktop -print | grep -q /etc/skel/Desktop/venvWin-Dashboard.desktop
xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-Capsules.desktop -print | grep -q /etc/skel/Desktop/venvWin-Capsules.desktop
xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-Doctor.desktop -print | grep -q /etc/skel/Desktop/venvWin-Doctor.desktop
xorriso -indev "${ISO}" -find / -path /etc/skel/Desktop/venvWin-Private-Browser.desktop -print | grep -q /etc/skel/Desktop/venvWin-Private-Browser.desktop

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
internal_codename=WinUx
iso=${ISO}
sha256=${SHA}
manifest=${MANIFEST}
size_mb=${ISO_MB}
pre_iso_readiness=pass
manifest_flags=pass
static_iso_inspection=pass
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
