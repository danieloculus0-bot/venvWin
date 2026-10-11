#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Legacy multi-image build is explicitly opt-in: it is NOT the Puppy-adjacent
# boot-development default and could generate several gigabytes of ISO files.
if [[ "${VENVWIN_ALLOW_MULTI_ISO_BUILD:-0}" != "1" ]]; then
  echo "Multi-profile monolithic build disabled by default. Explicitly set VENVWIN_ALLOW_MULTI_ISO_BUILD=1 for legacy lab comparisons." >&2
  exit 2
fi
PROFILES=(core standard privacy)

for profile in "${PROFILES[@]}"; do
  echo "========================================"
  echo "Building venvWin Portable profile: ${profile}"
  echo "========================================"
  VENVWIN_PORTABLE_PROFILE="${profile}" VENVWIN_PROFILE="${profile}" "${ROOT_DIR}/venvwin-portable/build-iso.sh"
done

"${ROOT_DIR}/venvwin-portable/compare-profiles.sh"
