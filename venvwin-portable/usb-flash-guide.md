# venvWin Portable USB Flash Guide

## Status rule

Do not write the ISO to a USB drive until the verdict file says:

```text
status=FLASH_READY
```

Required verdict file:

```text
dist/venvwin-flash-ready-verdict.txt
```

Required ISO:

```text
dist/venvwin-portable-alpha-standard.iso
```
Required checksum:

```text
dist/venvwin-portable-alpha-standard.iso.sha256
```

## Before flashing

Confirm the checksum:

```bash
(cd dist && sha256sum -c venvwin-portable-alpha-standard.iso.sha256)
```

Expected:

```text
OK
```

Confirm verdict:

```bash
cat dist/venvwin-flash-ready-verdict.txt
```

Expected:

```text
status=FLASH_READY
```

## Windows option

Use Rufus or balenaEtcher.

Recommended first test:

```text
Rufus
DD/Image mode when prompted
Target: known spare USB drive only
```

Do not select a work drive, backup drive, or anything you care about. Flashing writes the whole device.

## Linux/WSL warning

Do not use WSL to write directly to USB unless the USB device is explicitly attached and verified. For early testing, use Windows Rufus/balenaEtcher or native Linux.

## Native Linux flash path

List removable drives:

```bash
lsblk -o NAME,SIZE,TYPE,RM,MOUNTPOINTS,MODEL
```

Unmount mounted partitions on the target USB:

```bash
sudo umount /dev/sdX* 2>/dev/null || true
```

Write ISO to the whole USB device:

```bash
sudo dd if=dist/venvwin-portable-alpha-standard.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

Replace:

```text
/dev/sdX
```

with the actual whole USB device, not a partition like `/dev/sdX1`.

## First boot expectation

On first boot, the desktop should show:

```text
venvWin-First-Boot.desktop
venvWin-Dashboard.desktop
venvWin-Capsules.desktop
venvWin-Doctor.desktop
venvWin-Private-Browser.desktop
```

The first-boot GUI should open automatically and show:

```text
Start panel
Control Panel section
System Status section
Dashboard URL
Capsule storage path
Leave-no-trace status
Host write risk
```

The local dashboard should be available at:

```text
http://127.0.0.1:8787
```

## Pass/fail on first hardware boot

Pass if:

- desktop loads
- visible desktop shortcuts are present
- first-boot GUI opens
- dashboard opens locally
- storage path is visible
- doctor output exists
- first-boot proof bundle exists

Fail if:

- desktop is blank
- first-boot GUI does not open
- dashboard does not start
- storage path is hidden
- host write risk is invisible
- capsule state cannot be located

## Product rule

A demo flash is not a product release.

Product release requires USB persistence proof:

```text
create capsule
reboot
capsule still exists
```
