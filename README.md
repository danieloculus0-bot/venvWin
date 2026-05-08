# venvWin

venvWin is the Windows app capsule engine for WinUx.

WinUx is the Linux-based OS wrapper and product shell. It owns the bootable image, desktop shell, first-boot flow, dashboard, launcher UX, storage policy, and user-facing app management.

venvWin is the subsystem that manages isolated Windows-like app environments on Linux. It owns capsules, runner profiles, install routing, launch routing, snapshots, recovery, and compatibility backend selection.

The goal is not to rebuild Windows from scratch. The goal is to make Windows app compatibility boring, repeatable, isolated, recoverable, and easy enough that a normal user can install an app without spelunking through prefix hell.

Wine is allowed as backend number one. Wine is not the product. The product is the repeatable capsule environment and WinUx shell wrapped around it.

## Current status

Pre-alpha skeleton with real plumbing:

- Python CLI package
- per-app capsule metadata
- runner profiles
- Wine backend command preparation
- installer recording
- EXE/MSI file classification
- desktop handler generation
- launcher generation
- capsule snapshots and reset backups
- first-run storage flow
- leave-no-trace storage reporting
- local WinUx dashboard
- ISO build script for WinUx Portable profiles
- CI smoke gates and pre-ISO readiness checks

This is not native Windows compatibility yet. It is the product structure needed to make compatibility inspectable, recoverable, and less stupid than prefix chaos.

## Product split

```text
WinUx
  Bootable Linux OS wrapper
  Desktop shell
  First-boot setup
  Local dashboard
  App launcher UX
  System settings
  Storage policy
  Update manager
  venvWin integration

venvWin
  Per-app capsules
  Runner profiles
  Isolated prefixes
  Installer capture
  Windows file routing
  Launcher generation
  Snapshots and rollback
  Backend abstraction
  VM fallback later
```

## Alpha product gate

The hard definition of "real" lives here:

`winux-portable/product-gate.md`

WinUx Portable Alpha is real when a user can boot the image, see WinUx controls, initialize storage, double-click or route a Windows installer into a capsule, inspect the capsule, and understand where the app state lives.

Until that boot-tested evidence exists, this project is pre-alpha with a strong skeleton.

## First milestone

Build and prove a boot-tested WinUx Portable Alpha ISO:

- ISO boots to a usable desktop
- first-run setup completes
- dashboard opens locally
- storage destination is visible
- host write risk is reported
- EXE/MSI handlers are installed
- one dummy installer dry-run routes into a capsule
- capsule create/list/inspect/install dry-run works
- doctor/status output is visible

## Backend philosophy

venvWin must not collapse into "Wine with a hat."

The backend layer should support:

- Wine
- Proton-style runner profiles
- Bottles-style managed runners
- containerized runners
- VM fallback
- future compatibility shims

The CLI, dashboard, capsule model, and WinUx shell should survive backend changes without being rewritten from scratch.
