from pathlib import Path

from venvwin.persistence import choose_capsule_store, persistence_report


def test_choose_capsule_store_uses_home_fallback(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)
    monkeypatch.delenv("VENVWIN_HOME_SOURCE", raising=False)

    chosen = choose_capsule_store(tmp_path)

    assert chosen.source == "home-fallback"
    assert chosen.path == tmp_path / "WinUx-Capsules"
    assert chosen.writable is True
    assert chosen.portable_owned is False
    assert chosen.host_risk is True


def test_choose_capsule_store_prefers_env(tmp_path: Path, monkeypatch):
    target = tmp_path / "portable-store"
    monkeypatch.setenv("VENVWIN_HOME", str(target))
    monkeypatch.delenv("VENVWIN_HOME_SOURCE", raising=False)

    chosen = choose_capsule_store(tmp_path)

    assert chosen.source == "VENVWIN_HOME"
    assert chosen.path == target
    assert chosen.writable is True
    assert chosen.portable_owned is True
    assert chosen.host_risk is False


def test_env_source_preserves_home_fallback_risk(tmp_path: Path, monkeypatch):
    target = tmp_path / "WinUx-Capsules"
    monkeypatch.setenv("VENVWIN_HOME", str(target))
    monkeypatch.setenv("VENVWIN_HOME_SOURCE", "home-fallback")

    chosen = choose_capsule_store(tmp_path)
    report = persistence_report(tmp_path)

    assert chosen.source == "home-fallback"
    assert chosen.path == target
    assert chosen.portable_owned is False
    assert chosen.host_risk is True
    assert report["leave_no_trace"] is False
    assert report["host_write_warning"] is True


def test_env_source_can_mark_live_home_overlay_disposable(tmp_path: Path, monkeypatch):
    target = tmp_path / "WinUx-Capsules"
    monkeypatch.setenv("VENVWIN_HOME", str(target))
    monkeypatch.setenv("VENVWIN_HOME_SOURCE", "live-home-overlay")

    report = persistence_report(tmp_path)
    chosen = report["chosen"]

    assert chosen["source"] == "live-home-overlay"
    assert chosen["portable_owned"] is True
    assert chosen["host_risk"] is False
    assert report["leave_no_trace"] is True
    assert report["disposable_warning"] is True


def test_persistence_report_has_candidates(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)
    monkeypatch.delenv("VENVWIN_HOME_SOURCE", raising=False)

    report = persistence_report(tmp_path)

    assert "chosen" in report
    assert "candidates" in report
    assert "leave_no_trace" in report
    assert "host_write_warning" in report
    assert report["candidates"]
