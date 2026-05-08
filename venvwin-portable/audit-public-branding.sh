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

grep -q "venvWin = internal codename only" docs/branding.md || { echo "Branding doc must keep venvWin internal-only rule" >&2; exit 1; }
grep -q '"public_product_name": "venvWin Portable"' venvwin-portable/workflow-contract.json || { echo "Workflow contract missing public product name" >&2; exit 1; }
grep -q '"internal_codename": "venvWin"' venvwin-portable/workflow-contract.json || { echo "Workflow contract missing internal codename" >&2; exit 1; }

grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-flash-ready-standard.sh || { echo "Flash gate missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-flash-ready-standard.sh || { echo "Flash gate missing renamed verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing renamed verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/windows-wsl-build-command.md || { echo "WSL guide missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/windows-wsl-build-command.md || { echo "WSL guide missing renamed verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing renamed verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/run-wsl-flash-ready.ps1 || { echo "PowerShell WSL runner missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing renamed verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/build-attempt-checklist.md || { echo "Build attempt checklist missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing renamed verdict" >&2; exit 1; }
grep -q "status=FLASH_READY" venvwin-portable/usb-flash-guide.md || { echo "USB flash guide missing flash-ready status gate" >&2; exit 1; }
grep -q "venvwin-portable-flash-ready-standard" .github/workflows/flash-ready-standard.yml || { echo "Workflow missing renamed artifact" >&2; exit 1; }

bad_artifact_refs="$(grep -RIn --exclude-dir=.git \
  --exclude='audit-public-branding.sh' \
  --exclude='test_readme_product_contract.py' \
  -e 'venvwin-portable-alpha' \
  -e 'venvwin-flash-ready' \
  -e 'venvwin-portable-flash-ready-standard' \
  . || true)"

if [[ -n "${bad_artifact_refs}" ]]; then
  echo "Found stale old artifact references:" >&2
  echo "${bad_artifact_refs}" >&2
  exit 1
fi

bad_public_refs="$(grep -RIn --exclude-dir=.git \
  --exclude='audit-public-branding.sh' \
  --exclude='test_readme_product_contract.py' \
  -e 'venvWin Portable' \
  . || true)"

if [[ -n "${bad_public_refs}" ]]; then
  echo "Found stale public venvWin Portable references:" >&2
  echo "${bad_public_refs}" >&2
  exit 1
fi

echo "PUBLIC BRANDING AUDIT: PASS"
