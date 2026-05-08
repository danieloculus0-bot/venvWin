# WinUx Lightweight Old Hardware Target

WinUx Portable is intended to extend the usable life of older PCs, especially machines from around 2010 and newer that are too slow, unsupported, or annoying under modern Windows.

This is not a gaming distro. This is not a bloated workstation desktop. This is a practical Windows-like Linux appliance for legacy workflows and obsolete tech.

## Design target

WinUx should feel closer to a useful old Puppy Linux / lightweight rescue OS than a modern full desktop distro.

Target characteristics:

- boots from USB or optical media where possible
- runs acceptably on older dual-core machines
- prefers low RAM usage over visual polish
- avoids unnecessary resident services
- keeps the desktop simple and familiar
- avoids host hard-drive writes by default
- stores state in WinUx-owned portable storage
- provides compatibility paths for old Windows apps and obsolete tech

## Practical alpha hardware target

Alpha should aim for:

```text
CPU: 64-bit dual-core x86_64
RAM: 2 GB minimum, 4 GB comfortable
Storage: USB boot media plus optional WINUXDATA storage
GPU: basic integrated graphics
Network: optional, not required for local app use after image is built
```

Stretch target:

```text
RAM: usable at 1 GB for core profile
```

The standard profile may need more RAM because Wine and compatibility tooling are heavier.

## Profile intent

### core

Old-PC rescue profile.

Purpose:

- smallest practical desktop
- boot and inspect system
- local dashboard
- venvWin CLI plumbing
- no Wine by default
- suitable for very old or low-RAM hardware

### standard

Main compatibility profile.

Purpose:

- Windows-like shell
- venvWin capsules
- Wine backend installed
- EXE/MSI routing
- local dashboard
- first-boot proof bundle

### privacy

Heavier optional profile.

Purpose:

- standard profile plus privacy browser tooling
- not the default old-PC target
- allowed to be larger

## Desktop target

XFCE is acceptable for alpha because it is familiar, stable, available, and scriptable. It is not the final low-RAM ceiling.

Future candidates:

- LXDE
- LXQt
- JWM
- Openbox with tint2
- IceWM

A Puppy-ish final profile should consider JWM/Openbox/IceWM if XFCE proves too heavy.

## Services rule

Default alpha should avoid unnecessary services.

Allowed core services:

- init/systemd runtime
- display manager
- desktop session
- NetworkManager
- local dashboard
- first-run setup

Avoid by default:

- cloud sync
- search indexers
- telemetry
- heavyweight app stores
- automatic host-drive indexing
- silent update daemons that chew RAM

## Game policy

WinUx is not a game bundle.

Allowed:

- one tiny built-in easter egg game named `Daniel Boone: Bloat Stacker`
- Tkinter-only implementation using the Python standard library
- launcher entry in the WinUx menu

Not allowed:

- additional bundled games
- game package dependencies
- large art/audio assets
- anything that bloats the ISO or distracts from old-PC rescue and compatibility work

## LNT storage rule

Leave No Trace means no host hard-drive usage by default.

WinUx may log, but logs should go to WinUx-owned storage or the live session, not the host OS disk.

## Size target

Alpha size warnings:

```text
<= 1200 MB: excellent old-PC target
1201-2500 MB: acceptable alpha
2501-3500 MB: soft warning, too fat for product polish
> 3500 MB: hard concern
```

The current build scripts already flag these bands in profile comparison.

## First real proof

A build is not proven lightweight until QEMU or real hardware boot evidence shows:

- desktop reaches usable state
- dashboard opens locally
- first-run proof bundle appears
- capsule store resolves
- RAM usage is recorded after idle desktop
- ISO size is recorded
- profile is recorded in manifest
