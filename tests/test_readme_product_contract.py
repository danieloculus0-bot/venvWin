from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_names_public_product_without_alternate_codename():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "venvWin Portable" in readme
    assert "Wine is allowed as backend number one. Wine is not the product." in readme


def test_readme_links_build_and_flash_guides():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "venvwin-portable/local-flash-ready-build.md" in readme
    assert "venvwin-portable/usb-flash-guide.md" in readme
    assert "status=FLASH_READY" in readme


def test_readme_names_direct_powershell_wsl_runner():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Windows PowerShell WSL build runner" in readme
    assert ".\\venvwin-portable\\run-wsl-flash-ready.ps1" in readme


def test_readme_requires_visible_first_boot_shortcuts():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for launcher in [
        "venvWin-First-Boot.desktop",
        "venvWin-Dashboard.desktop",
        "venvWin-Capsules.desktop",
        "venvWin-Doctor.desktop",
        "venvWin-Private-Browser.desktop",
    ]:
        assert launcher in readme


def test_readme_does_not_use_stale_public_artifact_names():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    forbidden = [
        "venvWin",
        "VENVWIN",
        "venvWin",
        "WinUX",
        "venvWin Portable",
        "venvwin-portable-alpha",
        "venvwin-flash-ready",
        "venvwin-portable-flash-ready-standard",
    ]

    for text in forbidden:
        assert text not in readme
