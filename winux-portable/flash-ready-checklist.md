# WinUx Portable Flash-Ready Checklist

## Purpose

This checklist defines when WinUx Portable is ready to flash onto a USB drive.

No ISO is considered flash-ready until it passes the readiness gate.

## Required artifacts

Flash-ready means these files exist:

```text
winux-portable-alpha-standard.iso
winux-portable-alpha-standard.iso.sha256
winux-portable-alpha-standard-manifest.txt
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
leave_no_trace_default=true
first_boot_gui=true
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
- desktop launcher entries

## Required smoke pass

QEMU smoke must either:

- stay alive through the timeout, or
- produce useful logs that show boot reached live system initialization

## First boot requirements

On real hardware, first boot must show:

- WinUx desktop
- first-boot GUI opens automatically
- storage destination visible
- leave-no-trace status visible
- host-risk status visible
- capsule path visible
- Initialize button works
- Open Capsules button works
- Run Doctor button works
- Quick Start file exists on desktop

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
