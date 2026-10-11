# venvWin Portable Live Boot

## Goal

venvWin Portable should support a bootable USB mode that can optionally load the OS into RAM while keeping venvWin capsules persistent.

```text
Boot from USB
Load OS into RAM when hardware allows
Keep venvWin capsules persistent on USB or chosen storage
Double-click EXE/MSI and route into venvWin
```

This is a venvWin OS-wrapper feature. venvWin only needs to respect runtime paths and capsule storage locations.

## Product promise

```text
Plug in USB.
Boot venvWin Portable.
Open Windows apps through venvWin capsules.
Keep app state.
Leave the host machine mostly untouched.
```

## Boot modes

### Live USB

The OS boots from USB and runs as a live Linux session.

Good for:

- demos
- rescue use
- testing
- installs

### Persistent USB

The OS boots from USB and stores user/session changes in a persistence partition.

Good for:

- carrying a portable workstation
- saving venvWin capsules
- saving settings
- field work

### RAM mode

The core OS image loads into RAM when enough memory exists.

Good for:

- faster runtime
- lower USB dependency after boot
- old hardware rescue use
- rugged portable use

Rule: RAM mode accelerates the OS. It should not make app state fragile.

## Storage model

```text
USB drive
  EFI/boot partition
  compressed venvWin live image
  persistence partition
  venvWin capsule store

RAM
  loaded OS image
  temporary session cache

Persistent capsule store
  fake C drives
  registry/config state
  installers
  launchers
  snapshots
  logs
```

## venvWin runtime path

venvWin must support:

- `VENVWIN_HOME`
- user-local default path
- portable USB capsule path
- later venvWin-managed storage discovery

## Puppy-adjacent architecture (actual product target)

```text
Modern x86_64 kernel + initial RAM filesystem
Small compressed read-only base (SquashFS)
Puppy-like RAM working layer through OverlayFS
Tiny but useful desktop and everyday tools
USB-first normal boot, no forced persistence
Optional RAM copy only when measured memory allows
Optional explicit save layer + independent application SFS packs
venvWin EXE/MSI capsules and durable app state (if chosen)
```

The current Debian Bookworm live-build and XFCE session are **temporary
bootstrapping tooling**, not the product definition. The repo does not yet
implement custom initramfs layer assembly, actual SFS modules, verified
copy-to-RAM, or persistence across a real reboot. Do not call the ISO
flash-ready until BEAN's guest and persistence evidence passes.

## Jetson-friendly target

venvWin Portable should avoid:

- heavy desktop effects
- Electron-first control panels
- unnecessary compositing
- background indexer bloat
- VM dependency as the normal path

## Hard rule

venvWin Portable is allowed to be clever. It is not allowed to become fragile wizard bullshit.
