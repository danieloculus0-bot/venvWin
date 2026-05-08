from pathlib import Path

from venvwin.gui_first_run import display_model, status_color


def test_display_model_has_first_boot_fields(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    model = display_model(tmp_path)

    assert "capsule_store" in model
    assert "storage_status" in model
    assert "storage_message" in model
    assert "leave_no_trace" in model
    assert "portable_owned" in model
    assert "host_risk" in model
    assert model["capsule_store"] == str(tmp_path / "WinUx-Capsules")


def test_status_color_mapping():
    assert status_color("leave-no-trace-ok") == "#22c55e"
    assert status_color("disposable-warning") == "#f59e0b"
    assert status_color("host-risk-warning") == "#f59e0b"
    assert status_color("unknown") == "#ef4444"
