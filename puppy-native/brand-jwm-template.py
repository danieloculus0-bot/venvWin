#!/usr/bin/env python3
"""Conservatively brand the actual upstream Puppy JWM template.

Leave include files, shortcut keys, application menus and actions intact.
Refuse unfamiliar template structure instead of damaging the desktop.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

PALETTE = {
    "dark": "#161b23",
    "panel": "#1e232b",
    "active": "#ff8a00",
    "active_dark": "#d96e00",
    "text": "#f4f1ea",
    "muted": "#aeb4be",
}

def patch_style(source: str, tag: str, before: str, after: str) -> str:
    match = re.search(r"(<"+re.escape(tag)+r">)(.*?)(</"+re.escape(tag)+r">)",
                      source, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Upstream JWM {tag} section missing")
    body = match.group(2)
    if before not in body:
        raise ValueError(f"Upstream JWM {tag} value changed: {before}")
    replacement = body.replace(before, after)
    return source[:match.start(2)] + replacement + source[match.end(2):]

def brand_jwm(source: str) -> str:
    if "<!-- XDG_JWMRC_VERSION_001 -->" not in source:
        raise ValueError("Unknown upstream JWM template version")
    if source.count("<Include>/root/.jwmrc-tray</Include>") != 1:
        raise ValueError("Upstream JWM tray include missing")
    branded = source.replace('<RootMenu label="Menu"', '<RootMenu label="venvWin"')
    branded = patch_style(branded, "WindowStyle", "#fffa71:#ffda51", "#252b34:#191e26")
    branded = patch_style(branded, "WindowStyle", "#ffda51:#ffa100", "#ff8a00:#d96e00")
    branded = patch_style(branded, "PagerStyle", "#ffc100", "#2a313b")
    branded = patch_style(branded, "PagerStyle", "#ff8100", "#ff8a00")
    branded = patch_style(branded, "PagerStyle", "#ffa100", "#ff8a00")
    branded = patch_style(branded, "MenuStyle", "<Foreground>black</Foreground>",
                          "<Foreground>#f4f1ea</Foreground>")
    branded = patch_style(branded, "MenuStyle", "<Background>#ffda51</Background>",
                          "<Background>#161b23</Background>")
    branded = patch_style(branded, "MenuStyle", "#ffda51:#ffa100", "#ff8a00:#d96e00")
    branded = patch_style(branded, "PopupStyle", "<Foreground>black</Foreground>",
                          "<Foreground>#f4f1ea</Foreground>")
    branded = patch_style(branded, "PopupStyle", "<Background>yellow</Background>",
                          "<Background>#161b23</Background>")
    for line in source.splitlines():
        s=line.strip()
        if s.startswith(("<Key ","<Include>","PUPPYMENU","<StartupCommand>")) and line not in branded.splitlines():
            raise ValueError(f"JWM critical upstream menu/shortcut altered: {s}")
    return branded

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    output=brand_jwm(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(output,encoding="utf-8")
    print("VENVWIN_ACTUAL_JWM_MENU_THEME_BRANDED_SHORTCUTS_PRESERVED")

if __name__=="__main__":
    main()
