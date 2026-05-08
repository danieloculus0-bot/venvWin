# Local venvWin Portable Flash-Ready Build

## Purpose

This is the local Linux/WSL equivalent of the phone-runnable GitHub Actions workflow.

Use this path when GitHub Actions is disabled, invisible, or being a flaky little goblin.

It runs the same gate:

```text
pre-ISO readiness
standard ISO build
checksum
manifest checks
static ISO inspection
QEMU smoke
flash-ready verdict
```

## Fast path

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

Build command from repo root:

```bash
chmod +x winux-portable/audit-public-branding.sh winux-portable/pre-iso-readiness.sh winux-portable/build-iso.sh winux-portable/build-flash-ready-standard.sh
./winux-portable/build-flash-ready-standard.sh
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
