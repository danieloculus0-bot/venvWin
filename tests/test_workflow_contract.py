from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def test_flash_ready_workflow_matches_contract():
    contract = json.loads((ROOT / "winux-portable" / "workflow-contract.json").read_text(encoding="utf-8"))
    workflow = (ROOT / ".github" / "workflows" / "flash-ready-standard.yml").read_text(encoding="utf-8")

    assert f"name: {contract['workflow']}" in workflow
    assert "workflow_dispatch:" in workflow
    assert "./winux-portable/build-flash-ready-standard.sh" in workflow
    assert f"name: {contract['required_artifact']}" in workflow

    for required_file in contract["required_files"]:
        assert f"dist/{required_file}" in workflow


def test_flash_ready_script_writes_required_verdict():
    contract = json.loads((ROOT / "winux-portable" / "workflow-contract.json").read_text(encoding="utf-8"))
    script = (ROOT / "winux-portable" / "build-flash-ready-standard.sh").read_text(encoding="utf-8")

    assert contract["required_verdict"] in script
    assert "pre_iso_readiness=pass" in script
    assert "static_iso_inspection=pass" in script
    assert "qemu_smoke=pass" in script
    assert "manifest_flags=pass" in script
