from pathlib import Path

from venvwin.dashboard import dashboard_model, dashboard_url, get_or_create_token, render_dashboard, token_link


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


def test_dashboard_token_links():
    assert token_link("/api/status", None) == "/api/status"
    assert token_link("/api/status", "abc") == "/api/status?token=abc"
    assert token_link("/api/status?x=1", "abc") == "/api/status?x=1&token=abc"
    assert dashboard_url("0.0.0.0", 8787, "abc").startswith("http://127.0.0.1:8787/")
    assert "token=abc" in dashboard_url("0.0.0.0", 8787, "abc")


def test_get_or_create_token_persists(tmp_path: Path):
    first = get_or_create_token(tmp_path)
    second = get_or_create_token(tmp_path)

    assert first == second
    assert len(first) >= 20
    assert (tmp_path / ".winux-dashboard-token").exists()


def test_dashboard_render_includes_tokenized_api_links(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VENVWIN_HOME", str(tmp_path / "WINUXDATA" / "WinUx-Capsules"))

    model = dashboard_model(root=tmp_path / "runtime", home=tmp_path / "home")
    html = render_dashboard(model, token="abc")

    assert "/api/status?token=abc" in html
    assert "/api/doctor?token=abc" in html
    assert "/api/initialize?token=abc" in html
