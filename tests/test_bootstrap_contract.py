from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_script_points_at_flash_ready_gate_and_artifacts():
    script = (ROOT / "winux-portable" / "bootstrap-flash-ready-ubuntu.sh").read_text(encoding="utf-8")

    assert "./winux-portable/build-flash-ready-standard.sh" in script
    assert "dist/venvwin-portable-alpha-standard.iso" in script
    assert "dist/venvwin-portable-alpha-standard.iso.sha256" in script
    assert "dist/venvwin-portable-alpha-standard-manifest.txt" in script
    assert "dist/venvwin-flash-ready-verdict.txt" in script
    assert "cat dist/venvwin-flash-ready-verdict.txt" in script


def test_local_build_doc_mentions_fast_path_and_artifacts():
    doc = (ROOT / "winux-portable" / "local-flash-ready-build.md").read_text(encoding="utf-8")

    assert "bootstrap-flash-ready-ubuntu.sh" in doc
    assert "./winux-portable/build-flash-ready-standard.sh" in doc
    assert "FLASH READY: dist/venvwin-portable-alpha-standard.iso" in doc
    assert "status=FLASH_READY" in doc
