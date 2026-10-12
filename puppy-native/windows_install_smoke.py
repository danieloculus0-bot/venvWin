#!/usr/bin/env python3
"""Repeatable *real* Win64 NSIS and MSI installs, with BEAN memory gate.

This targets Ubuntu-hosted Wine only. Passing here NEVER proves Puppy guest Wine.
Reuses identical sourced results, stops blind identical-failure retries,
retains original logs and files; creates no ISO or Debian system image.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from bean_install_memory import Memory, SCHEMA, MARKER, fingerprint, file_hash

C_SOURCE = r'''#include <windows.h>
int main(void) {
 HANDLE h = CreateFileA("C:\\venvwin-simple-app-ran.txt", GENERIC_WRITE, 0,
  NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
 if (h == INVALID_HANDLE_VALUE) return 41;
 const char value[] = "REAL_WINDOWS_APPLICATION_LAUNCHED";
 DWORD n = 0;
 BOOL ok = WriteFile(h, value, sizeof(value)-1, &n, NULL);
 CloseHandle(h);
 return ok && n == sizeof(value)-1 ? 0 : 42;
}
'''
NSIS_SOURCE = r'''Unicode true
Name "venvWin Simple EXE Installer"
OutFile "Setup.exe"
InstallDir "$PROGRAMFILES64\VenvWinSmokeExe"
RequestExecutionLevel user
SilentInstall silent
Section "Install"
 SetOutPath "$INSTDIR"
 File "SmokeApp.exe"
SectionEnd
'''
WIX_SOURCE = r'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
 <Product Id="*" Name="venvWin Simple MSI Installer"
          Language="1033" Version="1.0.0" Manufacturer="venvWin"
          UpgradeCode="{E7CF7E80-F172-451D-8EA2-80F06425FE1D}">
  <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" Platform="x64"/>
  <Media Id="1" Cabinet="simple.cab" EmbedCab="yes"/>
  <Directory Id="TARGETDIR" Name="SourceDir">
   <Directory Id="ProgramFiles64Folder">
    <Directory Id="MSIINSTALLDIR" Name="VenvWinSmokeMsi">
     <Component Id="ApplicationComponent" Guid="{B0D0BABA-6146-4E89-9B95-557C6DA90FD6}" Win64="yes">
      <File Id="SmokeApplication" Name="SmokeApp.exe" Source="SmokeApp.exe" KeyPath="yes"/>
     </Component>
    </Directory>
   </Directory>
  </Directory>
  <Feature Id="MainFeature" Title="SimpleWindowsInstall" Level="1">
   <ComponentRef Id="ApplicationComponent"/>
  </Feature>
 </Product>
</Wix>
'''

def call(argv, cwd, timeout=180, check=True):
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=check)

def build(work):
    work.mkdir(parents=True, exist_ok=True)
    for name, content in (("SmokeApp.c", C_SOURCE), ("Setup.nsi", NSIS_SOURCE),
                          ("SimpleMsi.wxs", WIX_SOURCE)):
        (work / name).write_text(content)
    call(["x86_64-w64-mingw32-gcc", "-Os", "-s", "SmokeApp.c", "-o", "SmokeApp.exe"], work)
    call(["makensis", "-V2", "Setup.nsi"], work)
    call(["wixl", "--arch", "x64", "-o", "SimpleMsi.msi", "SimpleMsi.wxs"], work)
    for name in ("Setup.exe", "SimpleMsi.msi", "SmokeApp.exe"):
        if not (work / name).stat().st_size:
            raise RuntimeError("empty Windows installer fixture: " + name)
    print("WINDOWS_REAL_INSTALLER_BUILD_READY", flush=True)

def read_cli_json(path):
    raw = path.read_text()
    start = raw.find("{")
    if start < 0:
        raise RuntimeError("vWin CLI did not emit JSON: " + path.name)
    result, _ = json.JSONDecoder().raw_decode(raw[start:])
    return result

def write_receipt(out, case, identity, wine, installer):
    data = {
        "schema": SCHEMA, "scope": "ubuntu-wine", "case": case, "fingerprint": identity,
        "source_sha": os.environ["GITHUB_SHA"], "run_id": os.environ["GITHUB_RUN_ID"],
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "wine_version": wine, "installer_sha": file_hash(installer),
    }
    for field, file in (("install_sha", "install.json"), ("launch_sha", "launch.json"),
                        ("marker_sha", "marker.txt"), ("error_sha", "error.txt")):
        if (out / file).is_file():
            data[field] = file_hash(out / file)
    target = out / "receipt.json"
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return target

def install_real_case(work, out, case):
    installer = work / ("Setup.exe" if case == "nsis-exe" else "SimpleMsi.msi")
    capsule = "setup" if case == "nsis-exe" else "simplemsi"
    os.environ["VENVWIN_HOME"] = str((work / ("capsules-" + case)).resolve())
    call(["venvwin", "init"], work, timeout=30)
    installer_run = call(["venvwin", "open", str(installer)], work, timeout=240, check=False)
    (out / "install.json").write_text(installer_run.stdout)
    (out / "install-stderr.txt").write_text(installer_run.stderr[-6000:])
    details = read_cli_json(out / "install.json")
    if details.get("exit_code") != 0:
        return
    prefix = Path(details["env"]["WINEPREFIX"])
    installed = list((prefix / "drive_c").glob("Program Files*/VenvWinSmoke*/SmokeApp.exe"))
    if len(installed) != 1:
        raise RuntimeError("Wine reported successful install but installed program was not found")
    if file_hash(installed[0]) != file_hash(work / "SmokeApp.exe"):
        raise RuntimeError("installed binary not equal to verified original binary")
    marker = prefix / "drive_c" / "venvwin-simple-app-ran.txt"
    marker.unlink(missing_ok=True)
    launch = call(["venvwin", "run", capsule, str(installed[0])], work, timeout=120, check=False)
    (out / "launch.json").write_text(launch.stdout)
    (out / "launch-stderr.txt").write_text(launch.stderr[-6000:])
    read_cli_json(out / "launch.json")
    if marker.is_file():
        shutil.copy2(marker, out / "marker.txt")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="explicit retry of identical failure")
    args = parser.parse_args()
    repo = args.repo.resolve()
    work = args.work.resolve()
    evidence = args.evidence.resolve()
    build(work)
    wine = call(["wine", "--version"], work, timeout=20).stdout.strip()
    source_files = [repo / p for p in (
        "puppy-native/windows_install_smoke.py", "puppy-native/bean_install_memory.py",
        "src/venvwin/cli.py", "src/venvwin/runner.py", "src/venvwin/open.py",
        "src/venvwin/install.py", "src/venvwin/intake.py")]
    failed = False
    for case in ("nsis-exe", "wix-msi"):
        installer = work / ("Setup.exe" if case == "nsis-exe" else "SimpleMsi.msi")
        fp = fingerprint("ubuntu-wine", source_files + [installer, work / "SmokeApp.exe"],
                         wine + "|ubuntu-24.04|" + os.environ["BEAN_CORE_PIN"])
        with Memory(args.db) as mem:
            decision = mem.plan("ubuntu-wine", case, fp, args.force)
        print("BEAN_TEST_PLAN", case, json.dumps(decision, sort_keys=True), flush=True)
        if decision["decision"] == "reuse_scope_only":
            print("REUSED_VERIFIED_UBUNTU_WINE_RESULT", case, "run", decision["run_id"], flush=True)
            continue
        if decision["decision"] == "blocked_unchanged":
            print("NO_BLIND_RETRY_UNCHANGED_BLOCKER", case, decision["blocker"], flush=True)
            failed = True
            continue
        out = evidence / case
        out.mkdir(parents=True, exist_ok=True)
        try:
            install_real_case(work, out, case)
        except Exception as exc:
            (out / "error.txt").write_text(type(exc).__name__ + ": " + str(exc)[:250])
        receipt = write_receipt(out, case, fp, wine, installer)
        with Memory(args.db) as mem:
            result = mem.record(receipt)
        print("BEAN_TEST_RECORDED", case, json.dumps(result, sort_keys=True), flush=True)
        if result["state"] != "passed":
            failed = True
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
