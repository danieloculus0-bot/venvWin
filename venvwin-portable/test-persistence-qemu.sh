#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
VENVWIN_PROFILE="${VENVWIN_PROFILE:-standard}"
ISO_PATH="${ISO_PATH:-${DIST_DIR}/venvwin-portable-alpha-${VENVWIN_PROFILE}.iso}"
PERSIST_IMG="${PERSIST_IMG:-${DIST_DIR}/venvwin-persistence-test.img}"
MEMORY="${MEMORY:-4096}"
CPUS="${CPUS:-2}"
IMAGE_MB="${IMAGE_MB:-2048}"

if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ISO not found: ${ISO_PATH}" >&2
  echo "Build it first with:" >&2
  echo "  ./venvwin-portable/build-flash-ready-standard.sh" >&2
  exit 1
fi

for tool in qemu-system-x86_64 mkfs.ext4 truncate; do
  command -v "${tool}" >/dev/null 2>&1 || { echo "Missing required command: ${tool}" >&2; exit 1; }
done

mkdir -p "${DIST_DIR}"

if [[ ! -f "${PERSIST_IMG}" ]]; then
  echo "Creating persistence image: ${PERSIST_IMG}"
  truncate -s "${IMAGE_MB}M" "${PERSIST_IMG}"
  mkfs.ext4 -F -L persistence "${PERSIST_IMG}"
  TMP_MNT="$(mktemp -d)"
  cleanup_mount() {
    sudo umount "${TMP_MNT}" 2>/dev/null || true
    rmdir "${TMP_MNT}" 2>/dev/null || true
  }
  trap cleanup_mount EXIT
  sudo mount -o loop "${PERSIST_IMG}" "${TMP_MNT}"
  echo "/ union" | sudo tee "${TMP_MNT}/persistence.conf" >/dev/null
  sudo sync
  sudo umount "${TMP_MNT}"
  rmdir "${TMP_MNT}"
  trap - EXIT
else
  echo "Using existing persistence image: ${PERSIST_IMG}"
fi

cat <<'NOTE'
== venvWin Portable Persistence QEMU Test ==

Manual pass criteria:

1. Boot reaches desktop.
2. First boot writes proof files on Desktop.
3. Create a test file or capsule marker in the capsule store.
4. Shut down cleanly.
5. Boot again with the same persistence image.
6. Marker still exists.

If state does not survive reboot, this is NOT PRODUCT READY.
NOTE

exec qemu-system-x86_64 \
  -m "${MEMORY}" \
  -smp "${CPUS}" \
  -cdrom "${ISO_PATH}" \
  -drive file="${PERSIST_IMG}",format=raw,if=virtio \
  -boot d \
  -device virtio-net-pci,netdev=n0 \
  -netdev user,id=n0 \
  -serial mon:stdio
