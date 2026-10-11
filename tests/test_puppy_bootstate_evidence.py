"""Reconstruct mounted Puppy-style layers from actual evidence, not path guesses."""
from pathlib import Path

from venvwin.bootstate import (
    observed_mount_points, runtime_layers, BootState, bootstate_report,
)


def test_directory_exists_does_not_prove_layer_mount(tmp_path: Path):
    info = tmp_path / "mountinfo"
    info.write_text("19 1 0:7 / /initrd/venvwin/system_ro_fake rw - tmpfs tmpfs rw\n")
    states = runtime_layers(info)
    assert all(not x.mounted for x in states)
    assert all(x.source == "planned_unverified" for x in states)


def test_mountinfo_evidence_sets_only_real_mount(tmp_path: Path):
    info = tmp_path / "mountinfo"
    info.write_text(
        "20 1 0:9 / /initrd/venvwin/system_ro ro - squashfs /dev/loop0 ro\n"
        "21 1 0:10 / /initrd/venvwin/session_rw rw - tmpfs tmpfs rw\n"
    )
    points = observed_mount_points(info)
    assert "/initrd/venvwin/system_ro" in points
    states = {x.name: x for x in runtime_layers(info)}
    assert states["system_ro"].mounted
    assert states["session_rw"].mounted
    assert not states["save_rw"].mounted
    assert states["system_ro"].source == "observed_mountinfo"


def test_absent_mountinfo_cannot_claim_success(tmp_path: Path):
    assert observed_mount_points(tmp_path / "missing") == set()
    assert not any(x.mounted for x in runtime_layers(tmp_path / "missing"))


def test_ram_boot_flag_is_not_ram_copy_proof(monkeypatch):
    monkeypatch.setattr("venvwin.bootstate.read_kernel_cmdline",
                        lambda: "boot=live toram venvwin.mode=ram")
    report = bootstate_report()
    assert report.copy_to_ram_requested is True
    assert report.copy_to_ram is False
    assert "target-not-yet-boot-verified" in report.architecture
    assert "copy_to_ram_requested=true" in report.to_lines()
