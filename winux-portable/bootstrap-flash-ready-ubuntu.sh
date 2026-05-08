#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== venvWin Portable Ubuntu/WSL flash-ready bootstrap =="
echo "This installs build tools, runs preflight, builds the Standard ISO, and writes the flash-ready verdict."
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "Missing sudo. Run on Ubuntu/Debian/WSL with sudo access." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Missing apt-get. This bootstrap is for Ubuntu/Debian/WSL hosts." >&2
  exit 1
fi

echo "Step 1: Install system packages"
sudo apt-get update
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-full \
  live-build \
  rsync \
  xorriso \
  isolinux \
  syslinux-common \
  squashfs-tools \
  qemu-system-x86 \
  ovmf \
  curl \
  ca-certificates

echo "Step 2: Install Python package and tests"
python3 -m pip install --break-system-packages --upgrade pip || python3 -m pip install --upgrade pip
python3 -m pip install --break-system-packages -e . pytest || python3 -m pip install -e . pytest

echo "Step 3: Make build scripts executable"
chmod +x \
  winux-portable/audit-public-branding.sh \
  winux-portable/pre-iso-readiness.sh \
  winux-portable/build-iso.sh \
  winux-portable/build-flash-ready-standard.sh \
  winux-portable/test-iso-qemu.sh \
  winux-portable/test-persistence-qemu.sh

echo "Step 4: Run flash-ready standard gate"
./winux-portable/build-flash-ready-standard.sh

echo
echo "Step 5: Final verdict"
cat dist/venvwin-flash-ready-verdict.txt

echo
echo "Output bundle:"
echo "  dist/venvwin-portable-alpha-standard.iso"
echo "  dist/venvwin-portable-alpha-standard.iso.sha256"
echo "  dist/venvwin-portable-alpha-standard-manifest.txt"
echo "  dist/venvwin-flash-ready-verdict.txt"
