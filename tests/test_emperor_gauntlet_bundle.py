"""Offline source/ISO packaging contract for venvWin Portable's two games.

These tests do not claim that an ISO has booted or that gameplay was measured.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "src/venvwin/games/emperor-gauntlet/play.html"
CLETUS = ROOT / "src/venvwin/games/cletus/play.html"
CLETUS_COVER = ROOT / "src/venvwin/games/cletus/cover.svg"
CLETUS_ICON = ROOT / "src/venvwin/games/cletus/icon.svg"
BUILDER = ROOT / "venvwin-portable/build-iso.sh"
SOURCE_COMMIT = "49dfdb3127e6ba2fcacd610cfea211a61ee36e53"


class ExternalAssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.remote_runtime_assets = []
        self.scripts = []
        self.canvas_count = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "canvas":
            self.canvas_count += 1
        if tag == "script":
            self.scripts.append(attributes)
        if tag in ("script", "img", "audio", "video", "source"):
            if attributes.get("src"):
                self.remote_runtime_assets.append(attributes["src"])
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.remote_runtime_assets.append(attributes.get("href"))


def test_embedded_game_is_real_self_contained_canvas_game():
    page = GAME.read_text(encoding="utf-8")
    parser = ExternalAssetParser()
    parser.feed(page)
    assert "<title>Emperor Gauntlet" in page
    assert parser.canvas_count >= 1
    assert parser.scripts and all(not tag.get("src") for tag in parser.scripts)
    assert not parser.remote_runtime_assets
    assert "requestAnimationFrame(" in page
    assert "getContext(" in page
    # The game may include harmless hyperlinks; runtime never downloads scripts.
    assert not re.search(r"\bfetch\s*\(", page)
    assert not re.search(r"\bimport\s+.*\bfrom\b", page)


def test_iso_bundles_emperor_and_cletus():
    source = BUILDER.read_text(encoding="utf-8")
    assert "included_games=emperor-gauntlet,cletus-saves-candy" in source
    assert source.count("included_games=") == 1
    assert f"included_game_source=FUN@{SOURCE_COMMIT}" in source
    assert "included_game_engine=offline_html5_canvas_javascript" in source
    assert "included_game_source_cletus=FUN@e26473565988ef4d8bbe449ec36ccbe5a65c623d" in source
    assert "included_game_asset_cletus=src/venvwin/games/cletus/play.html" in source
    assert "venvwin/frontier_trail/" in source
    assert "--exclude 'venvwin/frontier_trail/'" in source
    assert "venvwin-frontier-trail.desktop" not in source
    assert "venvwin-frontier-trail.svg" not in source
    assert "Name=Daniel Boone: Frontier Trail" not in source


def test_boot_image_includes_modern_html5_engine_and_game_launcher():
    source = BUILDER.read_text(encoding="utf-8")
    assert "echo 'epiphany-browser' >> config/package-lists/00-venvwin-core.list.chroot" in source
    assert "firefox-esr" in source  # installed in standard / privacy
    assert "GAME_HTML=/opt/venvwin/src/venvwin/games/emperor-gauntlet/play.html" in source
    assert 'URL="file://${GAME_HTML}"' in source
    assert "exec firefox-esr --new-window" in source
    assert "exec epiphany --new-window" in source
    assert "netsurf-gtk --new-window" not in source
    assert "Name=Emperor Gauntlet" in source
    assert "Categories=Game;" in source
    assert "Name=Cletus Saves Candy" in source
    assert "Icon=venvwin-cletus-saves-candy" in source
    assert "venvWin-Cletus-Saves-Candy.desktop" in source
    assert "GAME_HTML=/opt/venvwin/src/venvwin/games/cletus/play.html" in source
    assert "venvWin-Emperor-Gauntlet.desktop" in source
    assert "included_game_launchers=venvwin-emperor-gauntlet.desktop,venvwin-cletus-saves-candy.desktop" in source
    assert "included_game_icons=venvwin-emperor-gauntlet.svg,venvwin-cletus-saves-candy.svg" in source


def test_game_asset_required_before_bundling_and_manifest_tracks_source():
    source = BUILDER.read_text(encoding="utf-8")
    assert 'GAME_HTML="${ROOT_DIR}/src/venvwin/games/emperor-gauntlet/play.html"' in source
    assert "EMPEROR_GAUNTLET_MISSING" in source
    assert "included_game_asset=src/venvwin/games/emperor-gauntlet/play.html" in source
    assert 'CLETUS_HTML="${ROOT_DIR}/src/venvwin/games/cletus/play.html"' in source
    assert "CLETUS_SAVES_CANDY_MISSING" in source
    assert "other_game_sources_excluded=venvwin/frontier_trail" in source
    subprocess.run(["bash", "-n", str(BUILDER)], check=True)

def test_cletus_offline_bundle_and_branded_artwork():
    page = CLETUS.read_text(encoding="utf-8")
    parser = ExternalAssetParser()
    parser.feed(page)
    assert "<title>Cletus Saves Candy</title>" in page
    assert parser.scripts and all(not tag.get("src") for tag in parser.scripts)
    assert not parser.remote_runtime_assets
    assert "https://fonts.googleapis.com" not in page
    assert "manifest.webmanifest" not in page
    assert "Cletus%20Saves%20Candy_%20Neon%20City%20Rescue.png" not in page.split("<body", 1)[-1]
    assert "cover.svg" in page
    assert "requestAnimationFrame" in page
    for art in (CLETUS_ICON, CLETUS_COVER):
        assert art.stat().st_size > 300
        assert ET.parse(art).getroot().tag.endswith("svg")


def test_both_games_have_own_menu_and_desktop_icons():
    source = BUILDER.read_text(encoding="utf-8")
    for game in ("emperor-gauntlet", "cletus-saves-candy"):
        assert f"config/includes.chroot/usr/share/applications/venvwin-{game}.desktop" in source
        assert f"Icon=venvwin-{game}" in source
        assert f"config/includes.chroot/usr/share/pixmaps/venvwin-{game}.svg" in source
    assert "venvWin-Cletus-Saves-Candy.desktop" in source
    assert "venvWin-Emperor-Gauntlet.desktop" in source
    assert "Categories=Game;" in source
