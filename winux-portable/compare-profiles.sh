#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
REPORT="${DIST_DIR}/winux-profile-comparison.txt"
PROFILES=(core standard privacy)

mkdir -p "${DIST_DIR}"

cat > "${REPORT}" <<'HEAD'
WinUx Portable Profile Comparison

This report compares locally available ISO artifacts.

HEAD

for profile in "${PROFILES[@]}"; do
  iso="${DIST_DIR}/winux-portable-alpha-${profile}.iso"
  manifest="${DIST_DIR}/winux-portable-alpha-${profile}-manifest.txt"
  checksum="${iso}.sha256"

  echo "== ${profile} ==" >> "${REPORT}"

  if [[ ! -f "${iso}" ]]; then
    echo "status=missing" >> "${REPORT}"
    echo "note=No ISO found. Build with: WINUX_PROFILE=${profile} ./winux-portable/build-iso.sh" >> "${REPORT}"
    echo >> "${REPORT}"
    continue
  fi

  bytes="$(stat -c%s "${iso}")"
  mb="$(( (bytes + 1048575) / 1048576 ))"
  echo "status=present" >> "${REPORT}"
  echo "size_mb=${mb}" >> "${REPORT}"

  if [[ -f "${checksum}" ]]; then
    if sha256sum -c "${checksum}" >/dev/null 2>&1; then
      echo "checksum=ok" >> "${REPORT}"
    else
      echo "checksum=fail" >> "${REPORT}"
    fi
  else
    echo "checksum=missing" >> "${REPORT}"
  fi

  if [[ -f "${manifest}" ]]; then
    echo "manifest=present" >> "${REPORT}"
  else
    echo "manifest=missing" >> "${REPORT}"
  fi

  if [[ "${mb}" -gt 3500 ]]; then
    echo "size_flag=hard-concern-bloated-goblin" >> "${REPORT}"
  elif [[ "${mb}" -gt 2500 ]]; then
    echo "size_flag=soft-warning-alpha-fat" >> "${REPORT}"
  elif [[ "${mb}" -le 1200 ]]; then
    echo "size_flag=sellable-target" >> "${REPORT}"
  else
    echo "size_flag=acceptable-alpha-beta" >> "${REPORT}"
  fi

  echo >> "${REPORT}"
done

cat "${REPORT}"
