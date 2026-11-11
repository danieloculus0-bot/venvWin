"""Puppy splash changes must not remove ANY boot options."""
import importlib.util
from pathlib import Path


def load():
    source = Path(__file__).resolve().parents[1]/'puppy-native'/'brand-boot-menu.py'
    spec = importlib.util.spec_from_file_location('brand_boot_menu', source)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def test_grub_keeps_all_boot_commands():
    b=load()
    original='background_image /boot/splash.png\ncolor_normal=cyan/black\nmenu_color_highlight=yellow/red\n'
    for i in range(7):
        original+=f'menuentry "BookwormPup64 10.0.12 - {i}" {{\n linux /vmlinuz pmedia=cd pfix=fsck\n initrd /initrd.gz\n}}\n'
    rewritten=b.brand_grub(original)
    assert rewritten.count('menuentry "venvWin Portable')==7
    b.verify_preserves_boot_commands(original,rewritten,'grub')
    assert rewritten.count('linux /vmlinuz') ==7
    assert rewritten.count('initrd /initrd.gz')==7


def test_grub_rejects_layout_drift():
    b=load()
    import pytest
    with pytest.raises(ValueError):
        b.brand_grub('menuentry "Puppy" {}')


def test_bios_keeps_ram_options():
    b=load()
    original='splashimage /boot/splash.jpg\n'
    for i in range(9):
        original+=f'title BookwormPup64 10.0.12 - {i}\n  kernel /vmlinuz pmedia=cd pfix=fsck,fsckp,copy\n  initrd /initrd.gz\n'
    after=b.brand_bios(original)
    assert after.count('title venvWin Portable')==9
    assert after.count('pfix=fsck,fsckp,copy')==9
    b.verify_preserves_boot_commands(original,after,'bios')
