from pathlib import Path
import importlib.util,pytest

src=Path(__file__).resolve().parents[1]/"puppy-native"/"brand-jwm-template.py"

def module():
    spec=importlib.util.spec_from_file_location("brand_jwm",src)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def test_theme_preserves_jwm_navigation_actions():
    original="""<JWM>
<!-- XDG_JWMRC_VERSION_001 -->
<RootMenu label="Menu"><Include>exec:app</Include></RootMenu>
<WindowStyle><Background>#fffa71:#ffda51</Background>
<Active><Background>#ffda51:#ffa100</Background></Active></WindowStyle>
<PagerStyle><Foreground>#ffc100</Foreground><Background>#ffc100</Background>
<Active><Foreground>#ff8100</Foreground><Background>#ffa100</Background></Active></PagerStyle>
<MenuStyle><Foreground>black</Foreground><Background>#ffda51</Background>
<Active><Foreground>black</Foreground><Background>#ffda51:#ffa100</Background></Active></MenuStyle>
<PopupStyle><Foreground>black</Foreground><Background>yellow</Background></PopupStyle>
PUPPYMENU jwm-xdgmenu /etc/xdg/menus/puppy-system.menu
<Key mask="A" key="F4">close</Key>
<Include>/root/.jwmrc-tray</Include>
</JWM>"""
    after=module().brand_jwm(original)
    assert '<RootMenu label="venvWin"' in after
    assert "#ff8a00" in after
    assert "#161b23" in after
    assert '<Key mask="A" key="F4">close</Key>' in after
    assert 'PUPPYMENU jwm-xdgmenu' in after

def test_jwm_unknown_input_fails_closed():
    with pytest.raises(ValueError):
        module().brand_jwm("<JWM><RootMenu label='Menu'/></JWM>")
