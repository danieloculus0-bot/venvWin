#!/usr/bin/env bash
# Reproducible Debian Bookworm live-build builder, independent of the host's
# old Ubuntu live-build (which does not support --bootloaders).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v docker >/dev/null || { echo "Docker is required for the Bookworm build" >&2; exit 1; }
# Two explicit, audited entrypoints; never infer a build from a branch name.
VENVWIN_BOOKWORM_BUILD_TARGET="${VENVWIN_BOOKWORM_BUILD_TARGET:-standard}"
case "${VENVWIN_BOOKWORM_BUILD_TARGET}" in
  standard|core) ;;
  *) echo "Unknown Bookworm build target: ${VENVWIN_BOOKWORM_BUILD_TARGET}" >&2; exit 2 ;;
esac
# Keep the evidence directory writable by the non-root GitHub Actions runner.
mkdir -p dist
docker run --rm --privileged \
  -e VENVWIN_BOOKWORM_BUILD_TARGET \
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
    git config --global --add safe.directory /workspace
    python3 -m venv /tmp/venvwin-build-venv
    /tmp/venvwin-build-venv/bin/python -m pip install -e . pytest
    export PATH="/tmp/venvwin-build-venv/bin:$PATH"
    case "$VENVWIN_BOOKWORM_BUILD_TARGET" in
      standard) bash ./venvwin-portable/build-flash-ready-standard.sh ;;
      core) bash ./venvwin-portable/build-core-proof.sh ;;
    esac
  '
