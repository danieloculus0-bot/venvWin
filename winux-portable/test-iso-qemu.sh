#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
WINUX_PROFILE="${WINUX_PROFILE:-standard}"
ISO_PATH="${ISO_PATH:-${DIST_DIR}/venvwin-portable-alpha-${WINUX_PROFILE}.iso}"
MEMORY="${MEMORY:-4096}"
CPUS="${CPUS:-2}"
BOOT_MODE="${BOOT_MODE:-gui}"

if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ISO not found: ${ISO_PATH}" >&2
  echo "Build it first with:" >&2
  echo "  WINUX_PROFILE=${WINUX_PROFILE} ./winux-portable/build-iso.sh" >&2
  exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 is missing. Install it with:" >&2
  echo "  sudo apt-get install -y qemu-system-x86" >&2
  exit 1
fi

if [[ -f "${ISO_PATH}.sha256" ]]; then
  echo "Checking checksum"
  sha256sum -c "${ISO_PATH}.sha256"
fi

echo "== venvWin Portable QEMU boot test =="
echo "profile=${WINUX_PROFILE}"
echo "iso=${ISO_PATH}"
echo "memory_mb=${MEMORY}"
echo "cpus=${CPUS}"
echo "boot_mode=${BOOT_MODE}"
echo

COMMON_ARGS=(
  -m "${MEMORY}"
  -smp "${CPUS}"
  -cdrom "${ISO_PATH}"
  -boot d
  -device virtio-net-pci,netdev=n0
  -netdev user,id=n0
)

case "${BOOT_MODE}" in
  gui)
    echo "Launching GUI boot test. Close the QEMU window when done."
    exec qemu-system-x86_64 "${COMMON_ARGS[@]}"
    ;;
  headless)
    echo "Launching headless boot smoke test. This verifies the ISO starts, not that the desktop is usable."
    exec qemu-system-x86_64 \
      "${COMMON_ARGS[@]}" \
      -display none \
      -serial mon:stdio \
      -no-reboot
    ;;
  kvm)
    echo "Launching GUI boot test with KVM acceleration. Close the QEMU window when done."
    exec qemu-system-x86_64 \
      -enable-kvm \
      -cpu host \
      "${COMMON_ARGS[@]}"
    ;;
  *)
    echo "Unknown BOOT_MODE='${BOOT_MODE}'. Use gui, headless, or kvm." >&2
    exit 1
    ;;
esac
