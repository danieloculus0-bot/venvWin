#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES=(core standard privacy)

for profile in "${PROFILES[@]}"; do
  echo "========================================"
  echo "Building venvWin Portable profile: ${profile}"
  echo "========================================"
  VENVWIN_PORTABLE_PROFILE="${profile}" WINUX_PROFILE="${profile}" "${ROOT_DIR}/winux-portable/build-iso.sh"
done

"${ROOT_DIR}/winux-portable/compare-profiles.sh"
