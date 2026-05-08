#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== venvWin Portable public branding audit =="

required_public=(
  "README.md"
  "docs/branding.md"
  "venvwin-portable/product-gate.md"
  "venvwin-portable/first-boot-product-gate.md"
  "venvwin-portable/flash-ready-checklist.md"
  "venvwin-portable/phone-build-status.md"
  "venvwin-portable/run-flash-ready-from-phone.md"
  "venvwin-portable/run-wsl-flash-ready.ps1"
  "venvwin-portable/build-attempt-checklist.md"
  "venvwin-portable/local-flash-ready-build.md"
  "venvwin-portable/windows-wsl-build-command.md"
  "venvwin-portable/usb-flash-guide.md"
  "venvwin-portable/workflow-contract.json"
  "venvwin-portable/build-iso.sh"
  "venvwin-portable/build-flash-ready-standard.sh"
  "venvwin-portable/bootstrap-flash-ready-ubuntu.sh"
)

for file in "${required_public[@]}"; do
  test -f "${file}" || { echo "Missing branding-audit file: ${file}" >&2; exit 1; }
  grep -q "venvWin Portable" "${file}" || { echo "Missing public name in: ${file}" >&2; exit 1; }
done

old_mixed="Wi""nUx"
old_upper="WI""NUX"
old_title="Wi""nux"
old_lower="wi""nux"

echo "Checking retired-name absence in tracked paths"
if git ls-files | grep -E "${old_mixed}|${old_upper}|${old_title}|${old_lower}"; then
  echo "Retired naming remains in tracked paths" >&2
  exit 1
fi

echo "Checking retired-name absence in tracked text"
if git grep -n -e "${old_mixed}" -e "${old_upper}" -e "${old_title}" -e "${old_lower}" -- .; then
  echo "Retired naming remains in tracked text" >&2
  exit 1
fi

grep -q '"public_product_name": "venvWin Portable"' venvwin-portable/workflow-contract.json || { echo "Workflow contract missing public product name" >&2; exit 1; }

grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-flash-ready-standard.sh || { echo "Flash gate missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-flash-ready-standard.sh || { echo "Flash gate missing verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/windows-wsl-build-command.md || { echo "WSL guide missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/windows-wsl-build-command.md || { echo "WSL guide missing verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing standard ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-flash-ready-standard" .github/workflows/flash-ready-standard.yml || { echo "Workflow missing flash-ready artifact" >&2; exit 1; }

echo "PUBLIC BRANDING AUDIT: PASS"
