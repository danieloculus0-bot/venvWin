#!/usr/bin/env python3
"""Adapt the checksum-pinned BookwormPup64's ACTUAL active JWM theme.

/root/.jwmrc includes /root/.jwm/jwmrc-theme; a modified XDG template alone
does not restyle the taskbar. This conservative transformer preserves fonts,
menu structure and upstream JWM interactions.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

UPSTREAM_SHA256="3bfb767dc01c017cc31904c675a755e8957659aebafca63c12804b1f30659007"
REPLACEMENTS={
    "WindowStyle/Active/Foreground":"#101216",
    "WindowStyle/Active/Background":"#ff8a00",
    "WindowStyle/Active/Outline":"#ff8a00",
    "WindowStyle/Foreground":"#f4f1ea",
    "WindowStyle/Background":"#242932",
    "WindowStyle/Outline":"#444b54",
    "TaskListStyle/Active/Foreground":"#101216",
    "TaskListStyle/Active/Background":"#ff8a00",
    "TaskListStyle/Background":"#242932",
    "TrayStyle/Foreground":"#f4f1ea",
    "TrayStyle/Background":"#15181e",
    "PagerStyle/Outline":"#444b54",
    "PagerStyle/Foreground":"#242932",
    "PagerStyle/Background":"#101216",
    "PagerStyle/Active/Foreground":"#ff8a00",
    "PagerStyle/Active/Background":"#242932",
    "PopupStyle/Outline":"#444b54",
    "PopupStyle/Foreground":"#f4f1ea",
    "PopupStyle/Background":"#242932",
    "MenuStyle/Foreground":"#f4f1ea",
    "MenuStyle/Background":"#1d2229",
    "MenuStyle/Active/Foreground":"#101216",
    "MenuStyle/Active/Background":"#ff8a00",
}

def brand_jwm_theme(original: bytes) -> bytes:
    if hashlib.sha256(original).hexdigest()!=UPSTREAM_SHA256:
        raise ValueError("Unknown Puppy 10.0.12 theme bytes, refuse blind modification")
    root=ET.fromstring(original)
    if root.tag!="JWM":
        raise ValueError("Expected JWM XML theme")
    for selector,value in REPLACEMENTS.items():
        node=root.find(selector)
        if node is None or not node.text or not node.text.strip():
            raise ValueError(f"Missing upstream JWM property: {selector}")
        node.text=value
    # Upstream sections must remain intact. Theme XML does not modify keybindings.
    assert {child.tag for child in root}=={"WindowStyle","TaskListStyle","TrayStyle","PagerStyle","PopupStyle","MenuStyle"}
    ET.indent(root,space="  ")
    text=ET.tostring(root,encoding="unicode",xml_declaration=False)
    return ('<?xml version="1.0"?>\n'+text+'\n').encode()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    updated=brand_jwm_theme(a.input.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(updated)
    print("VENVWIN_AUTHENTIC_PUPPY_JWM_DARK_ORANGE_THEME_GENERATED")

if __name__=="__main__":
    main()
