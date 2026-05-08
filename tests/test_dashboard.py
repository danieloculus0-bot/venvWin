from pathlib import Path

from venvwin.dashboard import dashboard_model, render_dashboard


def test_dashboard_model_has_required_sections(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VENVWIN_HOME", str(tmp_path / "WINUXDATA" / "WinUx-Capsules"))

    model = dashboard_model(root=tmp_path / "runtime", home=tmp_path / "home")

    assert "runtime_root" in model
    assert "storage" in model
    assert "first_run" in model
    assert "health" in model
    assert "capsules" in model
    assert "capsule_count" in model
    assert model["storage"]["chosen"]["writable"] is True


def test_dashboard_render_contains_product_signals(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VENVWIN_HOME", str(tmp_path / "WINUXDATA" / "WinUx-Capsules"))

    model = dashboard_model(root=tmp_path / "runtime", home=tmp_path / "home")
    html = render_dashboard(model)

    assert "WinUx Dashboard" in html
    assert "Storage destination" in html
    assert "Leave no trace" in html
    assert "Host write risk" in html
    assert "Capsules" in html
    assert "Status JSON" in html
    assert "Doctor JSON" in html
