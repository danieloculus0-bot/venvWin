# Local venvWin Portable Flash-Ready Build

## Purpose

This is the local Linux/WSL equivalent of the phone-runnable GitHub Actions workflow.

Use this path when GitHub Actions is disabled, invisible, or being a flaky little goblin.

It runs the same gate:

```text
pre-ISO readiness
public branding audit
Python tests
standard ISO build
checksum
manifest checks
squashfs static inspection
QEMU smoke
flash-ready verdict
```

## Windows PowerShell fast path

From repo root in PowerShell on Windows with WSL Ubuntu installed:

```powershell
.\winux-portable\run-wsl-flash-ready.ps1
```

Optional explicit repo path:

```powershell
.\winux-portable\run-wsl-flash-ready.ps1 -RepoPath "C:\Users\Daniel\venvWin"
```

The PowerShell runner converts the Windows path to `/mnt/c/...`, runs the Ubuntu bootstrap, reads the verdict, and refuses to call the build flash-ready unless the verdict says:

```text
status=FLASH_READY
```

## Ubuntu/WSL fast path

From repo root on Ubuntu/Debian/WSL:

```bash
chmod +x winux-portable/bootstrap-flash-ready-ubuntu.sh
./winux-portable/bootstrap-flash-ready-ubuntu.sh
```

That script installs the required system packages, installs the Python package/test tools, runs the flash-ready gate, and prints the verdict.

## Manual path

Use Linux or WSL with sudo access.

Ubuntu/Debian package setup:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv python3-full live-build rsync xorriso isolinux syslinux-common squashfs-tools qemu-system-x86 ovmf curl ca-certificates
```

Python setup from repo root:

```bash
python3 -m pip install --break-system-packages --upgrade pip || python3 -m pip install --upgrade pip
python3 -m pip install --break-system-packages -e . pytest || python3 -m pip install -e . pytest
```

Preflight only:

```bash
chmod +x winux-portable/audit-public-branding.sh winux-portable/pre-iso-readiness.sh
./winux-portable/pre-iso-readiness.sh
```

Required preflight output:

```text
PUBLIC BRANDING AUDIT: PASS
PRE-ISO READINESS: PASS
```

Build command from repo root:

```bash
chmod +x winux-portable/audit-public-branding.sh winux-portable/pre-iso-readiness.sh winux-portable/build-iso.sh winux-portable/build-flash-ready-standard.sh
./winux-portable/build-flash-ready-standard.sh
```

## Static inspection rule

The flash-ready gate must inspect the live filesystem inside:

```text
filesystem.squashfs
```

Required static inspection evidence:

```text
unsquashfs -ll
squashfs_static_inspection=pass
squashfs-root/etc/skel/Desktop/venvWin-First-Boot.desktop
```

## Success output

The script must print:

```text
FLASH READY: dist/venvwin-portable-alpha-standard.iso
```

The verdict file must say:

```text
status=FLASH_READY
```

## Output files

```text
dist/venvwin-portable-alpha-standard.iso
dist/venvwin-portable-alpha-standard.iso.sha256
dist/venvwin-portable-alpha-standard-manifest.txt
dist/venvwin-flash-ready-verdict.txt
```

## Flash rule

Only flash after:

```text
cat dist/venvwin-flash-ready-verdict.txt
```

shows:

```text
status=FLASH_READY
```

Anything else is not ready.
