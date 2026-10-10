#!/usr/bin/env bash
# Reproducible Debian Bookworm live-build builder, independent of the host's
# old Ubuntu live-build (which does not support --bootloaders).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v docker >/dev/null || { echo "Docker is required for the Bookworm build" >&2; exit 1; }
docker run --rm --privileged \
  -v "$ROOT:/workspace" \
  -w /workspace \
  debian:bookworm \
  bash -lc '
    set -euo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip python3-full \
      live-build sudo git rsync xorriso \
      grub-pc-bin grub-efi-amd64-bin grub-common \
      mtools dosfstools squashfs-tools qemu-system-x86 \
      curl ca-certificates wget gzip file
    python3 -m venv /tmp/venvwin-build-venv
    /tmp/venvwin-build-venv/bin/python -m pip install -e . pytest
    export PATH="/tmp/venvwin-build-venv/bin:$PATH"
    bash ./venvwin-portable/build-flash-ready-standard.sh
  '
