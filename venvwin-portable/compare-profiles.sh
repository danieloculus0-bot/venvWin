#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
REPORT="${DIST_DIR}/venvwin-profile-comparison.txt"
PROFILES=(core standard privacy)

mkdir -p "${DIST_DIR}"

cat > "${REPORT}" <<'HEAD'
venvWin Portable Profile Comparison

This report compares locally available ISO artifacts.

HEAD

for profile in "${PROFILES[@]}"; do
  iso="${DIST_DIR}/venvwin-portable-alpha-${profile}.iso"
  manifest="${DIST_DIR}/venvwin-portable-alpha-${profile}-manifest.txt"
  checksum="${iso}.sha256"

  echo "== ${profile} ==" >> "${REPORT}"

  if [[ ! -f "${iso}" ]]; then
    echo "status=missing" >> "${REPORT}"
    echo "note=No ISO found. Build with: VENVWIN_PROFILE=${profile} ./venvwin-portable/build-iso.sh" >> "${REPORT}"
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

  # Size does not prove bootability; report actual bytes and the source budget.
  if [[ "${profile}" == core ]]; then
    if [[ "${mb}" -gt 900 ]]; then
      echo "size_flag=core_over_hard_budget" >> "${REPORT}"
    elif [[ "${mb}" -gt 512 ]]; then
      echo "size_flag=core_above_soft_target" >> "${REPORT}"
    else
      echo "size_flag=core_within_size_goal_boot_unverified" >> "${REPORT}"
    fi
  else
    echo "size_flag=historical_full_profile_manual_only" >> "${REPORT}"
  fi
  echo "boot_verified=unverified_by_size_report" >> "${REPORT}"

  echo >> "${REPORT}"
done

cat "${REPORT}"
