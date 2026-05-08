# venvWin Portable Build Attempt Checklist

## Purpose

This is the shortest safe path from repository checkout to flash-ready ISO attempt.

Public product name:

```text
venvWin Portable
```

Internal codename:

```text
WinUx
```

## Current rule

Do not flash anything until the verdict says:

```text
status=FLASH_READY
```

## Windows PowerShell path

From the repository root on Windows with WSL Ubuntu installed:

```powershell
.\winux-portable\run-wsl-flash-ready.ps1
```

Optional explicit path:

```powershell
.\winux-portable\run-wsl-flash-ready.ps1 -RepoPath "C:\Users\Daniel\venvWin"
```

## Ubuntu/WSL path

From the repository root inside Ubuntu/WSL:

```bash
chmod +x winux-portable/bootstrap-flash-ready-ubuntu.sh
./winux-portable/bootstrap-flash-ready-ubuntu.sh
```

## What the build attempts

```text
install required Ubuntu packages
install Python package and tests
run public branding audit
run pre-ISO readiness gate
run test suite
build Standard ISO
create checksum
create manifest
extract filesystem.squashfs
inspect live filesystem contents
run QEMU boot smoke
write flash-ready verdict
```

## Required pass markers

```text
PUBLIC BRANDING AUDIT: PASS
PRE-ISO READINESS: PASS
squashfs_static_inspection=pass
qemu_smoke=pass
status=FLASH_READY
FLASH READY: dist/venvwin-portable-alpha-standard.iso
```

## Required output files

```text
dist/venvwin-portable-alpha-standard.iso
dist/venvwin-portable-alpha-standard.iso.sha256
dist/venvwin-portable-alpha-standard-manifest.txt
dist/venvwin-flash-ready-verdict.txt
```

## If the build fails

Capture:

```text
last visible error block
which step failed
contents of dist/venvwin-flash-ready-verdict.txt if it exists
```

Do not start random fixes before identifying the failing step. The whole point of the gate stack is to tell us which bastard broke.

## After FLASH_READY

Use:

```text
winux-portable/usb-flash-guide.md
```

First hardware boot must show:

```text
venvWin-First-Boot.desktop
venvWin-Dashboard.desktop
venvWin-Capsules.desktop
venvWin-Doctor.desktop
venvWin-Private-Browser.desktop
```

And the GUI must show:

```text
Start panel
Control Panel section
System Status section
Dashboard URL
Capsule storage path
Leave-no-trace status
Host write risk
```

## Product release warning

FLASH_READY means safe to try on USB.

It does not mean sellable.

Sellable requires persistence proof:

```text
create capsule
reboot
capsule still exists
```
