# WinUx Portable Live Boot

## Goal

WinUx Portable should support a bootable USB mode that can optionally load the OS into RAM while keeping venvWin capsules persistent.

```text
Boot from USB
Load OS into RAM when hardware allows
Keep venvWin capsules persistent on USB or chosen storage
Double-click EXE/MSI and route into venvWin
```

This is a WinUx OS-wrapper feature. venvWin only needs to respect runtime paths and capsule storage locations.

## Product promise

```text
Plug in USB.
Boot WinUx Portable.
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
  compressed WinUx live image
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
- later WinUx-managed storage discovery

## First practical target

```text
Debian or Ubuntu-family live image
XFCE or similarly lightweight desktop
dark premium WinUx theme
venvWin preinstalled
EXE/MSI file association enabled
persistent capsule partition
optional RAM boot flag
```

## Jetson-friendly target

WinUx Portable should avoid:

- heavy desktop effects
- Electron-first control panels
- unnecessary compositing
- background indexer bloat
- VM dependency as the normal path

## Hard rule

WinUx Portable is allowed to be clever. It is not allowed to become fragile wizard bullshit.
