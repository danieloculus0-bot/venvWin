"""Offline source/ISO packaging contract for venvWin Portable's one game.

These tests do not claim that an ISO has booted or that gameplay was measured.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "src/venvwin/games/emperor-gauntlet/play.html"
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


def test_iso_bundles_emperor_as_its_only_game():
    source = BUILDER.read_text(encoding="utf-8")
    assert "included_games=emperor-gauntlet" in source
    assert source.count("included_games=") == 1
    assert f"included_game_source=FUN@{SOURCE_COMMIT}" in source
    assert "included_game_engine=offline_html5_canvas_javascript" in source
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
    assert "venvWin-Emperor-Gauntlet.desktop" in source
    assert "included_game_launchers=venvwin-emperor-gauntlet.desktop" in source


def test_game_asset_required_before_bundling_and_manifest_tracks_source():
    source = BUILDER.read_text(encoding="utf-8")
    assert 'GAME_HTML="${ROOT_DIR}/src/venvwin/games/emperor-gauntlet/play.html"' in source
    assert "EMPEROR_GAUNTLET_MISSING" in source
    assert "included_game_asset=src/venvwin/games/emperor-gauntlet/play.html" in source
    assert "other_game_sources_excluded=venvwin/frontier_trail" in source
    subprocess.run(["bash", "-n", str(BUILDER)], check=True)
