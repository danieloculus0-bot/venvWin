#!/usr/bin/env python3
"""Verify a REAL guest screenshot contains the shipped venvWin Amber Arc artwork.

Checks unobstructed regions for appearance, not merely the presence of a bitmap
in the ISO. Does not inspect/mock a fake desktop. Fails if the stock Puppy
background is visible in these regions after native first-run UI settles.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

# Exclude Puppy taskbar, left icons and upper-right Conky.
# Logo glow and lower-right Amber Arc distinguish venvWin artwork.
REGIONS = (
    (0.305, 0.275, 0.54, 0.46),
    (0.56, 0.65, 0.74, 0.80),
    (0.545, 0.78, 0.74, 0.865),
)

def compare_capture(wallpaper: Path, capture: Path) -> list[float]:
    with Image.open(wallpaper) as src, Image.open(capture) as screen:
        expected=src.convert("RGB").resize(screen.size, Image.Resampling.LANCZOS)
        actual=screen.convert("RGB")
        if actual.width < 1024 or actual.height < 700:
            raise ValueError("Guest desktop resolution below supported verification threshold")
        scores=[]
        for coords in REGIONS:
            box=tuple(round(v * (actual.width if i%2==0 else actual.height))
                      for i,v in enumerate(coords))
            diff=ImageChops.difference(actual.crop(box),expected.crop(box))
            score=sum(ImageStat.Stat(diff).mean)/3
            scores.append(round(score,3))
        return scores

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--wallpaper",required=True,type=Path)
    p.add_argument("--capture",required=True,type=Path)
    args=p.parse_args()
    if not args.wallpaper.is_file() or not args.capture.is_file():
        raise SystemExit("WALLPAPER_REAL_CAPTURE_OR_EXPECTED_IMAGE_MISSING")
    scores=compare_capture(args.wallpaper,args.capture)
    print("ACTUAL_GUEST_WALLPAPER_REGION_DIFFS="+",".join(map(str,scores)))
    # Screenshot/image interpolation and color-space differences remain small
    # on the correct artwork, while old Puppy/old venvWin SVG fails >30/50.
    if scores[0] > 23 or scores[1] > 23 or scores[2] > 23:
        print("ACTUAL_GUEST_APPROVED_WALLPAPER_NOT_VISIBLE_REFUSE_PASS")
        return 1
    print("ACTUAL_GUEST_APPROVED_VENVWIN_WALLPAPER_VISIBLE_PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
