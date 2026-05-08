#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

DASH_PID=""
TOKEN_DASH_PID=""
TMP_ROOT=""
cleanup() {
  if [[ -n "${DASH_PID}" ]]; then kill "${DASH_PID}" 2>/dev/null || true; fi
  if [[ -n "${TOKEN_DASH_PID}" ]]; then kill "${TOKEN_DASH_PID}" 2>/dev/null || true; fi
  if [[ -n "${TMP_ROOT}" && -d "${TMP_ROOT}" ]]; then rm -rf "${TMP_ROOT}" || true; fi
}
trap cleanup EXIT

echo "== venvWin Portable pre-ISO readiness gate =="

echo "Checking required command tools"
for tool in bash python3 curl; do
  command -v "${tool}" >/dev/null 2>&1 || { echo "Missing required command: ${tool}" >&2; exit 1; }
done

echo "Checking required files"
required_files=(
  "pyproject.toml"
  "docs/branding.md"
  "src/venvwin/cli.py"
  "src/venvwin/dashboard.py"
  "src/venvwin/first_run.py"
  "src/venvwin/gui_first_run.py"
  "src/venvwin/persistence.py"
  "src/venvwin/health.py"
  "venvwin-portable/audit-public-branding.sh"
  "venvwin-portable/bootstrap-flash-ready-ubuntu.sh"
  "venvwin-portable/build-all-profiles.sh"
  "venvwin-portable/build-attempt-checklist.md"
  "venvwin-portable/build-flash-ready-standard.sh"
  "venvwin-portable/build-iso.sh"
  "venvwin-portable/compare-profiles.sh"
  "venvwin-portable/run-wsl-flash-ready.ps1"
  "venvwin-portable/test-iso-qemu.sh"
  "venvwin-portable/test-persistence-qemu.sh"
  "venvwin-portable/usb-flash-guide.md"
  "venvwin-portable/windows-wsl-build-command.md"
  "venvwin-portable/workflow-contract.json"
  "venvwin-portable/first-boot-product-gate.md"
  "venvwin-portable/flash-ready-checklist.md"
  "venvwin-portable/leave-no-trace.md"
  "venvwin-portable/local-flash-ready-build.md"
  "venvwin-portable/phone-build-status.md"
  "venvwin-portable/product-gate.md"
  "venvwin-portable/run-flash-ready-from-phone.md"
)
for file in "${required_files[@]}"; do
  test -f "${file}" || { echo "Missing required file: ${file}" >&2; exit 1; }
done

echo "Checking shell syntax"
for script in \
  venvwin-portable/audit-public-branding.sh \
  venvwin-portable/bootstrap-flash-ready-ubuntu.sh \
  venvwin-portable/build-iso.sh \
  venvwin-portable/compare-profiles.sh \
  venvwin-portable/build-all-profiles.sh \
  venvwin-portable/test-iso-qemu.sh \
  venvwin-portable/test-persistence-qemu.sh \
  venvwin-portable/build-flash-ready-standard.sh; do
  bash -n "${script}"
done

echo "Checking release contract text"
echo "Checking build attempt checklist contract"
grep -q "venvWin Portable" venvwin-portable/build-attempt-checklist.md
grep -q "run-wsl-flash-ready.ps1" venvwin-portable/build-attempt-checklist.md
grep -q "bootstrap-flash-ready-ubuntu.sh" venvwin-portable/build-attempt-checklist.md
grep -q "PUBLIC BRANDING AUDIT: PASS" venvwin-portable/build-attempt-checklist.md
grep -q "PRE-ISO READINESS: PASS" venvwin-portable/build-attempt-checklist.md
grep -q "status=FLASH_READY" venvwin-portable/build-attempt-checklist.md
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-attempt-checklist.md
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-attempt-checklist.md

echo "Checking PowerShell WSL runner contract"
grep -q "venvWin Portable" venvwin-portable/run-wsl-flash-ready.ps1
grep -q "bootstrap-flash-ready-ubuntu.sh" venvwin-portable/run-wsl-flash-ready.ps1
grep -q "status=FLASH_READY" venvwin-portable/run-wsl-flash-ready.ps1
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/run-wsl-flash-ready.ps1
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/run-wsl-flash-ready.ps1

echo "Checking flash-ready gate contract"
grep -q "unsquashfs -ll" venvwin-portable/build-flash-ready-standard.sh
grep -q "squashfs_static_inspection=pass" venvwin-portable/build-flash-ready-standard.sh
grep -q "squashfs-root/etc/skel/Desktop/venvWin-First-Boot.desktop" venvwin-portable/build-flash-ready-standard.sh
grep -q "boot_toram_absent=pass" venvwin-portable/build-flash-ready-standard.sh
grep -q "live_user_autologin=pass" venvwin-portable/build-flash-ready-standard.sh
grep -q "storage_source_marker=pass" venvwin-portable/build-flash-ready-standard.sh
grep -q "venvwin-portable-alpha-standard.iso" venvwin-portable/build-flash-ready-standard.sh
grep -q "venvwin-flash-ready-verdict.txt" venvwin-portable/build-flash-ready-standard.sh

echo "Checking USB flash guide contract"
grep -q "status=FLASH_READY" venvwin-portable/usb-flash-guide.md
grep -q "sha256sum -c dist/venvwin-portable-alpha-standard.iso.sha256" venvwin-portable/usb-flash-guide.md
grep -q "dist/venvwin-portable-alpha-standard.iso" venvwin-portable/usb-flash-guide.md
grep -q "dist/venvwin-flash-ready-verdict.txt" venvwin-portable/usb-flash-guide.md

echo "Checking public branding contract"
chmod +x venvwin-portable/audit-public-branding.sh
./venvwin-portable/audit-public-branding.sh

echo "Checking Python imports, GUI model, dashboard model, and fallback honesty"
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory

from venvwin.cli import build_parser
from venvwin.dashboard import dashboard_model, dashboard_url, get_or_create_token, render_dashboard, token_link
from venvwin.first_run import (
    DASHBOARD_NAME,
    FIRST_BOOT_CHECKLIST_NAME,
    FIRST_BOOT_PROOF_NAME,
    PUBLIC_PRODUCT_NAME,
    QUICK_START_NAME,
    first_run_summary,
    wizard_text,
    write_first_run_files,
)
from venvwin.gui_first_run import display_model, status_color
from venvwin.persistence import persistence_report

build_parser()

with TemporaryDirectory() as tmp:
    base = Path(tmp)
    home = base / "home"
    root = base / "runtime"
    home.mkdir(parents=True, exist_ok=True)
    summary = first_run_summary(home)
    assert summary["product_name"] == PUBLIC_PRODUCT_NAME
    assert summary["capsule_store"] == str(home / "venvWin-Capsules")
    assert summary["dashboard_url"] == "http://127.0.0.1:8787"
    write_first_run_files(home)
    desktop = home / "Desktop"
    quick_start = desktop / QUICK_START_NAME
    first_boot_proof = desktop / FIRST_BOOT_PROOF_NAME
    dashboard_file = desktop / DASHBOARD_NAME
    checklist_file = desktop / FIRST_BOOT_CHECKLIST_NAME
    for path in (quick_start, first_boot_proof, dashboard_file, checklist_file):
        assert path.exists(), path
    assert (home / ".venvwin-capsule-store").exists()
    assert (home / ".venvwin-capsule-store-source").read_text(encoding="utf-8") == "home-fallback"
    assert (home / ".venvwin-persistence-report.json").exists()
    assert "Dashboard:" in quick_start.read_text(encoding="utf-8")
    proof_text = first_boot_proof.read_text(encoding="utf-8")
    assert f"{PUBLIC_PRODUCT_NAME} First Boot Proof" in proof_text
    assert DASHBOARD_NAME in proof_text
    assert FIRST_BOOT_CHECKLIST_NAME in proof_text
    assert "dashboard_url=http://127.0.0.1:8787" in proof_text
    assert "capsule_store=" in proof_text
    assert f"{PUBLIC_PRODUCT_NAME} Dashboard" in dashboard_file.read_text(encoding="utf-8")
    assert f"{PUBLIC_PRODUCT_NAME} First Boot Checklist" in checklist_file.read_text(encoding="utf-8")
    model = display_model(home)
    assert model["capsule_store"] == str(home / "venvWin-Capsules")
    assert status_color("leave-no-trace-ok") == "#22c55e"
    wizard = wizard_text(home)
    assert f"{PUBLIC_PRODUCT_NAME} First Run" in wizard
    assert "Where should Windows app state live?" in wizard
    assert "Dashboard: http://127.0.0.1:8787" in wizard
    report = persistence_report(home)
    assert report["chosen"]["source"] == "home-fallback"
    assert report["disposable_warning"] is True
    assert report["host_write_warning"] is True
    dash = dashboard_model(root=root, home=home)
    assert dash["product_name"] == PUBLIC_PRODUCT_NAME
    assert "storage" in dash
    assert "health" in dash
    assert "capsules" in dash
    rendered = render_dashboard(dash)
    assert PUBLIC_PRODUCT_NAME in rendered
    assert "Control Panel" in rendered
    assert "Leave no trace" in rendered
    rendered_token = render_dashboard(dash, token="abc")
    assert "/api/status?token=abc" in rendered_token
    assert token_link("/api/status", "abc") == "/api/status?token=abc"
    assert dashboard_url("0.0.0.0", 8787, "abc") == "http://127.0.0.1:8787/?token=abc"
    first_token = get_or_create_token(home)
    second_token = get_or_create_token(home)
    assert first_token == second_token
    assert len(first_token) >= 20
    assert (home / ".venvwin-dashboard-token").exists()

print("Python readiness checks passed")
PY

echo "Running tests"
python3 -m pytest -q

echo "Checking CLI smoke commands"
TMP_ROOT="$(mktemp -d)"
export VENVWIN_HOME="${TMP_ROOT}/venvwin-home"
export VENVWIN_HOME_SOURCE="VENVWIN_HOME"
mkdir -p "${TMP_ROOT}/installers" "${TMP_ROOT}/apps" "${TMP_ROOT}/home" "${VENVWIN_HOME}"
touch "${TMP_ROOT}/installers/setup.exe"

python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" init
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home"
test -f "${TMP_ROOT}/home/.venvwin-capsule-store-source"
grep -q "VENVWIN_HOME" "${TMP_ROOT}/home/.venvwin-capsule-store-source"
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home" --wizard-text >/dev/null
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home" --json >/dev/null
python3 -m venvwin.cli storage >/dev/null
python3 -m venvwin.cli storage --json >/dev/null
PYTHONPATH=src python3 -m venvwin.dashboard --root "${TMP_ROOT}/runtime" --home "${TMP_ROOT}/home" --port 9878 >/tmp/venvwin-dashboard-smoke.log 2>&1 &
DASH_PID=$!
sleep 1
curl -fsS http://127.0.0.1:9878/ >/dev/null
curl -fsS http://127.0.0.1:9878/api/status >/dev/null
curl -fsS http://127.0.0.1:9878/api/doctor >/dev/null
kill "${DASH_PID}" || true
DASH_PID=""

PYTHONPATH=src python3 -m venvwin.dashboard --root "${TMP_ROOT}/runtime" --home "${TMP_ROOT}/home" --port 9879 --token testtoken >/tmp/venvwin-dashboard-token-smoke.log 2>&1 &
TOKEN_DASH_PID=$!
sleep 1
LOCK_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9879/)"
test "${LOCK_CODE}" = "403"
curl -fsS "http://127.0.0.1:9879/?token=testtoken" >/dev/null
curl -fsS "http://127.0.0.1:9879/api/status?token=testtoken" >/dev/null
curl -fsS "http://127.0.0.1:9879/api/doctor?token=testtoken" >/dev/null
kill "${TOKEN_DASH_PID}" || true
TOKEN_DASH_PID=""

python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" doctor >/dev/null || true
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" doctor --json >/dev/null || true
python3 -m venvwin.cli associate --applications-dir "${TMP_ROOT}/apps" >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" create "Notepad Plus Plus" >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" list >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" inspect notepad-plus-plus >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" install-command notepad-plus-plus setup.exe >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" install notepad-plus-plus "${TMP_ROOT}/installers/setup.exe" --dry-run >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" open "${TMP_ROOT}/installers/setup.exe" --dry-run >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" launcher create notepad-plus-plus "Notepad Plus Plus" "C:\\Program Files\\Notepad++\\notepad++.exe" >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" snapshot create notepad-plus-plus --label smoke >/dev/null
python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" reset notepad-plus-plus >/dev/null

echo "PRE-ISO READINESS: PASS"
