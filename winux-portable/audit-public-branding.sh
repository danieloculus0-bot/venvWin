#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== venvWin Portable public branding audit =="

required_public=(
  "README.md"
  "docs/branding.md"
  "winux-portable/product-gate.md"
  "winux-portable/first-boot-product-gate.md"
  "winux-portable/flash-ready-checklist.md"
  "winux-portable/phone-build-status.md"
  "winux-portable/run-flash-ready-from-phone.md"
  "winux-portable/local-flash-ready-build.md"
  "winux-portable/workflow-contract.json"
  "winux-portable/build-iso.sh"
  "winux-portable/build-flash-ready-standard.sh"
  "winux-portable/bootstrap-flash-ready-ubuntu.sh"
)

for file in "${required_public[@]}"; do
  test -f "${file}" || { echo "Missing branding-audit file: ${file}" >&2; exit 1; }
  grep -q "venvWin Portable" "${file}" || { echo "Missing public name in: ${file}" >&2; exit 1; }
done

grep -q "WinUx = internal codename only" docs/branding.md || { echo "Branding doc must keep WinUx internal-only rule" >&2; exit 1; }
grep -q '"public_product_name": "venvWin Portable"' winux-portable/workflow-contract.json || { echo "Workflow contract missing public product name" >&2; exit 1; }
grep -q '"internal_codename": "WinUx"' winux-portable/workflow-contract.json || { echo "Workflow contract missing internal codename" >&2; exit 1; }

grep -q "venvwin-portable-alpha-standard.iso" winux-portable/build-flash-ready-standard.sh || { echo "Flash gate missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" winux-portable/build-flash-ready-standard.sh || { echo "Flash gate missing renamed verdict" >&2; exit 1; }
grep -q "venvwin-portable-alpha-standard.iso" winux-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing renamed ISO" >&2; exit 1; }
grep -q "venvwin-flash-ready-verdict.txt" winux-portable/bootstrap-flash-ready-ubuntu.sh || { echo "Bootstrap missing renamed verdict" >&2; exit 1; }
grep -q "venvwin-portable-flash-ready-standard" .github/workflows/flash-ready-standard.yml || { echo "Workflow missing renamed artifact" >&2; exit 1; }

bad_artifact_refs="$(grep -RIn --exclude-dir=.git --exclude='audit-public-branding.sh' \
  -e 'winux-portable-alpha' \
  -e 'winux-flash-ready' \
  -e 'winux-portable-flash-ready-standard' \
  . || true)"

if [[ -n "${bad_artifact_refs}" ]]; then
  echo "Found stale old artifact references:" >&2
  echo "${bad_artifact_refs}" >&2
  exit 1
fi

bad_public_refs="$(grep -RIn --exclude-dir=.git --exclude='audit-public-branding.sh' \
  -e 'WinUx Portable' \
  . || true)"

if [[ -n "${bad_public_refs}" ]]; then
  echo "Found stale public WinUx Portable references:" >&2
  echo "${bad_public_refs}" >&2
  exit 1
fi

echo "PUBLIC BRANDING AUDIT: PASS"
