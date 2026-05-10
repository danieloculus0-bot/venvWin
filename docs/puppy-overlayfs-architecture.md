# venvWin Puppy-style OverlayFS architecture

venvWin Portable uses Lucid Puppy as a design reference for portability, not as a codebase to copy.

The current alpha remains a Debian live-build image with venvWin bundled. This document defines the target boot/session architecture that should replace the simple live image over time.

## Core idea

Puppy feels fast because the visible filesystem is assembled from layers.

For venvWin, the modern model is OverlayFS:

```text
visible /
= session_rw      highest priority, writable tmpfs session layer
+ save_rw         USB persistence layer or encrypted save image
+ system_ro       pristine compressed base system image
+ drivers_ro      optional driver and firmware module image
+ apps_ro         optional app/module SFS layers
+ dev_ro          optional developer SDK module
```

The base system stays pristine. Runtime changes land in a writable session layer. Persistence is explicit and can be skipped, encrypted, or manually saved.

## Layer map

Planned runtime mount points:

```text
/initrd/venvwin/session_rw
/initrd/venvwin/save_rw
/initrd/venvwin/system_ro
/initrd/venvwin/drivers_ro
/initrd/venvwin/apps_ro
/initrd/venvwin/dev_ro
```

Layer roles:

- `session_rw`: tmpfs session layer for speed and flash-life preservation.
- `save_rw`: persistent USB save partition or image file.
- `system_ro`: read-only `venvwin-system.sfs` base OS.
- `drivers_ro`: read-only `venvwin-drivers.sfs` firmware/kernel module payload.
- `apps_ro`: optional read-only app capsules/modules.
- `dev_ro`: optional `venvwin-dev.sfs` SDK/build-tool module.

## Boot modes

Target boot menu modes:

- `normal`: live USB with persistence if configured.
- `ram`: copy base image to RAM when enough memory exists.
- `nosave`: ignore persistence and run disposable.
- `repair`: shell/diagnostic boot for fixing storage, boot, or capsule issues.
- `developer`: normal boot plus optional dev module.

Kernel parameter examples:

```text
venvwin.mode=normal
venvwin.mode=ram
venvwin.mode=nosave
venvwin.mode=repair
venvwin.mode=developer
venvwin.save=plain
venvwin.save=encrypted
venvwin.save=none
venvwin.ram
venvwin.nocopy
```

Puppy compatibility-style flags may be interpreted where harmless:

```text
pfix=copy
pfix=nocopy
pfix=ram
```

## USB-first rules

Do not hard-code `/dev/sdX`.

Device resolution priority should be:

1. UUID
2. PARTUUID
3. filesystem label
4. known relative path from boot media
5. last-resort scan with explicit warning

Target save markers:

```text
filesystem label: VENVWIN_SAVE
directory marker: .venvwin-save
image filename: venvwin-save.img
state file: /etc/venvwin/BOOTSTATE
```

## BOOTSTATE

Runtime boot/session state should be visible in:

```text
/etc/venvwin/BOOTSTATE
```

Minimum fields:

```text
product=venvWin Portable
architecture=puppy-style-overlayfs
boot_mode=normal|ram|nosave|repair|developer
save_mode=plain|encrypted|none|developer|unknown
session_layer=tmpfs
copy_to_ram=true|false
usb_first=true
system_sfs=venvwin-system.sfs
drivers_sfs=venvwin-drivers.sfs
dev_sfs=venvwin-dev.sfs
save_target=venvwin-save partition or save image
```

## Persistence model

First boot should offer:

- no persistence
- plain persistence
- encrypted persistence
- developer persistence

Writes should first hit `session_rw`. For flash-drive life, persistence should be explicit:

- save now
- periodic save
- save at shutdown
- never save this session

## Developer module

Developer tools should not live in the normal user image.

Target module:

```text
venvwin-dev.sfs
```

It should contain compilers, headers, packaging tools, and build dependencies. Load only in developer mode or by explicit user action.

## Current alpha mapping

Current alpha is not a full custom initramfs yet.

It maps as:

```text
Debian live system = temporary system_ro approximation
live persistence = temporary save_rw approximation
venvWin capsules = app/user state under selected capsule store
```

The first implementation step is not to replace init. It is to expose the target model through BOOTSTATE, docs, manifest fields, and CLI inspection. Then the initramfs/OverlayFS work can happen without guessing.
