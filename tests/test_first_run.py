from pathlib import Path

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


def test_first_run_summary_has_storage_status(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    summary = first_run_summary(tmp_path)

    assert summary["product_name"] == PUBLIC_PRODUCT_NAME
    assert "internal_codename" not in summary
    assert "capsule_store" in summary
    assert "storage_status" in summary
    assert "storage_message" in summary
    assert "dashboard_url" in summary
    assert summary["capsule_store"] == str(tmp_path / "venvWin-Capsules")
    assert summary["dashboard_url"] == "http://127.0.0.1:8787"


def test_write_first_run_files(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    summary = write_first_run_files(tmp_path)
    desktop = tmp_path / "Desktop"

    assert (desktop / QUICK_START_NAME).exists()
    assert (desktop / FIRST_BOOT_PROOF_NAME).exists()
    assert (desktop / DASHBOARD_NAME).exists()
    assert (desktop / FIRST_BOOT_CHECKLIST_NAME).exists()
    assert (tmp_path / ".venvwin-capsule-store").exists()
    assert (tmp_path / ".venvwin-persistence-report.json").exists()
    assert Path(summary["capsule_store"]).exists()

    proof_text = (desktop / FIRST_BOOT_PROOF_NAME).read_text(encoding="utf-8")
    checklist_text = (desktop / FIRST_BOOT_CHECKLIST_NAME).read_text(encoding="utf-8")
    dashboard_text = (desktop / DASHBOARD_NAME).read_text(encoding="utf-8")

    assert f"{PUBLIC_PRODUCT_NAME} First Boot Proof" in proof_text
    assert "internal_codename=" not in proof_text
    assert DASHBOARD_NAME in proof_text
    assert FIRST_BOOT_CHECKLIST_NAME in proof_text
    assert f"{PUBLIC_PRODUCT_NAME} First Boot Checklist" in checklist_text
    assert f"{PUBLIC_PRODUCT_NAME} Dashboard" in dashboard_text
    assert "http://127.0.0.1:8787" in dashboard_text


def test_wizard_text(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    text = wizard_text(tmp_path)

    assert f"{PUBLIC_PRODUCT_NAME} First Run" in text
    assert "Where should Windows app state live?" in text
    assert "leave the host machine alone" in text
    assert "Dashboard: http://127.0.0.1:8787" in text
