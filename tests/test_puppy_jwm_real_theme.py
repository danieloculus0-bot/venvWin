"""The actual upstream Puppy taskbar must use the approved premium palette."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"puppy-native"/"brand-jwm-theme.py"

def module():
    spec=importlib.util.spec_from_file_location("venvwin_jwm_theme",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def test_theme_must_fail_closed_on_unknown_puppy_version():
    with pytest.raises(ValueError,match="Unknown Puppy"):
        module().brand_jwm_theme(b"<JWM><TrayStyle /></JWM>")

def test_dark_taskbar_and_orange_active_states_are_explicit():
    m=module()
    assert m.REPLACEMENTS["TrayStyle/Background"]=="#15181e"
    assert m.REPLACEMENTS["TaskListStyle/Active/Background"]=="#ff8a00"
    assert m.REPLACEMENTS["MenuStyle/Active/Background"]=="#ff8a00"
    assert m.REPLACEMENTS["WindowStyle/Background"]=="#242932"
    assert len(m.UPSTREAM_SHA256)==64

def test_builder_installs_real_jwm_theme_into_guest_addon():
    script=(ROOT/"puppy-native"/"build-puppy.sh").read_text()
    assert "brand-jwm-theme.py" in script
    assert "root/.jwm/jwmrc-theme" in script
    assert "etc/xdg/templates/_root_.jwmrc" in script
