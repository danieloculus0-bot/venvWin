#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/venvwin-portable-iso"
OUT_DIR="${ROOT_DIR}/dist"
IMAGE_NAME="venvwin-portable-alpha"
WINUX_PROFILE="${WINUX_PROFILE:-standard}"
PUBLIC_PRODUCT_NAME="venvWin Portable"
INTERNAL_CODENAME="WinUx"

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is missing. Install it with: sudo apt-get install -y live-build" >&2
  exit 1
fi

case "${WINUX_PROFILE}" in
  core|standard|privacy)
    ;;
  *)
    echo "Unknown WINUX_PROFILE='${WINUX_PROFILE}'. Use core, standard, or privacy." >&2
    exit 1
    ;;
esac

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}" "${OUT_DIR}"
cd "${BUILD_DIR}"

lb config \
  --mode debian \
  --distribution bookworm \
  --architectures amd64 \
  --binary-images iso-hybrid \
  --archive-areas "main contrib non-free non-free-firmware" \
  --debian-installer false \
  --memtest none \
  --bootappend-live "boot=live components quiet splash persistence" \
  --iso-application "${PUBLIC_PRODUCT_NAME}" \
  --iso-publisher "venvWin" \
  --iso-volume "VENVWIN_PORTABLE"

mkdir -p \
  config/package-lists \
  config/includes.chroot/opt/venvwin \
  config/includes.chroot/usr/local/bin \
  config/includes.chroot/usr/share/applications \
  config/includes.chroot/etc/xdg/autostart \
  config/includes.chroot/etc/skel/Desktop \
  config/hooks/normal

cat > config/package-lists/00-winux-core.list.chroot <<'EOF'
live-boot
live-config
systemd-sysv
sudo
network-manager
network-manager-gnome
xorg
lightdm
xfce4-session
xfce4-panel
xfce4-settings
xfwm4
xfdesktop4
xfce4-terminal
thunar
gvfs
mousepad
python3
python3-tk
xdg-utils
xdg-user-dirs
desktop-file-utils
shared-mime-info
curl
ca-certificates
rsync
netsurf-gtk
adwaita-icon-theme
hicolor-icon-theme
EOF

if [[ "${WINUX_PROFILE}" == "standard" || "${WINUX_PROFILE}" == "privacy" ]]; then
cat > config/package-lists/10-winux-runner.list.chroot <<'EOF'
wine
wine64
cabextract
p7zip-full
EOF
fi

if [[ "${WINUX_PROFILE}" == "privacy" ]]; then
cat > config/package-lists/20-winux-privacy.list.chroot <<'EOF'
tor
torsocks
firefox-esr
torbrowser-launcher
EOF
fi

rsync -a \
  --exclude .git \
  --exclude build \
  --exclude dist \
  --exclude .pytest_cache \
  --exclude __pycache__ \
  "${ROOT_DIR}/" "config/includes.chroot/opt/venvwin/"

cat > config/includes.chroot/usr/local/bin/venvwin <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.cli "$@"
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin

cat > config/includes.chroot/usr/local/bin/winux-first-boot-gui <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.gui_first_run
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-first-boot-gui

cat > config/includes.chroot/usr/local/bin/winux-dashboard <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.dashboard --host 127.0.0.1 --port 8787
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-dashboard

cat > config/includes.chroot/usr/local/bin/winux-dashboard-lan <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.dashboard --host 0.0.0.0 --port 8787 --lan-token
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-dashboard-lan

cat > config/includes.chroot/usr/local/bin/winux-select-capsule-store <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
python3 - <<'PY'
import json
from pathlib import Path
from venvwin.persistence import persistence_report
report = persistence_report()
chosen = report["chosen"]
Path.home().joinpath(".winux-capsule-store").write_text(chosen["path"], encoding="utf-8")
Path.home().joinpath(".winux-capsule-store-source").write_text(chosen["source"], encoding="utf-8")
Path.home().joinpath(".winux-persistence-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(chosen["path"])
PY
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-select-capsule-store

cat > config/includes.chroot/usr/local/bin/winux-private-browser <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if command -v torbrowser-launcher >/dev/null 2>&1; then
  exec torbrowser-launcher
fi

if command -v tor-browser >/dev/null 2>&1; then
  exec tor-browser
fi

if command -v torsocks >/dev/null 2>&1 && command -v firefox-esr >/dev/null 2>&1; then
  cat <<'WARN'
Tor Browser is missing. Starting Firefox ESR through torsocks as a fallback.
This is not Tor Browser. It may reduce direct exposure, but it is not hardened anonymity.
Useful for testing, not for production privacy claims.
WARN
  exec torsocks firefox-esr --new-instance --profile "$HOME/.winux-firefox-tor-fallback"
fi

cat <<'ERR'
Privacy browser is not installed in this venvWin Portable profile.
Use WINUX_PROFILE=privacy for Tor/Firefox tooling.
Core and Standard stay lean on purpose.
ERR
exit 1
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-private-browser

cat > config/includes.chroot/usr/local/bin/winux-first-run <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CAPSULE_STORE="$(/usr/local/bin/winux-select-capsule-store)"
CAPSULE_STORE_SOURCE="$(cat "$HOME/.winux-capsule-store-source" 2>/dev/null || echo unknown)"
export VENVWIN_HOME="${VENVWIN_HOME:-$CAPSULE_STORE}"
export VENVWIN_HOME_SOURCE="${VENVWIN_HOME_SOURCE:-$CAPSULE_STORE_SOURCE}"
FIRST_RUN_MARKER="$HOME/.venvwin-first-run-complete"
mkdir -p "$HOME/Desktop" "$VENVWIN_HOME"

if [[ -f "${FIRST_RUN_MARKER}" ]]; then
  exit 0
fi

venvwin init > "$HOME/Desktop/venvwin-init.txt" 2>&1 || true
venvwin associate > "$HOME/Desktop/venvwin-associate.txt" 2>&1 || true
venvwin first-run > "$HOME/Desktop/venvwin-first-run.txt" 2>&1 || true
venvwin storage > "$HOME/Desktop/venvwin-storage.txt" 2>&1 || true
venvwin doctor > "$HOME/Desktop/venvwin-doctor.txt" 2>&1 || true

date -Iseconds > "${FIRST_RUN_MARKER}"
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-first-run

cat > config/includes.chroot/etc/xdg/autostart/winux-first-run.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Run Setup
Comment=Initialize venvWin Portable capsule storage and file handlers
Exec=/usr/local/bin/winux-first-run
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/etc/xdg/autostart/winux-first-boot-gui.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Boot
Comment=Show venvWin Portable first boot setup screen
Exec=/usr/local/bin/winux-first-boot-gui
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/etc/xdg/autostart/winux-dashboard.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard Service
Comment=Start local-only venvWin Portable dashboard on port 8787
Exec=/usr/local/bin/winux-dashboard
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/usr/share/applications/winux-first-boot.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Boot
Comment=Open venvWin Portable first boot setup screen
Exec=/usr/local/bin/winux-first-boot-gui
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/winux-dashboard.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard
Comment=Open the local venvWin Portable dashboard in the browser
Exec=sh -c 'xdg-open http://127.0.0.1:8787 >/dev/null 2>&1 || sensible-browser http://127.0.0.1:8787 >/dev/null 2>&1 || netsurf-gtk http://127.0.0.1:8787'
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/winux-dashboard-lan.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard LAN Mode
Comment=Start token-protected LAN dashboard access
Exec=xfce4-terminal --command="winux-dashboard-lan"
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/winux-private-browser.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Private Browser
Comment=Privacy browser launcher. Installed only in Privacy profile.
Exec=/usr/local/bin/winux-private-browser
Terminal=false
Categories=Network;WebBrowser;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-doctor.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Doctor
Comment=Check venvWin health and setup status
Exec=xfce4-terminal --command="venvwin doctor"
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-capsules.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Capsules
Comment=Open venvWin capsule storage
Exec=sh -c 'thunar "$(cat "$HOME/.winux-capsule-store" 2>/dev/null || echo "$HOME/WinUx-Capsules")"'
Terminal=false
Categories=Utility;
EOF

install -m 0755 config/includes.chroot/usr/share/applications/winux-first-boot.desktop config/includes.chroot/etc/skel/Desktop/venvWin-First-Boot.desktop
install -m 0755 config/includes.chroot/usr/share/applications/winux-dashboard.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Dashboard.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-capsules.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Capsules.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-doctor.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Doctor.desktop
install -m 0755 config/includes.chroot/usr/share/applications/winux-private-browser.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Private-Browser.desktop

cat > config/hooks/normal/010-winux-setup.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Setting up venvWin Portable runtime hooks"

cat > /etc/profile.d/venvwin.sh <<'PROFILE'
if [ -f "$HOME/.winux-capsule-store" ]; then
  export VENVWIN_HOME="$(cat "$HOME/.winux-capsule-store")"
  if [ -f "$HOME/.winux-capsule-store-source" ]; then
    export VENVWIN_HOME_SOURCE="$(cat "$HOME/.winux-capsule-store-source")"
  fi
else
  export VENVWIN_HOME="${VENVWIN_HOME:-$HOME/WinUx-Capsules}"
  export VENVWIN_HOME_SOURCE="${VENVWIN_HOME_SOURCE:-home-fallback}"
fi
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
PROFILE

update-desktop-database /usr/share/applications || true
update-mime-database /usr/share/mime || true
EOF
chmod +x config/hooks/normal/010-winux-setup.chroot

cat > config/hooks/normal/090-winux-trim.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Trimming venvWin Portable image"
apt-get clean || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* || true
rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* || true
find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} + || true
EOF
chmod +x config/hooks/normal/090-winux-trim.chroot

sudo lb build

ISO_PATH="$(find . -maxdepth 1 \( -name 'live-image-*.iso' -o -name 'live-image-*.hybrid.iso' \) -type f | head -n 1 || true)"
if [[ -z "${ISO_PATH}" ]]; then
  echo "ISO build finished but no ISO was found. Build failed product gate." >&2
  exit 1
fi

OUTPUT_ISO="${OUT_DIR}/${IMAGE_NAME}-${WINUX_PROFILE}.iso"
cp "${ISO_PATH}" "${OUTPUT_ISO}"
sha256sum "${OUTPUT_ISO}" > "${OUTPUT_ISO}.sha256"

ISO_BYTES="$(stat -c%s "${OUTPUT_ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"
cat > "${OUT_DIR}/${IMAGE_NAME}-${WINUX_PROFILE}-manifest.txt" <<EOF
venvWin Portable ISO Manifest
profile=${WINUX_PROFILE}
public_product_name=${PUBLIC_PRODUCT_NAME}
internal_codename=${INTERNAL_CODENAME}
iso=${OUTPUT_ISO}
size_mb=${ISO_MB}
sha256_file=${OUTPUT_ISO}.sha256
leave_no_trace_default=true
default_storage=venvWin Portable USB/install drive only
boot_toram_default=false
first_boot_gui=true
dashboard=true
dashboard_url=http://127.0.0.1:8787
dashboard_bind_default=127.0.0.1
dashboard_lan_mode=explicit_token_required
first_boot_desktop_launchers=true
first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop
first_boot_proof_bundle=true
first_boot_expected_desktop_files=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Private-Browser.desktop,venvWin-Quick-Start.txt,venvWin-First-Boot-Proof.txt,venvWin-Dashboard.txt,venvWin-First-Boot-Checklist.txt,venvwin-init.txt,venvwin-associate.txt,venvwin-first-run.txt,venvwin-storage.txt,venvwin-doctor.txt
storage_source_marker=true
standard_browser=netsurf-gtk
privacy_browser_profile=privacy_only
standard_profile_policy=lean_runtime_only
product_gate=first boot must initialize storage, expose status, show setup UI, write proof bundle, show desktop launchers, and start local dashboard
EOF

echo "Built ISO: ${OUTPUT_ISO}"
echo "Size: ${ISO_MB} MB"
echo "Checksum: ${OUTPUT_ISO}.sha256"
if [[ "${ISO_MB}" -gt 3500 ]]; then
  echo "Hard concern: ISO is over 3500 MB. Trim before product release."
elif [[ "${ISO_MB}" -gt 2500 ]]; then
  echo "Soft warning: ISO is over 2500 MB. Alpha can continue, but tune size later."
fi
