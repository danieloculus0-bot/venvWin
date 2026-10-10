#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== venvWin Portable Ubuntu/WSL flash-ready bootstrap =="
echo "Using a Debian Bookworm container for the reproducible ISO build."
echo "The host's Ubuntu live-build is incompatible with the Debian GRUB options."
echo "Container dependencies include squashfs-tools, QEMU, GRUB, pytest and live-build."
# The container calls ./venvwin-portable/build-flash-ready-standard.sh.
# A genuine guest proof and BEAN evidence are required by the CI release gate.
command -v docker >/dev/null 2>&1 || {
  echo "Docker is required. Enable Docker Desktop's WSL integration or install Docker Engine." >&2
  exit 1
}
docker info >/dev/null
bash ./venvwin-portable/build-in-bookworm.sh

echo "== Final verdict =="
cat dist/venvwin-flash-ready-verdict.txt
echo "Output bundle:"
echo "  dist/venvwin-portable-alpha-standard.iso"
echo "  dist/venvwin-portable-alpha-standard.iso.sha256"
echo "  dist/venvwin-portable-alpha-standard-manifest.txt"
echo "  dist/venvwin-flash-ready-verdict.txt"
