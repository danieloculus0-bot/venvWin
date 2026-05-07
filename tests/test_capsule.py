from pathlib import Path

from venvwin.capsule import create_capsule, list_capsules, load_capsule, slugify_app_name
from venvwin.profile import RunnerProfile


def test_slugify_app_name():
    assert slugify_app_name("Notepad++") == "notepad"
    assert slugify_app_name("  My App  ") == "my-app"
    assert slugify_app_name("!!!") == "app"


def test_create_list_load_capsule(tmp_path: Path):
    profile = RunnerProfile.default()
    capsule = create_capsule(tmp_path, "Test App", profile)

    assert capsule.capsule_id == "test-app"
    assert (tmp_path / "test-app" / "venvwin.json").exists()
    assert (tmp_path / "test-app" / "prefix").is_dir()

    capsules = list_capsules(tmp_path)
    assert len(capsules) == 1
    assert capsules[0].app_name == "Test App"

    loaded = load_capsule(tmp_path, "test-app")
    assert loaded.app_name == "Test App"
    assert loaded.profile.runner == "wine"
