#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/winux-portable-iso"
OUT_DIR="${ROOT_DIR}/dist"
IMAGE_NAME="winux-portable-alpha"

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is missing. Install it with: sudo apt-get install -y live-build" >&2
  exit 1
fi

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

cat > config/package-lists/winux.list.chroot <<'EOF'
live-boot
live-config
systemd-sysv
sudo
network-manager
xorg
lightdm
xfce4
xfce4-terminal
thunar
mousepad
python3
python3-venv
python3-pip
python3-tk
xdg-utils
desktop-file-utils
shared-mime-info
wine
wine64
cabextract
p7zip-full
curl
ca-certificates
git
rsync
EOF

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

cat > config/includes.chroot/usr/local/bin/winux-first-run <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

export VENVWIN_HOME="${VENVWIN_HOME:-$HOME/WinUx-Capsules}"
mkdir -p "$HOME/Desktop" "$VENVWIN_HOME"

venvwin init || true
venvwin associate || true
venvwin doctor > "$HOME/Desktop/venvwin-doctor.txt" || true

cat > "$HOME/Desktop/WinUx-Quick-Start.txt" <<'MSG'
Welcome to WinUx Portable.

Double-click a Windows EXE/MSI, or run:

  venvwin open /path/to/app.exe

Capsules live here:

  ~/WinUx-Capsules

Run health check:

  venvwin doctor

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
Exec=thunar /home/user/WinUx-Capsules
Terminal=false
Categories=Utility;
EOF

cat > config/hooks/normal/010-winux-setup.chroot <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Setting up WinUx Portable runtime hooks"

cat > /etc/profile.d/venvwin.sh <<'PROFILE'
export VENVWIN_HOME="${VENVWIN_HOME:-$HOME/WinUx-Capsules}"
export PYTHONPATH="/opt/venvwin/src:${PYTHONPATH:-}"
PROFILE

update-desktop-database /usr/share/applications || true
update-mime-database /usr/share/mime || true
EOF
chmod +x config/hooks/normal/010-winux-setup.chroot

sudo lb build

ISO_PATH="$(find . -maxdepth 1 \( -name 'live-image-*.iso' -o -name 'live-image-*.hybrid.iso' \) -type f | head -n 1 || true)"
if [[ -z "${ISO_PATH}" ]]; then
  echo "ISO build finished but no ISO was found. That is cursed and not product-ready." >&2
  exit 1
fi

cp "${ISO_PATH}" "${OUT_DIR}/${IMAGE_NAME}.iso"
sha256sum "${OUT_DIR}/${IMAGE_NAME}.iso" > "${OUT_DIR}/${IMAGE_NAME}.iso.sha256"

echo "Built ISO: ${OUT_DIR}/${IMAGE_NAME}.iso"
echo "Checksum: ${OUT_DIR}/${IMAGE_NAME}.iso.sha256"
