#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/venvwin-portable-iso"
OUT_DIR="${ROOT_DIR}/dist"
IMAGE_NAME="venvwin-portable-alpha"
PROFILE="${VENVWIN_PORTABLE_PROFILE:-standard}"
PUBLIC_PRODUCT_NAME="venvWin Portable"

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is missing. Install it with: sudo apt-get install -y live-build" >&2
  exit 1
fi

case "${PROFILE}" in
  core|standard|privacy)
    ;;
  *)
    echo "Unknown VENVWIN_PORTABLE_PROFILE='${PROFILE}'. Use core, standard, or privacy." >&2
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
  --linux-packages none \
  --linux-flavours none \
  --security false \
  --debian-installer false \
  --memtest none \
  --bootappend-live "boot=live components quiet splash persistence" \
  --iso-application "${PUBLIC_PRODUCT_NAME}" \
  --iso-publisher "venvWin" \
  --iso-volume "VENVWIN_PORTABLE"

mkdir -p \
  config/archives \
  config/package-lists \
  config/includes.chroot/opt/venvwin \
  config/includes.chroot/usr/local/bin \
  config/includes.chroot/usr/share/applications \
  config/includes.chroot/etc/xdg/autostart \
  config/includes.chroot/etc/skel/Desktop \
  config/includes.chroot/etc/skel/.config/gtk-3.0 \
  config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml \
  config/includes.chroot/etc/lightdm/lightdm.conf.d \
  config/hooks/normal

cat > config/archives/bookworm-security.list.chroot <<'EOF'
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

cat > config/archives/bookworm-security.list.binary <<'EOF'
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

cat > config/package-lists/00-venvwin-core.list.chroot <<'EOF'
linux-image-amd64
live-boot
live-config
systemd-sysv
sudo
network-manager
network-manager-gnome
wpasupplicant
wireless-tools
rfkill
pciutils
usbutils
lshw
inxi
firmware-linux
firmware-linux-nonfree
firmware-iwlwifi
firmware-realtek
firmware-atheros
firmware-brcm80211
firmware-misc-nonfree
firmware-sof-signed
xorg
lightdm
lightdm-gtk-greeter
xfce4-session
xfce4-panel
xfce4-settings
xfwm4
xfdesktop4
xfce4-terminal
thunar
gvfs
mousepad
ristretto
xarchiver
file-roller
evince
galculator
synaptic
gdebi
policykit-1
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

if [[ "${PROFILE}" == "standard" || "${PROFILE}" == "privacy" ]]; then
cat > config/package-lists/10-venvwin-runner.list.chroot <<'EOF'
wine
wine64
cabextract
p7zip-full
EOF
fi

if [[ "${PROFILE}" == "privacy" ]]; then
cat > config/package-lists/20-venvwin-privacy.list.chroot <<'EOF'
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

cat > config/includes.chroot/etc/lightdm/lightdm.conf.d/50-venvwin-live-autologin.conf <<'EOF'
[Seat:*]
autologin-user=user
autologin-user-timeout=0
user-session=xfce
greeter-session=lightdm-gtk-greeter
EOF

cat > config/includes.chroot/usr/local/bin/venvwin <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.cli "$@"
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin

cat > config/includes.chroot/usr/local/bin/venvwin-first-boot-gui <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.gui_first_run
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-first-boot-gui

cat > config/includes.chroot/usr/local/bin/venvwin-wine <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CAPSULE_STORE="$(${VENVWIN_SELECT_CAPSULE_STORE:-/usr/local/bin/venvwin-select-capsule-store} 2>/dev/null || true)"
if [[ -z "${CAPSULE_STORE}" ]]; then
  CAPSULE_STORE="${VENVWIN_HOME:-$HOME/venvWin-Capsules}"
fi
export VENVWIN_HOME="${VENVWIN_HOME:-$CAPSULE_STORE}"
export WINEPREFIX="${WINEPREFIX:-$VENVWIN_HOME/manual-wine-prefix}"
export WINEARCH="${WINEARCH:-win64}"
mkdir -p "$WINEPREFIX"

if [[ "$#" -eq 0 ]]; then
  cat <<'HELP'
venvWin Wine wrapper
Usage:
  venvwin-wine /path/to/app.exe [args...]
  venvwin-wine winecfg

EXE/MSI files are routed through venvwin open when possible; other commands run in
the isolated manual Wine prefix under the venvWin capsule store.
HELP
  exit 0
fi

case "${1,,}" in
  *.exe|*.msi)
    if [[ "$#" -eq 1 ]]; then
      exec venvwin open "$1"
    fi
    exec wine "$@"
    ;;
  winecfg) shift; exec winecfg "$@" ;;
  *) exec wine "$@" ;;
esac
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-wine

cat > config/includes.chroot/usr/local/bin/venvwin-run-windows-app <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
python3 - <<'PY'
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

root = Tk()
root.withdraw()
path = filedialog.askopenfilename(
    title="Choose a Windows app or installer",
    filetypes=[("Windows programs", "*.exe *.msi"), ("All files", "*")],
)
if not path:
    sys.exit(0)
completed = subprocess.run(["venvwin", "open", path], text=True, capture_output=True)
if completed.returncode != 0:
    messagebox.showerror("venvWin", completed.stderr or completed.stdout or "Unable to open the selected file.")
else:
    messagebox.showinfo("venvWin", completed.stdout or f"Started {Path(path).name}")
sys.exit(completed.returncode)
PY
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-run-windows-app

cat > config/includes.chroot/usr/local/bin/venvwin-dashboard <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.dashboard --host 127.0.0.1 --port 8787
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-dashboard

cat > config/includes.chroot/usr/local/bin/venvwin-dashboard-lan <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
exec python3 -m venvwin.dashboard --host 0.0.0.0 --port 8787 --lan-token
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-dashboard-lan

cat > config/includes.chroot/usr/local/bin/venvwin-select-capsule-store <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
python3 - <<'PY'
import json
from pathlib import Path
from venvwin.persistence import persistence_report
report = persistence_report()
chosen = report["chosen"]
Path.home().joinpath(".venvwin-capsule-store").write_text(chosen["path"], encoding="utf-8")
Path.home().joinpath(".venvwin-capsule-store-source").write_text(chosen["source"], encoding="utf-8")
Path.home().joinpath(".venvwin-persistence-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(chosen["path"])
PY
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-select-capsule-store

cat > config/includes.chroot/usr/local/bin/venvwin-private-browser <<'EOF'
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
  exec torsocks firefox-esr --new-instance --profile "$HOME/.venvwin-firefox-tor-fallback"
fi

cat <<'ERR'
Privacy browser is not installed in this venvWin Portable profile.
Use VENVWIN_PORTABLE_PROFILE=privacy for Tor/Firefox tooling.
Core and Standard stay lean on purpose.
ERR
exit 1
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-private-browser

cat > config/includes.chroot/usr/local/bin/venvwin-first-run <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CAPSULE_STORE="$(/usr/local/bin/venvwin-select-capsule-store)"
CAPSULE_STORE_SOURCE="$(cat "$HOME/.venvwin-capsule-store-source" 2>/dev/null || echo unknown)"
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
chmod +x config/includes.chroot/usr/local/bin/venvwin-first-run

cat > config/includes.chroot/etc/xdg/autostart/venvwin-first-run.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Run Setup
Comment=Initialize venvWin Portable capsule storage and file handlers
Exec=/usr/local/bin/venvwin-first-run
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/etc/xdg/autostart/venvwin-first-boot-gui.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Boot
Comment=Show venvWin Portable first boot setup screen
Exec=/usr/local/bin/venvwin-first-boot-gui
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/etc/xdg/autostart/venvwin-dashboard.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard Service
Comment=Start local-only venvWin Portable dashboard on port 8787
Exec=/usr/local/bin/venvwin-dashboard
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-app-manager.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin App Manager
Comment=Manage Windows app capsules and portable storage
Exec=/usr/local/bin/venvwin-first-boot-gui
Terminal=false
Categories=Utility;System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-run-windows-app.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Run Windows App
Comment=Choose an EXE or MSI and open it with venvWin
Exec=/usr/local/bin/venvwin-run-windows-app
Terminal=false
Categories=Utility;Emulator;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-file-manager.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=File Manager
Comment=Browse files with Thunar
Exec=thunar
Terminal=false
Categories=System;FileManager;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-terminal.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Terminal
Comment=Open the XFCE terminal
Exec=xfce4-terminal
Terminal=false
Categories=System;TerminalEmulator;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-power.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Shutdown / Reboot / Logout
Comment=Open session logout, reboot, and shutdown options
Exec=xfce4-session-logout
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-first-boot.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable First Boot
Comment=Open venvWin Portable first boot setup screen
Exec=/usr/local/bin/venvwin-first-boot-gui
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-dashboard.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard
Comment=Open the local venvWin Portable dashboard in the browser
Exec=sh -c 'xdg-open http://127.0.0.1:8787 >/dev/null 2>&1 || sensible-browser http://127.0.0.1:8787 >/dev/null 2>&1 || netsurf-gtk http://127.0.0.1:8787'
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-dashboard-lan.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Dashboard LAN Mode
Comment=Start token-protected LAN dashboard access
Exec=xfce4-terminal --command="venvwin-dashboard-lan"
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-software-center.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Software Center
Comment=Install and manage Debian packages with Synaptic and GDebi
Exec=sh -c 'synaptic-pkexec || pkexec synaptic || xfce4-terminal --command="sudo synaptic"'
Terminal=false
Categories=System;PackageManager;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-notepad.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Notepad
Comment=Lightweight text editor
Exec=mousepad
Terminal=false
Categories=Utility;TextEditor;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-network-settings.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Wireless & Network Settings
Comment=Manage Wi-Fi, Ethernet, and saved network connections
Exec=nm-connection-editor
Terminal=false
Categories=Network;Settings;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-hardware-check.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Hardware & Driver Check
Comment=Show detected PCI, USB, Wi-Fi, and system hardware
Exec=xfce4-terminal --hold --command="sh -c 'echo PCI DEVICES; lspci; echo; echo USB DEVICES; lsusb; echo; echo NETWORK DEVICES; nmcli device status; echo; echo SYSTEM REPORT; inxi -Fxz'"
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-private-browser.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Private Browser
Comment=Privacy browser launcher. Installed only in Privacy profile.
Exec=/usr/local/bin/venvwin-private-browser
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
Exec=sh -c 'thunar "$(cat "$HOME/.venvwin-capsule-store" 2>/dev/null || echo "$HOME/venvWin-Capsules")"'
Terminal=false
Categories=Utility;
EOF

cat > config/includes.chroot/etc/skel/.config/gtk-3.0/gtk.css <<'EOF'
/* venvWin Portable: dark Mint-style desktop with orange highlights and red warnings only. */
@define-color theme_bg_color #101010;
@define-color theme_fg_color #f4f1ea;
@define-color theme_selected_bg_color #ff8a00;
@define-color theme_selected_fg_color #111111;
button, .button { border-radius: 0; }
.warning, .error { color: #e04436; }
EOF

cat > config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Adwaita-dark"/>
    <property name="IconThemeName" type="string" value="Adwaita"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="FontName" type="string" value="Sans 10"/>
    <property name="DecorationLayout" type="string" value="menu:minimize,maximize,close"/>
  </property>
</channel>
EOF

cat > config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Default"/>
    <property name="button_layout" type="string" value="O|HMC"/>
    <property name="title_font" type="string" value="Sans Bold 10"/>
  </property>
</channel>
EOF

cat > config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="desktop-icons" type="empty">
    <property name="style" type="int" value="2"/>
  </property>
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitor0" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="rgba1" type="array"><value type="double" value="0.04"/><value type="double" value="0.04"/><value type="double" value="0.04"/><value type="double" value="1.0"/></property>
        </property>
      </property>
    </property>
  </property>
</channel>
EOF

install -m 0755 config/includes.chroot/usr/share/applications/venvwin-first-boot.desktop config/includes.chroot/etc/skel/Desktop/venvWin-First-Boot.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-app-manager.desktop config/includes.chroot/etc/skel/Desktop/venvWin-App-Manager.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-run-windows-app.desktop config/includes.chroot/etc/skel/Desktop/Run-Windows-App.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-file-manager.desktop config/includes.chroot/etc/skel/Desktop/File-Manager.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-terminal.desktop config/includes.chroot/etc/skel/Desktop/Terminal.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-power.desktop config/includes.chroot/etc/skel/Desktop/Shutdown-Reboot-Logout.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-dashboard.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Dashboard.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-capsules.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Capsules.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-doctor.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Doctor.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-private-browser.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Private-Browser.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-software-center.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Software-Center.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-notepad.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Notepad.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-network-settings.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Network-Settings.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-hardware-check.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Hardware-Check.desktop

cat > config/hooks/normal/010-venvwin-setup.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Setting up venvWin Portable runtime hooks"

cat > /etc/profile.d/venvwin.sh <<'PROFILE'
if [ -f "$HOME/.venvwin-capsule-store" ]; then
  export VENVWIN_HOME="$(cat "$HOME/.venvwin-capsule-store")"
  if [ -f "$HOME/.venvwin-capsule-store-source" ]; then
    export VENVWIN_HOME_SOURCE="$(cat "$HOME/.venvwin-capsule-store-source")"
  fi
else
  export VENVWIN_HOME="${VENVWIN_HOME:-$HOME/venvWin-Capsules}"
  export VENVWIN_HOME_SOURCE="${VENVWIN_HOME_SOURCE:-home-fallback}"
fi
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
PROFILE

update-desktop-database /usr/share/applications || true
update-mime-database /usr/share/mime || true
EOF
chmod +x config/hooks/normal/010-venvwin-setup.chroot

cat > config/hooks/normal/090-venvwin-trim.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Trimming venvWin Portable image"
apt-get clean || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* || true
rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* || true
find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} + || true
EOF
chmod +x config/hooks/normal/090-venvwin-trim.chroot

LB_CONTENTS_DIST="bookworm"
LB_CONTENTS_ARCH="amd64"
LB_CONTENTS_CACHE="cache/contents.chroot/contents.${LB_CONTENTS_DIST}.${LB_CONTENTS_ARCH}"
LB_CONTENTS_URL="https://deb.debian.org/debian/dists/${LB_CONTENTS_DIST}/main/Contents-${LB_CONTENTS_ARCH}.gz"
mkdir -p "$(dirname "${LB_CONTENTS_CACHE}")"
if [[ ! -s "${LB_CONTENTS_CACHE}" ]]; then
  echo "Preloading live-build contents cache from ${LB_CONTENTS_URL}"
  if command -v wget >/dev/null 2>&1; then
    wget -qO- "${LB_CONTENTS_URL}" | gunzip -c > "${LB_CONTENTS_CACHE}"
  else
    curl -fsSL "${LB_CONTENTS_URL}" | gunzip -c > "${LB_CONTENTS_CACHE}"
  fi
fi

test -s "${LB_CONTENTS_CACHE}"

sudo lb build

ISO_PATH="$(find . -maxdepth 1 \( -name 'live-image-*.iso' -o -name 'live-image-*.hybrid.iso' \) -type f | head -n 1 || true)"
if [[ -z "${ISO_PATH}" ]]; then
  echo "ISO build finished but no ISO was found. Build failed product gate." >&2
  exit 1
fi

OUTPUT_ISO="${OUT_DIR}/${IMAGE_NAME}-${PROFILE}.iso"
cp "${ISO_PATH}" "${OUTPUT_ISO}"
(
  cd "${OUT_DIR}"
  sha256sum "$(basename "${OUTPUT_ISO}")" > "$(basename "${OUTPUT_ISO}").sha256"
)

ISO_BYTES="$(stat -c%s "${OUTPUT_ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"
cat > "${OUT_DIR}/${IMAGE_NAME}-${PROFILE}-manifest.txt" <<EOF
venvWin Portable ISO Manifest
profile=${PROFILE}
public_product_name=${PUBLIC_PRODUCT_NAME}
iso=${OUTPUT_ISO}
size_mb=${ISO_MB}
sha256_file=${OUTPUT_ISO}.sha256
leave_no_trace_default=true
default_storage=venvWin Portable USB/install drive only
boot_toram_default=false
live_user_autologin=true
first_boot_gui=true
dashboard=true
dashboard_url=http://127.0.0.1:8787
dashboard_bind_default=127.0.0.1
dashboard_lan_mode=explicit_token_required
first_boot_desktop_launchers=true
first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-App-Manager.desktop,Run-Windows-App.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop,venvWin-Software-Center.desktop,venvWin-Notepad.desktop,venvWin-Network-Settings.desktop,venvWin-Hardware-Check.desktop,File-Manager.desktop,Terminal.desktop,Shutdown-Reboot-Logout.desktop
first_boot_proof_bundle=true
first_boot_expected_desktop_files=venvWin-First-Boot.desktop,venvWin-App-Manager.desktop,Run-Windows-App.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop,venvWin-Software-Center.desktop,venvWin-Notepad.desktop,venvWin-Network-Settings.desktop,venvWin-Hardware-Check.desktop,venvWin-Quick-Start.txt,venvWin-First-Boot-Proof.txt,venvWin-Dashboard.txt,venvWin-First-Boot-Checklist.txt,venvwin-init.txt,venvwin-associate.txt,venvwin-first-run.txt,venvwin-storage.txt,venvwin-doctor.txt
storage_source_marker=true
standard_browser=netsurf-gtk
software_center=synaptic,gdebi
notepad=mousepad
wireless_manager=network-manager,network-manager-gnome
hardware_probe_tools=pciutils,usbutils,lshw,inxi,rfkill,nmcli
firmware_bundle=firmware-linux,firmware-linux-nonfree,firmware-iwlwifi,firmware-realtek,firmware-atheros,firmware-brcm80211,firmware-misc-nonfree,firmware-sof-signed
privacy_browser_profile=privacy_only
standard_profile_policy=lean_runtime_plus_essential_desktop_tools
theme=dark_mint_style_orange_highlights_red_warnings_square_windows
venvwin_wine_wrapper=/usr/local/bin/venvwin-wine
required_tools=file_manager:thunar,terminal:xfce4-terminal,notepad:mousepad,network:network-manager-gnome,software_center:synaptic,gdebi,app_manager:venvwin-first-boot-gui,power:xfce4-session-logout
product_gate=first boot must initialize storage, expose status, show setup UI, write proof bundle, show desktop launchers, start local dashboard, expose software center, expose notepad, expose network settings, expose app manager/Wine wrapper, expose shutdown/reboot/logout, and provide hardware/driver diagnostics
EOF

echo "Built ISO: ${OUTPUT_ISO}"
echo "Size: ${ISO_MB} MB"
echo "Checksum: ${OUTPUT_ISO}.sha256"
if [[ "${ISO_MB}" -gt 3500 ]]; then
  echo "Hard concern: ISO is over 3500 MB. Trim before product release."
elif [[ "${ISO_MB}" -gt 2500 ]]; then
  echo "Soft warning: ISO is over 2500 MB. Alpha can continue, but tune size later."
fi
