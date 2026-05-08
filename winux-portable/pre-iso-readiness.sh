#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== WinUx pre-ISO readiness gate =="

echo "Checking required files"
required_files=(
  "pyproject.toml"
  "src/venvwin/cli.py"
  "src/venvwin/dashboard.py"
  "src/venvwin/first_run.py"
  "src/venvwin/gui_first_run.py"
  "src/venvwin/persistence.py"
  "src/venvwin/health.py"
  "winux-portable/build-iso.sh"
  "winux-portable/test-iso-qemu.sh"
  "winux-portable/first-boot-product-gate.md"
  "winux-portable/leave-no-trace.md"
  "winux-portable/product-gate.md"
)

for file in "${required_files[@]}"; do
  test -f "${file}" || { echo "Missing required file: ${file}" >&2; exit 1; }
done

echo "Checking shell syntax"
bash -n winux-portable/build-iso.sh
bash -n winux-portable/compare-profiles.sh
bash -n winux-portable/build-all-profiles.sh
bash -n winux-portable/test-iso-qemu.sh

echo "Checking Python imports, GUI model, and dashboard model"
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory

from venvwin.cli import build_parser
from venvwin.dashboard import dashboard_model, render_dashboard
from venvwin.first_run import first_run_summary, wizard_text, write_first_run_files
from venvwin.gui_first_run import display_model, status_color
from venvwin.persistence import persistence_report

build_parser()

with TemporaryDirectory() as tmp:
    base = Path(tmp)
    home = base / "home"
    root = base / "runtime"
    summary = first_run_summary(home)
    assert summary["capsule_store"] == str(home / "WinUx-Capsules")
    assert summary["dashboard_url"] == "http://127.0.0.1:8787"
    write_first_run_files(home)
    quick_start = home / "Desktop" / "WinUx-Quick-Start.txt"
    first_boot_proof = home / "Desktop" / "WinUx-First-Boot-Proof.txt"
    assert quick_start.exists()
    assert first_boot_proof.exists()
    assert (home / ".winux-capsule-store").exists()
    assert (home / ".winux-persistence-report.json").exists()
    assert "Dashboard:" in quick_start.read_text(encoding="utf-8")
    proof_text = first_boot_proof.read_text(encoding="utf-8")
    assert "WinUx First Boot Proof" in proof_text
    assert "dashboard_url=http://127.0.0.1:8787" in proof_text
    assert "capsule_store=" in proof_text
    model = display_model(home)
    assert model["capsule_store"] == str(home / "WinUx-Capsules")
    assert status_color("leave-no-trace-ok") == "#22c55e"
    wizard = wizard_text(home)
    assert "Where should Windows app state live?" in wizard
    assert "Dashboard: http://127.0.0.1:8787" in wizard
    report = persistence_report(home)
    assert "chosen" in report
    assert "leave_no_trace" in report
    assert "host_write_warning" in report
    dash = dashboard_model(root=root, home=home)
    assert "storage" in dash
    assert "health" in dash
    assert "capsules" in dash
    rendered = render_dashboard(dash)
    assert "WinUx Dashboard" in rendered
    assert "Leave no trace" in rendered

print("Python readiness checks passed")
PY

echo "Running tests"
python3 -m pytest -q

echo "Checking CLI smoke commands"
TMP_ROOT="$(mktemp -d)"
export VENVWIN_HOME="${TMP_ROOT}/venvwin-home"
mkdir -p "${TMP_ROOT}/installers" "${TMP_ROOT}/apps" "${TMP_ROOT}/home"
touch "${TMP_ROOT}/installers/setup.exe"

python3 -m venvwin.cli --root "${TMP_ROOT}/runtime" init
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home"
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home" --wizard-text >/dev/null
python3 -m venvwin.cli first-run --home "${TMP_ROOT}/home" --json >/dev/null
python3 -m venvwin.cli storage >/dev/null
python3 -m venvwin.cli storage --json >/dev/null
PYTHONPATH=src python3 -m venvwin.dashboard --root "${TMP_ROOT}/runtime" --home "${TMP_ROOT}/home" --port 9878 >/tmp/winux-dashboard-smoke.log 2>&1 &
DASH_PID=$!
sleep 1
curl -fsS http://127.0.0.1:9878/ >/dev/null
curl -fsS http://127.0.0.1:9878/api/status >/dev/null
curl -fsS http://127.0.0.1:9878/api/doctor >/dev/null
kill "${DASH_PID}" || true
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
