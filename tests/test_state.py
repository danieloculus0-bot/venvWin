from pathlib import Path

from venvwin.state import default_filesystem_mappings, default_permission_policy, ensure_prefix_shape


def test_default_filesystem_mappings_use_home(tmp_path: Path):
    mappings = default_filesystem_mappings(tmp_path)

    assert mappings[r"C:\\users\\venvwin\\Documents"] == str(tmp_path / "Documents")
    assert mappings[r"C:\\users\\venvwin\\Downloads"] == str(tmp_path / "Downloads")


def test_default_permission_policy_is_user_safe():
    policy = default_permission_policy()

    assert policy["run_as_root"] is False
    assert policy["allow_system_writes"] is False
    assert policy["protect_user_documents_on_reset"] is True


def test_ensure_prefix_shape(tmp_path: Path):
    ensure_prefix_shape(tmp_path)

    assert (tmp_path / "drive_c" / "Program Files").is_dir()
    assert (tmp_path / "drive_c" / "users" / "venvwin" / "Documents").is_dir()
    assert (tmp_path / "drive_c" / "users" / "venvwin" / "AppData" / "Roaming").is_dir()
