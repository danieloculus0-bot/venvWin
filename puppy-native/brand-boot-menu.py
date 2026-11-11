#!/usr/bin/env python3
"""Brand verified upstream boot menus WITHOUT changing kernel/initrd commands."""
from __future__ import annotations
import argparse
from pathlib import Path


GRUB_ENTRIES = 7
BIOS_ENTRIES = 9


def brand_grub(original: str) -> str:
    if original.count('background_image /boot/splash.png') != 1:
        raise ValueError('Upstream GRUB splash layout changed')
    if original.count('menuentry "BookwormPup64 10.0.12') != GRUB_ENTRIES:
        raise ValueError('Unexpected GRUB Puppy boot entry count')
    result = original.replace('menuentry "BookwormPup64 10.0.12', 'menuentry "venvWin Portable')
    result = result.replace('color_normal=cyan/black', 'color_normal=light-gray/black')
    result = result.replace('menu_color_highlight=yellow/red', 'menu_color_highlight=yellow/black')
    return result


def brand_bios(original: str) -> str:
    if original.count('splashimage /boot/splash.jpg') != 1:
        raise ValueError('Upstream GRUB4DOS splash layout changed')
    if original.count('title BookwormPup64 10.0.12') != BIOS_ENTRIES:
        raise ValueError('Unexpected GRUB4DOS Puppy boot entry count')
    result = original.replace('title BookwormPup64 10.0.12', 'title venvWin Portable')
    result = result.replace('color light-gray/black yellow/red cyan/black light-blue/black',
                            'color light-gray/black yellow/black light-gray/black light-gray/black')
    return result


def verify_preserves_boot_commands(before: str, after: str, kind: str) -> None:
    # Only public-facing label, menu color and splash source may change.
    for line in before.splitlines():
        stripped = line.strip()
        if (stripped.startswith(('linux ', 'kernel ', 'initrd ', 'echo "Loading',
                                'errorcheck ', 'configfile ', 'chainloader ')) and
                line not in after.splitlines()):
            raise ValueError(f'{kind} critical upstream boot command changed: {stripped}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=['grub', 'bios'], required=True)
    args = parser.parse_args()
    before = args.input.read_text(encoding='utf-8')
    after = brand_grub(before) if args.kind == 'grub' else brand_bios(before)
    verify_preserves_boot_commands(before, after, args.kind)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(after, encoding='utf-8')
    print(f'VENVWIN_{args.kind.upper()}_LABELS_BRANDED_BOOT_COMMANDS_PRESERVED')


if __name__ == '__main__':
    main()
