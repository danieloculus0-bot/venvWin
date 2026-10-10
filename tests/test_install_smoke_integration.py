"""Real CLI-process smoke tests using an isolated fake Wine runner.

The fake runner emulates process/prefix behavior, not Windows API compatibility.
Full ISO boot and genuine Wine checks are separate release gates.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def environment(tmp_path: Path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    wine = bindir / "wine"
    wine.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, pathlib, sys\n"
        "prefix = pathlib.Path(os.environ['WINEPREFIX'])\n"
        "prefix.mkdir(parents=True, exist_ok=True)\n"
        "(prefix / 'smoke-runner.json').write_text(json.dumps({"
        "'args': sys.argv[1:], 'arch': os.environ['WINEARCH']"
        "}), encoding='utf-8')\n"
        "sys.exit(19 if '--fail-test' in sys.argv else 0)\n",
        encoding="utf-8",
    )
    wine.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    env["VENVWIN_HOME"] = str(tmp_path / "state")
    return tmp_path, env


def run_cli(env: dict[str, str], *args: str, exit_code: int = 0) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "venvwin.cli", *args],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == exit_code, (
        f"command {args}: exit={result.returncode} expected={exit_code}\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    return result.stdout


def test_install_persists_and_reloads_across_cli_processes(environment):
    base, env = environment
    app = base / "installers" / "Setup.exe"
    app.parent.mkdir()
    app.write_bytes(b"MZ fake test data")
    run_cli(env, "init")

    result = json.loads(run_cli(env, "open", str(app)))
    assert result["action"] == "install"
    assert result["dry_run"] is False
    assert result["exit_code"] == 0
    assert Path(result["stored_path"]).read_bytes() == app.read_bytes()
    assert "setup" in run_cli(env, "list")

    metadata = json.loads(run_cli(env, "inspect", "setup"))
    assert metadata["installers"][-1]["exit_code"] == 0
    runner_marker = Path(metadata["prefix_path"]) / "smoke-runner.json"
    assert json.loads(runner_marker.read_text())["args"] == [str(app)]
    assert json.loads(runner_marker.read_text())["arch"] == "win64"

    snapshot = json.loads(run_cli(env, "snapshot", "create", "setup", "--label", "smoke"))
    assert snapshot
    run_cli(env, "reset", "setup")
    assert not runner_marker.exists()


def test_msi_and_portable_exe_execute_with_isolated_prefixes(environment):
    base, env = environment
    run_cli(env, "init")
    msi = base / "Package.msi"
    portable = base / "LegacyTool.exe"
    msi.write_bytes(b"fake MSI")
    portable.write_bytes(b"MZ fake EXE")
    install = json.loads(run_cli(env, "open", str(msi)))
    launch = json.loads(run_cli(env, "open", str(portable)))
    assert install["exit_code"] == launch["exit_code"] == 0
    assert install["command"][-3:] == ["msiexec", "/i", str(msi)]
    assert launch["command"][-1] == str(portable)
    assert install["env"]["WINEPREFIX"] != launch["env"]["WINEPREFIX"]
    assert Path(install["env"]["WINEPREFIX"], "smoke-runner.json").exists()
    assert Path(launch["env"]["WINEPREFIX"], "smoke-runner.json").exists()


def test_runner_failure_propagates_to_cli(environment):
    base, env = environment
    run_cli(env, "init")
    failing = base / "Setup.exe"
    failing.write_bytes(b"MZ")
    wine = base / "bin" / "wine"
    wine.write_text(wine.read_text().replace(
        "'--fail-test' in sys.argv", "True"
    ), encoding="utf-8")
    output = run_cli(env, "open", str(failing), exit_code=19)
    assert json.loads(output)["exit_code"] == 19
    recorded = json.loads(run_cli(env, "inspect", "setup"))
    assert recorded["installers"][-1]["exit_code"] == 19


def test_file_association_generation(environment):
    base, env = environment
    apps_dir = base / "applications"
    run_cli(env, "associate", "--applications-dir", str(apps_dir))
    exe = (apps_dir / "venvwin-open-exe.desktop").read_text()
    msi = (apps_dir / "venvwin-open-msi.desktop").read_text()
    assert "Exec=venvwin open %f" in exe
    assert "Exec=venvwin open %f" in msi
