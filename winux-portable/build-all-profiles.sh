#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES=(core standard privacy)

for profile in "${PROFILES[@]}"; do
  echo "========================================"
  echo "Building WinUx Portable profile: ${profile}"
  echo "========================================"
  WINUX_PROFILE="${profile}" "${ROOT_DIR}/winux-portable/build-iso.sh"
done

"${ROOT_DIR}/winux-portable/compare-profiles.sh"
