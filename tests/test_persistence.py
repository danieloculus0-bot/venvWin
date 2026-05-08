from pathlib import Path

from venvwin.persistence import choose_capsule_store, persistence_report


def test_choose_capsule_store_uses_home_fallback(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    chosen = choose_capsule_store(tmp_path)

    assert chosen.source == "home-fallback"
    assert chosen.path == tmp_path / "WinUx-Capsules"
    assert chosen.writable is True
    assert chosen.portable_owned is False
    assert chosen.host_risk is True


def test_choose_capsule_store_prefers_env(tmp_path: Path, monkeypatch):
    target = tmp_path / "portable-store"
    monkeypatch.setenv("VENVWIN_HOME", str(target))

    chosen = choose_capsule_store(tmp_path)

    assert chosen.source == "VENVWIN_HOME"
    assert chosen.path == target
    assert chosen.writable is True
    assert chosen.portable_owned is True
    assert chosen.host_risk is False


def test_persistence_report_has_candidates(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("VENVWIN_HOME", raising=False)

    report = persistence_report(tmp_path)

    assert "chosen" in report
    assert "candidates" in report
    assert "leave_no_trace" in report
    assert "host_write_warning" in report
    assert report["candidates"]
