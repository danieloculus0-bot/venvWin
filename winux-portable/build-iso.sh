#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/winux-portable-iso"
OUT_DIR="${ROOT_DIR}/dist"
IMAGE_NAME="winux-portable-alpha"
WINUX_PROFILE="${WINUX_PROFILE:-standard}"

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
  --bootappend-live "boot=live components quiet splash persistence toram" \
  --iso-application "WinUx Portable" \
  --iso-publisher "WinUx / venvWin" \
  --iso-volume "WINUX_PORTABLE"

mkdir -p \
  config/package-lists \
  config/includes.chroot/opt/venvwin \
  config/includes.chroot/usr/local/bin \
  config/includes.chroot/usr/share/applications \
  config/includes.chroot/etc/xdg/autostart \
  config/hooks/normal

cat > config/package-lists/00-winux-core.list.chroot <<'EOF'
live-boot
live-config
systemd-sysv
sudo
network-manager
xorg
lightdm
xfce4-session
xfce4-panel
xfce4-settings
xfwm4
xfdesktop4
xfce4-terminal
thunar
mousepad
python3
xdg-utils
desktop-file-utils
shared-mime-info
curl
ca-certificates
rsync
EOF

if [[ "${WINUX_PROFILE}" == "standard" || "${WINUX_PROFILE}" == "privacy" ]]; then
cat > config/package-lists/10-winux-runner.list.chroot <<'EOF'
wine
wine64
cabextract
p7zip-full
EOF
fi

if [[ "${WINUX_PROFILE}" == "standard" || "${WINUX_PROFILE}" == "privacy" ]]; then
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

cat > config/includes.chroot/usr/local/bin/winux-select-capsule-store <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
python3 - <<'PY'
from pathlib import Path
from venvwin.persistence import persistence_report
report = persistence_report()
chosen = report["chosen"]
Path.home().joinpath(".winux-capsule-store").write_text(chosen["path"], encoding="utf-8")
Path.home().joinpath(".winux-persistence-report.json").write_text(__import__("json").dumps(report, indent=2), encoding="utf-8")
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
Useful for testing, not spy-movie bullshit.
WARN
  exec torsocks firefox-esr --new-instance --profile "$HOME/.winux-firefox-tor-fallback"
fi

cat <<'ERR'
Privacy browser is not ready.
Tor Browser / torbrowser-launcher is missing, and fallback Firefox-over-Tor is unavailable.
Installing a normal browser and calling it anonymous would be bullshit.
ERR
exit 1
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-private-browser

cat > config/includes.chroot/usr/local/bin/winux-first-run <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CAPSULE_STORE="$(/usr/local/bin/winux-select-capsule-store)"
export VENVWIN_HOME="${VENVWIN_HOME:-$CAPSULE_STORE}"
mkdir -p "$HOME/Desktop" "$VENVWIN_HOME"

venvwin init || true
venvwin associate || true
venvwin doctor > "$HOME/Desktop/venvwin-doctor.txt" || true

LEAVE_NO_TRACE_NOTE="Leave-no-trace mode: writing to WinUx-owned portable storage. Host machine stays clean."
DISPOSABLE_NOTE="Persistent capsule store selected: $VENVWIN_HOME"
if [ "$VENVWIN_HOME" = "$HOME/WinUx-Capsules" ]; then
  LEAVE_NO_TRACE_NOTE="Leave-no-trace warning: no WinUx-owned persistent storage was found. Do not write to host disks unless you explicitly choose to."
  DISPOSABLE_NOTE="Disposable-session warning: capsule storage is in the live user's home folder. Fine for testing, terrible for keeping your work unless persistence is enabled."
fi

cat > "$HOME/Desktop/WinUx-Quick-Start.txt" <<MSG
Welcome to WinUx Portable.

Default rule:

  Write only to the WinUx USB/install drive. Leave the host machine alone.

$LEAVE_NO_TRACE_NOTE

Double-click a Windows EXE/MSI, or run:

  venvwin open /path/to/app.exe

Capsules live here:

  $VENVWIN_HOME

$DISPOSABLE_NOTE

Run health check:

  venvwin doctor

Private browser:

  winux-private-browser

If Windows files are being bullshit, run:

  venvwin associate
MSG
EOF
chmod +x config/includes.chroot/usr/local/bin/winux-first-run

cat > config/includes.chroot/etc/xdg/autostart/winux-first-run.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=WinUx First Run
Comment=Initialize venvWin capsule storage and double-click handlers
Exec=/usr/local/bin/winux-first-run
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/usr/share/applications/winux-private-browser.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=WinUx Private Browser
Comment=Launch Tor Browser or honest Tor fallback without fake privacy bullshit
Exec=/usr/local/bin/winux-private-browser
Terminal=false
Categories=Network;WebBrowser;
EOF

cat > config/includes.chroot/usr/share/applications/venvwin-doctor.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=venvWin Doctor
Comment=Check venvWin health before the goblins multiply
Exec=xfce4-terminal -e "venvwin doctor"
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

cat > config/hooks/normal/010-winux-setup.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Setting up WinUx Portable runtime hooks"

cat > /etc/profile.d/venvwin.sh <<'PROFILE'
if [ -f "$HOME/.winux-capsule-store" ]; then
  export VENVWIN_HOME="$(cat "$HOME/.winux-capsule-store")"
else
  export VENVWIN_HOME="${VENVWIN_HOME:-$HOME/WinUx-Capsules}"
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

echo "Trimming WinUx Portable image fat"
apt-get clean || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* || true
rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/info/* || true
find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} + || true
EOF
chmod +x config/hooks/normal/090-winux-trim.chroot

sudo lb build

ISO_PATH="$(find . -maxdepth 1 \( -name 'live-image-*.iso' -o -name 'live-image-*.hybrid.iso' \) -type f | head -n 1 || true)"
if [[ -z "${ISO_PATH}" ]]; then
  echo "ISO build finished but no ISO was found. That is cursed and not product-ready." >&2
  exit 1
fi

OUTPUT_ISO="${OUT_DIR}/${IMAGE_NAME}-${WINUX_PROFILE}.iso"
cp "${ISO_PATH}" "${OUTPUT_ISO}"
sha256sum "${OUTPUT_ISO}" > "${OUTPUT_ISO}.sha256"

ISO_BYTES="$(stat -c%s "${OUTPUT_ISO}")"
ISO_MB="$(( (ISO_BYTES + 1048575) / 1048576 ))"
cat > "${OUT_DIR}/${IMAGE_NAME}-${WINUX_PROFILE}-manifest.txt" <<EOF
WinUx Portable ISO Manifest
profile=${WINUX_PROFILE}
iso=${OUTPUT_ISO}
size_mb=${ISO_MB}
sha256_file=${OUTPUT_ISO}.sha256
leave_no_trace_default=true
default_storage=WinUx USB/install drive only
EOF

echo "Built ISO: ${OUTPUT_ISO}"
echo "Size: ${ISO_MB} MB"
echo "Checksum: ${OUTPUT_ISO}.sha256"
if [[ "${ISO_MB}" -gt 3500 ]]; then
  echo "Hard concern: ISO is over 3500 MB. This is bloated-goblin territory."
elif [[ "${ISO_MB}" -gt 2500 ]]; then
  echo "Soft warning: ISO is over 2500 MB. Alpha can live, but trim this bastard later."
fi
