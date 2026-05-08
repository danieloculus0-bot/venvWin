#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES=(core standard privacy)

for profile in "${PROFILES[@]}"; do
  echo "========================================"
  echo "Building venvWin Portable profile: ${profile}"
  echo "========================================"
  VENVWIN_PORTABLE_PROFILE="${profile}" VENVWIN_PROFILE="${profile}" "${ROOT_DIR}/venvwin-portable/build-iso.sh"
done

"${ROOT_DIR}/venvwin-portable/compare-profiles.sh"
