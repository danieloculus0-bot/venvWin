from pathlib import Path

from venvwin.first_run import QUICK_START_NAME, first_run_summary, wizard_text, write_first_run_files


def test_first_run_summary_has_storage_status(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    summary = first_run_summary(tmp_path)

    assert "capsule_store" in summary
    assert "storage_status" in summary
    assert "storage_message" in summary
    assert summary["capsule_store"] == str(tmp_path / "WinUx-Capsules")


def test_write_first_run_files(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    summary = write_first_run_files(tmp_path)

    assert (tmp_path / "Desktop" / QUICK_START_NAME).exists()
    assert (tmp_path / ".winux-capsule-store").exists()
    assert Path(summary["capsule_store"]).exists()


def test_wizard_text(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    text = wizard_text(tmp_path)

    assert "WinUx First Run" in text
    assert "Where should Windows app state live?" in text
    assert "Leave the host machine alone" in text
