from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def readme() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_names_current_product_and_license():
    text = readme()
    assert "# venvWin" in text
    assert "Windows-compatibility capsule" in text
    assert "GPL-3.0" in text
    assert "free of charge" in text


def test_readme_links_existing_product_gate_and_license():
    text = readme()
    for path in ("venvwin-portable/product-gate.md", "LICENSE"):
        assert path in text
        assert (ROOT / path).is_file()


def test_readme_links_archived_legacy_build_guidance():
    text = readme()
    path = "docs/archive/README_2026-10-20_before_refresh.md"
    assert path in text
    assert (ROOT / path).is_file()


def test_readme_distinguishes_experimental_build_from_verified_guest():
    text = readme()
    assert "Experimental" in text
    assert "CI alone does not demonstrate" in text
    assert "Physical hardware boots" in text


def test_readme_preserves_upstream_license_distinction():
    text = readme()
    assert "their own upstream licenses" in text
    assert "does not relicense those works" in text
    assert "No-fee distribution is project policy" in text
