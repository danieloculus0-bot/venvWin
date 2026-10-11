"""Prevent obsolete full-ISO size targets and accidental multi-profile builds."""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MULTI = ROOT / "venvwin-portable" / "build-all-profiles.sh"
COMPARISON = ROOT / "venvwin-portable" / "compare-profiles.sh"


def test_shell_script_syntax():
    subprocess.run(["bash", "-n", str(MULTI)], check=True)
    subprocess.run(["bash", "-n", str(COMPARISON)], check=True)


def test_full_three_iso_build_requires_explicit_opt_in():
    environment = dict(os.environ)
    environment.pop("VENVWIN_ALLOW_MULTI_ISO_BUILD", None)
    outcome = subprocess.run(["bash", str(MULTI)], env=environment,
                             text=True, capture_output=True, check=False)
    assert outcome.returncode == 2
    assert "disabled by default" in outcome.stderr
    assert "VENVWIN_ALLOW_MULTI_ISO_BUILD=1" in outcome.stderr


def test_comparison_reports_measurement_not_sellability():
    script = COMPARISON.read_text()
    assert "core_over_hard_budget" in script
    assert "core_above_soft_target" in script
    assert "core_within_size_goal_boot_unverified" in script
    assert "historical_full_profile_manual_only" in script
    assert "boot_verified=unverified_by_size_report" in script
    assert "sellable-target" not in script
    assert "hard-concern-bloated-goblin" not in script


def test_puppy_architecture_contract_matches_package_split():
    contract = (ROOT / "docs" / "puppy-bean-evidence-contract.md").read_text()
    profiles = (ROOT / "venvwin-portable" / "package-profiles.md").read_text()
    assert "61" in contract and "28" in contract
    assert "61" in profiles and "28" in profiles
    assert "39 package" not in contract
    assert "50 heavier" not in contract
    target = (ROOT / "docs" / "portable-live-boot.md").read_text()
    assert "not the product definition" in target
