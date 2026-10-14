"""Source-only safety tests for the isolated Puppy 10.0.12 app trimmer.

Passing these tests does NOT prove guest boot, office fidelity, or Wine execution.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / "puppy-native" / "optimize-slacko-apps.py"
PROTECTED = [
    "usr/bin/abiword", "usr/bin/gnumeric", "usr/bin/ssconvert", "usr/bin/mtpaint",
    "usr/bin/jwm", "usr/local/bin/rox", "usr/local/bin/frisbee",
    "usr/bin/connman-gtk", "usr/bin/mpv", "usr/bin/smplayer",
    "usr/bin/aplay", "usr/bin/pipewire",
    "usr/bin/simplescreenrecorder",
    "usr/share/applications/simplescreenrecorder.desktop",
    "usr/share/applications/abiword.desktop",
    "usr/share/applications/gnumeric.desktop",
    "usr/share/applications/frisbee.desktop",
    "usr/share/applications/mpv.desktop",
    "usr/share/applications/smplayer.desktop",
    "usr/share/applications/mtpaint.desktop",
    "usr/lib/x86_64-linux-gnu/libc.so.6",
    "usr/lib/x86_64-linux-gnu/libasound.so.2",
    "usr/lib/wine/wine64", "usr/bin/wineserver",
    "opt/FirefoxESR-portable64/firefox64/firefox",
    "usr/share/applications/claws-mail.desktop",
]


def fixture(tmp_path: Path) -> Path:
    root = tmp_path / "dist" / "puppy" / "root"
    for rel in PROTECTED:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("immutable: " + rel)
    targets = [
        "usr/bin/mhwaveedit", "usr/share/applications/mhwaveedit.desktop",
        "usr/share/applications/defaultaudioeditor.desktop",
        "usr/bin/easytag", "usr/bin/qwinff",
        "usr/bin/celluloid", "usr/bin/simsu", "usr/share/applications/simsu.desktop",
        "usr/bin/deadbeef", "usr/share/applications/deadbeef.desktop",
        "usr/share/applications/smplayer_enqueue.desktop",
        "opt/deadbeef/bin/deadbeef", "opt/deadbeef/lib/deadbeef/private.so",
    ]
    for rel in targets:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("remove: " + rel)
    wrappers = {
        "usr/local/bin/defaultaudioplayer": '#!/bin/sh\nexec deadbeef "$@"\n',
        "usr/local/bin/defaultcdplayer": '#!/bin/sh\nexec deadbeef /dev/sr0/all.cda "$@"\n',
        "usr/local/bin/defaultaudioeditor": '#!/bin/sh\nexec mhwaveedit "$@"\n',
    }
    for rel, payload in wrappers.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    return root


def invoke(root: Path, report: Path, apply: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), str(root), "--report", str(report)]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=15)


def test_plan_does_not_change_original_copy(tmp_path: Path):
    root = fixture(tmp_path)
    path = root / "usr/bin/mhwaveedit"
    before = path.read_bytes()
    report_path = tmp_path / "plan.json"
    r = invoke(root, report_path)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert path.read_bytes() == before
    report = json.loads(report_path.read_text())
    assert report["status"] == "PLAN_ONLY"
    assert report["removed"] == []


def test_actual_trim_only_removes_standalone_extras(tmp_path: Path):
    root = fixture(tmp_path)
    report_path = tmp_path / "applied.json"
    r = invoke(root, report_path, apply=True)
    assert r.returncode == 0, (r.stdout, r.stderr)
    for rel in PROTECTED:
        assert (root / rel).read_text() == "immutable: " + rel
    for rel in ("usr/bin/mhwaveedit", "usr/bin/deadbeef", "opt/deadbeef",
                "usr/bin/celluloid", "usr/bin/simsu", "usr/bin/qwinff"):
        assert not (root / rel).exists()
    report = json.loads(report_path.read_text())
    assert (root / "usr/local/bin/defaultaudioplayer").read_text().startswith("#!/bin/sh\nexec mpv")
    assert (root / "usr/local/bin/defaultcdplayer").read_text().startswith("#!/bin/sh\nexec mpv")
    assert "mpv cdda://" in (root / "usr/local/bin/defaultcdplayer").read_text()
    assert "Install one via Synaptic" in (root / "usr/local/bin/defaultaudioeditor").read_text()
    assert (root / "usr/bin/simplescreenrecorder").exists()
    assert (root / "usr/share/applications/simplescreenrecorder.desktop").exists()
    assert report["status"] == "TEST_COPY_MUTATED"
    assert report["system_or_wine_library_components_removed"] == 0
    assert report["guest_puppy_boot"] == "NOT_TESTED_BY_THIS_SCRIPT"
    assert report["guest_wine_32_and_64"] == "NOT_TESTED_BY_THIS_SCRIPT"


def test_not_allowed_to_prune_machine_root(tmp_path: Path):
    r = invoke(Path("/"), tmp_path / "bad.json", apply=True)
    assert r.returncode != 0
    assert "STOP_UNSAFE_OPTIMIZER_ROOT" in (r.stdout + r.stderr)


def test_no_library_paths_or_wine_in_direct_removal_list():
    import ast
    tree = ast.parse(SCRIPT.read_text())
    val = next(ast.literal_eval(node.value) for node in tree.body
               if isinstance(node, ast.Assign) and
               any(getattr(t, "id", None) == "REMOVAL_TARGETS" for t in node.targets))
    for group, paths in val.items():
        for p in paths:
            assert not p.startswith(("usr/lib/", "usr/lib64/", "lib/", "etc/", "root/"))
            assert "wine" not in p.lower()
            assert "gnumeric" not in p and "abiword" not in p
            assert "frisbee" not in p and "connman" not in p
            assert not p.startswith("usr/bin/mpv")
            assert not p.startswith("usr/bin/smplayer")

def test_protect_package_management_and_db_metadata():
    source=SCRIPT.read_text()
    for key in ("usr/sbin/synaptic", "usr/bin/apt", "usr/bin/dpkg",
                "usr/local/petget/pkg_chooser.sh", "usr/local/bin/sfs_load",
                "var/lib/dpkg/", "var/lib/apt/"):
        assert key in source
    assert "NOT_PROVEN_NEEDS_POST_TRIM_DPKG_PET_AUDIT" in source

def test_refuse_unknown_audio_handler(tmp_path: Path):
    root=fixture(tmp_path)
    handler=root/"usr/local/bin/defaultaudioplayer"
    handler.write_text("#!/bin/sh\nrm -rf /\n",encoding="utf-8")
    r=invoke(root, tmp_path/"unknown.json", apply=True)
    assert r.returncode != 0
    assert "STOP_UNKNOWN_DEFAULT_HANDLER" in (r.stderr+r.stdout)
