# venvWin Portable Flash-Ready Checklist

## Purpose

This checklist defines when venvWin Portable is ready to flash onto a USB drive.

No ISO is considered flash-ready until it passes the readiness gate.

Internal codename:

```text
WinUx
```

## Required artifacts

Flash-ready means these files exist:

```text
venvwin-portable-alpha-standard.iso
venvwin-portable-alpha-standard.iso.sha256
venvwin-portable-alpha-standard-manifest.txt
venvwin-flash-ready-verdict.txt
```

## Required pre-ISO pass

Before building the ISO, this must pass:

```bash
./winux-portable/pre-iso-readiness.sh
```

Required output:

```text
PRE-ISO READINESS: PASS
```

## Required ISO build pass

The Standard profile must build successfully:

```bash
WINUX_PROFILE=standard ./winux-portable/build-iso.sh
```

Required manifest flags:

```text
profile=standard
public_product_name=venvWin Portable
internal_codename=WinUx
leave_no_trace_default=true
first_boot_gui=true
dashboard=true
dashboard_url=http://127.0.0.1:8787
first_boot_desktop_launchers=true
```

## Required static inspection

The ISO must contain:

- bootloader data
- kernel
- initrd
- filesystem.squashfs
- venvWin source under `/opt/venvwin`
- `winux-first-boot-gui`
- `winux-first-run`
- `winux-dashboard`
- `winux-dashboard-lan`
- desktop launcher entries
- `/etc/skel/Desktop/venvWin-First-Boot.desktop`
- `/etc/skel/Desktop/venvWin-Dashboard.desktop`
- `/etc/skel/Desktop/venvWin-Capsules.desktop`
- `/etc/skel/Desktop/venvWin-Doctor.desktop`
- `/etc/skel/Desktop/venvWin-Private-Browser.desktop`

## Required smoke pass

QEMU smoke must either:

- stay alive through the timeout, or
- produce useful logs that show boot reached live system initialization

## First boot requirements

On real hardware, first boot must show:

- venvWin Portable desktop
- first-boot GUI opens automatically
- visible desktop shortcuts are present
- Start panel is visible
- Control Panel section is visible
- System Status section is visible
- dashboard URL is visible
- dashboard opens at `http://127.0.0.1:8787`
- storage destination visible
- leave-no-trace status visible
- host-risk status visible
- capsule path visible
- Initialize Storage button works
- Open Dashboard button works
- Open Capsules button works
- Run Doctor button works
- Private Browser button works when installed in the selected profile
- Quick Start file exists on desktop

Required visible desktop shortcuts:

```text
venvWin-First-Boot.desktop
venvWin-Dashboard.desktop
venvWin-Capsules.desktop
venvWin-Doctor.desktop
venvWin-Private-Browser.desktop
```

## USB persistence requirement

Before product release, persistent mode must prove:

```text
create capsule
reboot
capsule still exists
```

If capsule state does not survive reboot, the ISO may be a demo build but not a product build.

## Flash-ready verdicts

```text
NOT READY
PRE-ISO PASS
ISO BUILT
STATIC PASS
SMOKE PASS
FLASH READY
PRODUCT READY
```

## Rule

Do not flash for product testing until the verdict reaches at least:

```text
FLASH READY
```

Do not sell until the verdict reaches:

```text
PRODUCT READY
```
