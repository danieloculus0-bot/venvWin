#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/venvwin-portable-iso"
OUT_DIR="${ROOT_DIR}/dist"
IMAGE_NAME="venvwin-portable-alpha"
PROFILE="${VENVWIN_PORTABLE_PROFILE:-core}"
PUBLIC_PRODUCT_NAME="venvWin Portable"

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is missing. Install it with: sudo apt-get install -y live-build" >&2
  exit 1
fi

case "${PROFILE}" in
  core|standard|privacy) ;;
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
  --bootloaders "grub-pc,grub-efi" \
  --archive-areas "main contrib non-free non-free-firmware" \
  --linux-packages linux-image \
  --linux-flavours amd64 \
  --security false \
  --debian-installer false \
  --memtest none \
  --bootappend-live "boot=live components console=tty0 console=ttyS0,115200n8" \
  --iso-application "${PUBLIC_PRODUCT_NAME}" \
  --iso-publisher "venvWin" \
  --iso-volume "VENVWIN_PORTABLE"

mkdir -p \
  config/archives \
  config/package-lists \
  config/includes.chroot/opt/venvwin \
  config/includes.chroot/usr/local/bin \
  config/includes.chroot/usr/share/applications \
  config/includes.chroot/usr/share/pixmaps \
  config/includes.chroot/etc/xdg/autostart \
  config/includes.chroot/etc/skel/Desktop \
  config/includes.chroot/etc/lightdm/lightdm.conf.d \
  config/includes.chroot/etc/systemd/system/multi-user.target.wants \
  config/hooks/normal

cat > config/archives/bookworm-security.list.chroot <<'EOF'
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

cat > config/archives/bookworm-security.list.binary <<'EOF'
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

# Puppy-adjacent core: boot, desktop, networking, Python and venvWin.
# Full office/media/repair apps stay outside the lean core build.
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
gvfs-backends
udisks2
dosfstools
mtools
mousepad
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
pciutils
usbutils
firmware-iwlwifi
firmware-realtek
firmware-atheros
firmware-brcm80211
firmware-sof-signed
pmount
usb-modeswitch
exfatprogs
ntfs-3g
ristretto
mtpaint
xarchiver
abiword
gnumeric
galculator
alsa-utils
pipewire
pipewire-pulse
wireplumber
xfce4-pulseaudio-plugin
EOF

# Core also needs a real HTML5/Canvas JavaScript engine for its one offline game.
# NetSurf is retained for simple browsing; Epiphany/WebKit renders Gauntlet.
# Standard/privacy already include Firefox ESR and avoid duplicating engines.
if [[ "${PROFILE}" == "core" ]]; then
  echo 'epiphany-browser' >> config/package-lists/00-venvwin-core.list.chroot
fi

# The existing standard/privacy ISO still includes every original package.
# True independent app SFS modules remain a separate, unverified milestone.
if [[ "${PROFILE}" == "standard" || "${PROFILE}" == "privacy" ]]; then
cat > config/package-lists/05-venvwin-utilities.list.chroot <<'EOF'
lshw
inxi
firmware-linux
firmware-linux-nonfree
firmware-misc-nonfree
mtp-tools
jmtpfs
geany
file-roller
evince
libreoffice-writer
libreoffice-calc
libreoffice-gtk3
synaptic
gdebi
firefox-esr
mpv
ffmpeg
guvcview
v4l-utils
pavucontrol
pamixer
gparted
parted
testdisk
smartmontools
gsmartcontrol
ufw
EOF
fi

if [[ "${PROFILE}" == "standard" || "${PROFILE}" == "privacy" ]]; then
cat > config/package-lists/10-venvwin-runner.list.chroot <<'EOF'
wine
wine64
cabextract
p7zip-full
tor
torsocks
torbrowser-launcher
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

# Product image receives ONLY executable application source, never the whole
# development repository (tests, workflows, documentation, build scripts, etc.).
# Only Emperor Gauntlet ships as a game; Frontier Trail remains in source control.
GAME_HTML="${ROOT_DIR}/src/venvwin/games/emperor-gauntlet/play.html"
if [[ ! -s "${GAME_HTML}" ]] || ! grep -q '<canvas' "${GAME_HTML}"; then
  echo "EMPEROR_GAUNTLET_MISSING: required vendored offline HTML5 game is absent" >&2
  exit 1
fi
rsync -a \
  --exclude 'venvwin/frontier_trail/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  "${ROOT_DIR}/src/" "config/includes.chroot/opt/venvwin/src/"
# One tiny offline introduction belongs on the USB; full developer docs do not.
install -m 0644 "${ROOT_DIR}/venvwin-portable/README.md" \
  "config/includes.chroot/opt/venvwin/README-PORTABLE.md"

# Booted-guest proof: unlike a QEMU timeout, this proves an actual user session,
# first-run desktop output, and HTTP dashboard response inside the guest.
cat > config/includes.chroot/usr/local/bin/venvwin-guest-probe <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
emit() {
  printf '%s\n' "$1" >> /var/log/venvwin-guest-proof.log
  if [[ -c /dev/ttyS0 ]]; then printf '%s\n' "$1" > /dev/ttyS0 || true; fi
}
emit 'BEAN_GUEST_STARTED'
for attempt in $(seq 1 100); do
  if [[ -f /home/user/Desktop/venvWin-First-Boot-Proof.txt ]] \
     && [[ -f /home/user/.venvwin-first-run-complete ]] \
     && pgrep -u user -f 'xfce4-session' >/dev/null 2>&1 \
     && curl -fsS --max-time 2 http://127.0.0.1:8787/api/status >/dev/null 2>&1; then
    if /usr/local/bin/venvwin --root /home/user/.local/share/venvwin list >/dev/null 2>&1; then
      emit 'BEAN_GUEST_FIRST_RUN_PASS'
      emit 'BEAN_GUEST_READY'
      exit 0
    fi
  fi
  sleep 2
done
emit 'BEAN_GUEST_NOT_READY'
exit 1
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-guest-probe

cat > config/includes.chroot/etc/systemd/system/venvwin-guest-probe.service <<'EOF'
[Unit]
Description=venvWin booted guest evidence probe
After=display-manager.service
Wants=display-manager.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/venvwin-guest-probe
TimeoutStartSec=240

[Install]
WantedBy=multi-user.target
EOF
ln -s ../venvwin-guest-probe.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/venvwin-guest-probe.service

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
Privacy browser tooling is not available in this boot image.
Use a standard/privacy venvWin Portable build or install the privacy browser package set.
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

venvwin init > "$HOME/Desktop/venvwin-init.txt" 2>&1
venvwin associate > "$HOME/Desktop/venvwin-associate.txt" 2>&1
if command -v xdg-mime >/dev/null 2>&1; then
  for kind in application/x-ms-dos-executable application/x-msdownload application/vnd.microsoft.portable-executable; do
    xdg-mime default venvwin-open-exe.desktop "$kind" >> "$HOME/Desktop/venvwin-associate.txt" 2>&1
  done
  for kind in application/x-msi application/x-ms-installer; do
    xdg-mime default venvwin-open-msi.desktop "$kind" >> "$HOME/Desktop/venvwin-associate.txt" 2>&1
  done
fi
venvwin first-run > "$HOME/Desktop/venvwin-first-run.txt" 2>&1
venvwin storage > "$HOME/Desktop/venvwin-storage.txt" 2>&1
venvwin doctor > "$HOME/Desktop/venvwin-doctor.txt" 2>&1 || true

date -Iseconds > "${FIRST_RUN_MARKER}"
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-first-run

cat > config/includes.chroot/usr/share/pixmaps/venvwin-emperor-gauntlet.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
 <rect x="5" y="5" width="118" height="118" rx="22" fill="#071826"/>
 <circle cx="95" cy="30" r="12" fill="#d9fc70"/>
 <path d="M18 92 Q64 60 110 93 L110 112 H18Z" fill="#aaf4ff"/>
 <ellipse cx="62" cy="72" rx="30" ry="43" fill="#172c3c"/>
 <ellipse cx="62" cy="78" rx="19" ry="33" fill="#f2f8fa"/>
 <ellipse cx="48" cy="48" rx="5" ry="7" fill="#f2f8fa"/>
 <ellipse cx="76" cy="48" rx="5" ry="7" fill="#f2f8fa"/>
 <circle cx="49" cy="49" r="2.2" fill="#07121c"/>
 <circle cx="75" cy="49" r="2.2" fill="#07121c"/>
 <path d="M57 57 L67 57 L62 66Z" fill="#ffd26a"/>
 <path d="M31 99 L51 105 L39 114Z M72 105 L92 99 L84 114Z" fill="#ffd26a"/>
</svg>
EOF

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
Comment=Show detected PCI, USB, Wi-Fi, audio, and system hardware
Exec=xfce4-terminal --hold --command="sh -c 'echo PCI DEVICES; lspci; echo; echo USB DEVICES; lsusb; echo; echo AUDIO DEVICES; aplay -l || true; arecord -l || true; echo; echo VIDEO DEVICES; v4l2-ctl --list-devices || true; echo; echo NETWORK DEVICES; nmcli device status; echo; echo SYSTEM REPORT; inxi -Fxz'"
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-private-browser.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Portable Private Browser
Comment=Open Tor Browser launcher or venvWin privacy fallback
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

cat > config/includes.chroot/usr/share/applications/venvwin-media-player.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Media Player
Comment=Play lightweight audio and video files with mpv
Exec=mpv
Terminal=false
Categories=AudioVideo;Player;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-audio-control.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Audio Control
Comment=Select speakers, microphones, and USB audio devices
Exec=pavucontrol
Terminal=false
Categories=AudioVideo;Settings;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-camera.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Camera Test
Comment=View and test webcams, USB cameras, and microphones
Exec=guvcview
Terminal=false
Categories=AudioVideo;Video;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-partition-manager.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Partition Manager
Comment=Open GParted for partition and rescue work
Exec=sh -c 'gparted-pkexec || pkexec gparted || xfce4-terminal --command="sudo gparted"'
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-drive-health.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Drive Health
Comment=Inspect drive SMART status
Exec=gsmartcontrol
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-file-recovery.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin File Recovery
Comment=Open TestDisk recovery utility
Exec=xfce4-terminal --command="sudo testdisk"
Terminal=false
Categories=System;
EOF

cat > config/includes.chroot/usr/local/bin/venvwin-emperor-gauntlet <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
GAME_HTML=/opt/venvwin/src/venvwin/games/emperor-gauntlet/play.html
if [[ ! -r "${GAME_HTML}" ]]; then
  echo "Emperor Gauntlet HTML asset is not installed" >&2
  exit 1
fi
# This is an offline file: no service, network, or game dependency to start.
# NetSurf is not used: this title requires modern Canvas + JavaScript.
URL="file://${GAME_HTML}"
if command -v firefox-esr >/dev/null 2>&1; then
  exec firefox-esr --new-window "${URL}"
elif command -v epiphany >/dev/null 2>&1; then
  exec epiphany --new-window "${URL}"
elif command -v chromium >/dev/null 2>&1; then
  exec chromium --new-window "${URL}"
else
  echo "An HTML5 canvas-capable browser is required (Firefox ESR, Epiphany, Chromium)" >&2
  exit 1
fi
EOF
chmod +x config/includes.chroot/usr/local/bin/venvwin-emperor-gauntlet

cat > config/includes.chroot/usr/share/applications/venvwin-emperor-gauntlet.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Emperor Gauntlet
Comment=Play the offline Antarctic arcade game, the only game bundled with venvWin Portable
Exec=/usr/local/bin/venvwin-emperor-gauntlet
Icon=venvwin-emperor-gauntlet
Terminal=false
Categories=Game;
EOF

install -m 0755 config/includes.chroot/usr/share/applications/venvwin-emperor-gauntlet.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Emperor-Gauntlet.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-first-boot.desktop config/includes.chroot/etc/skel/Desktop/venvWin-First-Boot.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-dashboard.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Dashboard.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-capsules.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Capsules.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-doctor.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Doctor.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-private-browser.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Private-Browser.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-software-center.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Software-Center.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-notepad.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Notepad.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-network-settings.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Network-Settings.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-hardware-check.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Hardware-Check.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-media-player.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Media-Player.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-audio-control.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Audio-Control.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-camera.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Camera-Test.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-partition-manager.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Partition-Manager.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-drive-health.desktop config/includes.chroot/etc/skel/Desktop/venvWin-Drive-Health.desktop
install -m 0755 config/includes.chroot/usr/share/applications/venvwin-file-recovery.desktop config/includes.chroot/etc/skel/Desktop/venvWin-File-Recovery.desktop

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

# Fail before publishing the ISO if there is no bootable live kernel/initramfs.
# GRUB + filesystem.squashfs alone is not a bootable Linux live image.
# xorriso echoes single-quoted ISO paths; strip quotes before matching.
command -v xorriso >/dev/null || { echo "xorriso is required for the ISO kernel gate" >&2; exit 1; }
ISO_BOOT_FILE_LIST="$(mktemp)"
trap 'rm -f "${ISO_BOOT_FILE_LIST}"' EXIT
xorriso -indev "${ISO_PATH}" -find / -type f -exec echo -- 2>/dev/null |
  sed "s/^'//;s/'$//" > "${ISO_BOOT_FILE_LIST}"
if ! grep -Eq '^/live/vmlinuz([.-].*)?$' "${ISO_BOOT_FILE_LIST}"; then
  echo "ISO_KERNEL_MISSING: /live/vmlinuz not found; refusing to publish an unbootable ISO" >&2
  exit 1
fi
if ! grep -Eq '^/live/initrd(\.img)?([.-].*)?$' "${ISO_BOOT_FILE_LIST}"; then
  echo "ISO_INITRD_MISSING: /live/initrd not found; refusing to publish an unbootable ISO" >&2
  exit 1
fi
if ! grep -Eq '^/live/filesystem.squashfs$' "${ISO_BOOT_FILE_LIST}"; then
  echo "ISO_SQUASHFS_MISSING: /live/filesystem.squashfs not found" >&2
  exit 1
fi
echo "ISO_BOOT_FILES_PRESENT: kernel, initrd, squashfs"

# Enforce the core size gate before writing release artifacts.
ISO_UNPUBLISHED_BYTES="$(stat -c%s "${ISO_PATH}")"
ISO_UNPUBLISHED_MB="$(( (ISO_UNPUBLISHED_BYTES + 1048575) / 1048576 ))"
if [[ "${PROFILE}" == core && "${ISO_UNPUBLISHED_MB}" -gt 900 ]]; then
  echo "CORE_SIZE_BUDGET_FAIL: core ISO exceeds 900 MiB; refusing to publish." >&2
  exit 1
elif [[ "${PROFILE}" == core && "${ISO_UNPUBLISHED_MB}" -gt 512 ]]; then
  echo "CORE_SIZE_WARNING: 512 MiB target exceeded: ${ISO_UNPUBLISHED_MB} MiB."
fi
if [[ "${PROFILE}" != core && "${ISO_UNPUBLISHED_MB}" -gt 900 ]]; then
  echo "HEAVY_PROFILE_WARNING: full legacy profile; optional SFS packaging is not implemented." >&2
fi

OUTPUT_ISO="${OUT_DIR}/${IMAGE_NAME}-${PROFILE}.iso"
cp "${ISO_PATH}" "${OUTPUT_ISO}"
sha256sum "${OUTPUT_ISO}" > "${OUTPUT_ISO}.sha256"

ISO_BYTES="$(stat -c%s "${OUTPUT_ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"
# Manifest reflects actual profile packages, never aspirational full-stack claims.
# Source, modules, guest boot and persistence are separately audited by BEAN.
if [[ "${PROFILE}" == core ]]; then
  VENVWIN_MANIFEST_STANDARD_BROWSER="netsurf-gtk,epiphany-browser"
  VENVWIN_MANIFEST_PRIVACY_BROWSER_PROFILE="not_bundled"
  VENVWIN_MANIFEST_SOFTWARE_CENTER="not_bundled"
  VENVWIN_MANIFEST_LIGHT_EDITOR="mousepad"
  VENVWIN_MANIFEST_OFFICE_TOOLS="abiword,gnumeric"
  VENVWIN_MANIFEST_PDF_VIEWER="not_bundled"
  VENVWIN_MANIFEST_MEDIA_TOOLS="not_bundled"
  VENVWIN_MANIFEST_CAMERA_TOOLS="not_bundled"
  VENVWIN_MANIFEST_AUDIO_STACK="pipewire,pipewire-pulse,wireplumber,alsa-utils,xfce4-pulseaudio-plugin"
  VENVWIN_MANIFEST_USB_SUPPORT="udisks2,gvfs-backends,pmount,usb-modeswitch,exfatprogs,ntfs-3g,dosfstools"
  VENVWIN_MANIFEST_HARDWARE_PROBE_TOOLS="pciutils,usbutils,rfkill,nmcli,aplay,arecord"
  VENVWIN_MANIFEST_RESCUE_TOOLS="not_bundled"
  VENVWIN_MANIFEST_FIRMWARE_BUNDLE="firmware-iwlwifi,firmware-realtek,firmware-atheros,firmware-brcm80211,firmware-sof-signed"
  VENVWIN_MANIFEST_STANDARD_PROFILE_POLICY="puppy_compact_core_with_opt_in_modules"
else
  VENVWIN_MANIFEST_STANDARD_BROWSER="netsurf-gtk,firefox-esr"
  VENVWIN_MANIFEST_PRIVACY_BROWSER_PROFILE="torbrowser-launcher,tor,torsocks"
  VENVWIN_MANIFEST_SOFTWARE_CENTER="synaptic,gdebi"
  VENVWIN_MANIFEST_LIGHT_EDITOR="geany"
  VENVWIN_MANIFEST_OFFICE_TOOLS="abiword,gnumeric,libreoffice-writer,libreoffice-calc"
  VENVWIN_MANIFEST_PDF_VIEWER="evince"
  VENVWIN_MANIFEST_MEDIA_TOOLS="mpv,ffmpeg"
  VENVWIN_MANIFEST_CAMERA_TOOLS="guvcview,v4l-utils"
  VENVWIN_MANIFEST_AUDIO_STACK="pipewire,pipewire-pulse,wireplumber,alsa-utils,pavucontrol,pamixer,xfce4-pulseaudio-plugin"
  VENVWIN_MANIFEST_USB_SUPPORT="udisks2,gvfs-backends,pmount,usb-modeswitch,mtp-tools,jmtpfs,exfatprogs,ntfs-3g,dosfstools"
  VENVWIN_MANIFEST_HARDWARE_PROBE_TOOLS="pciutils,usbutils,lshw,inxi,rfkill,nmcli,v4l2-ctl,aplay,arecord"
  VENVWIN_MANIFEST_RESCUE_TOOLS="gparted,parted,testdisk,smartmontools,gsmartcontrol,ufw"
  VENVWIN_MANIFEST_FIRMWARE_BUNDLE="firmware-linux,firmware-linux-nonfree,firmware-iwlwifi,firmware-realtek,firmware-atheros,firmware-brcm80211,firmware-misc-nonfree,firmware-sof-signed"
  VENVWIN_MANIFEST_STANDARD_PROFILE_POLICY="lean_runtime_plus_puppy_era_essentials"
fi

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
persistence_default=none
persistence_opt_in=true
packaged_payload=app_source_only
boot_media_policy=read_only_by_default
optional_launchers_may_require_modules=true
live_user_autologin=true
first_boot_gui=true
dashboard=true
dashboard_url=http://127.0.0.1:8787
dashboard_bind_default=127.0.0.1
dashboard_lan_mode=explicit_token_required
first_boot_desktop_launchers=true
first_boot_desktop_launchers_list=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Doctor.desktop,venvWin-Private-Browser.desktop,venvWin-Software-Center.desktop,venvWin-Notepad.desktop,venvWin-Network-Settings.desktop,venvWin-Hardware-Check.desktop,venvWin-Media-Player.desktop,venvWin-Audio-Control.desktop,venvWin-Camera-Test.desktop,venvWin-Partition-Manager.desktop,venvWin-Drive-Health.desktop,venvWin-File-Recovery.desktop,venvWin-Emperor-Gauntlet.desktop
first_boot_proof_bundle=true
first_boot_expected_desktop_files=venvWin-First-Boot.desktop,venvWin-Dashboard.desktop,venvWin-Capsules.desktop,venvWin-Private-Browser.desktop,venvWin-Software-Center.desktop,venvWin-Notepad.desktop,venvWin-Network-Settings.desktop,venvWin-Hardware-Check.desktop,venvWin-Media-Player.desktop,venvWin-Audio-Control.desktop,venvWin-Camera-Test.desktop,venvWin-Partition-Manager.desktop,venvWin-Drive-Health.desktop,venvWin-File-Recovery.desktop,venvWin-Emperor-Gauntlet.desktop,venvWin-Quick-Start.txt,venvWin-First-Boot-Proof.txt,venvWin-Dashboard.txt,venvWin-First-Boot-Checklist.txt,venvwin-init.txt,venvwin-associate.txt,venvwin-first-run.txt,venvwin-storage.txt,venvwin-doctor.txt
storage_source_marker=true
standard_browser=${VENVWIN_MANIFEST_STANDARD_BROWSER}
privacy_browser_profile=${VENVWIN_MANIFEST_PRIVACY_BROWSER_PROFILE}
software_center=${VENVWIN_MANIFEST_SOFTWARE_CENTER}
notepad=mousepad
light_editor=${VENVWIN_MANIFEST_LIGHT_EDITOR}
office_tools=${VENVWIN_MANIFEST_OFFICE_TOOLS}
pdf_viewer=${VENVWIN_MANIFEST_PDF_VIEWER}
image_tools=mtpaint,ristretto
media_tools=${VENVWIN_MANIFEST_MEDIA_TOOLS}
camera_tools=${VENVWIN_MANIFEST_CAMERA_TOOLS}
audio_stack=${VENVWIN_MANIFEST_AUDIO_STACK}
wireless_manager=network-manager,network-manager-gnome
usb_support=${VENVWIN_MANIFEST_USB_SUPPORT}
hardware_probe_tools=${VENVWIN_MANIFEST_HARDWARE_PROBE_TOOLS}
rescue_tools=${VENVWIN_MANIFEST_RESCUE_TOOLS}
included_games=emperor-gauntlet
included_game_engine=offline_html5_canvas_javascript
included_game_source=FUN@442c87250a391ef74ead84db8a98821a0f512291
included_game_asset=src/venvwin/games/emperor-gauntlet/play.html
included_game_launchers=venvwin-emperor-gauntlet.desktop
included_game_icons=venvwin-emperor-gauntlet.svg
other_game_sources_excluded=venvwin/frontier_trail
firmware_bundle=${VENVWIN_MANIFEST_FIRMWARE_BUNDLE}
standard_profile_policy=${VENVWIN_MANIFEST_STANDARD_PROFILE_POLICY}
excluded_bloat=inkscape,cd_tools,dvd_tools,burners,audio_editors,extra_games_except_emperor_gauntlet,full_libreoffice_suite,libreoffice-impress,libreoffice-draw,libreoffice-base,developer_stack
product_gate=first boot must initialize storage, expose status, show setup UI, write proof bundle, show desktop launchers, start local dashboard, expose software center, expose notepad, expose network settings, provide audio/camera/media tools, provide document and CSV compatibility, expose offline Emperor Gauntlet as the only bundled game, with a desktop launcher and HTML5-compatible browser, and provide hardware/driver/rescue diagnostics
EOF

echo "Built ISO: ${OUTPUT_ISO}"
echo "Size: ${ISO_MB} MB"
echo "Checksum: ${OUTPUT_ISO}.sha256"
