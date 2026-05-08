# venvWin

venvWin is the Windows app capsule engine for WinUx.

WinUx is the lightweight Linux-based OS wrapper and Windows-like product shell. It is meant to extend the usable life of older PCs by giving them a familiar desktop, portable storage behavior, and managed compatibility paths for old Windows apps, obsolete tech, and legacy workflows.

venvWin is the subsystem that manages isolated Windows-like app environments on Linux. It owns capsules, runner profiles, install routing, launch routing, snapshots, recovery, and compatibility backend selection.

The goal is not to rebuild Windows from scratch. The goal is to make older hardware useful again with a small, familiar Linux system where compatibility is boring, repeatable, isolated, recoverable, and easy enough that a normal user can install an app without spelunking through prefix hell.

Wine is allowed as backend number one. Wine is not the product. The product is the repeatable capsule environment and WinUx shell wrapped around it.

## Product intent

WinUx should feel more like a practical 2011-era lightweight Linux appliance than a bloated modern desktop distro.

Target direction:

- bootable portable OS
- Windows-like shell and launcher flow
- useful on older 2010-ish PCs where practical
- compatibility layer for obsolete tech and legacy apps
- low background overhead
- local dashboard, not cloud dependency
- no host hard-drive usage by default
- WinUx-owned state, logs, and capsules
- Windows app routing through venvWin capsules

Leave No Trace means no unwanted host hard-drive writes. It does not mean stealth, hidden use, or hacker bullshit. WinUx should keep visible proof and logs inside its own session/storage while avoiding host desktop/browser residue.

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
- LNT storage reporting
- local WinUx dashboard
- ISO build script for WinUx Portable profiles
- CI smoke gates and pre-ISO readiness checks

This is not native Windows compatibility yet. It is the product structure needed to make compatibility inspectable, recoverable, and less stupid than prefix chaos.

## Product split

```text
WinUx
  Lightweight bootable Linux OS wrapper
  Windows-like desktop shell
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
  Legacy app compatibility
  Obsolete tech compatibility layer
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

- ISO boots to a usable lightweight desktop
- first-run setup completes
- dashboard opens locally
- storage destination is visible
- host write risk is reported
- EXE/MSI handlers are installed
- one dummy installer dry-run routes into a capsule
- capsule create/list/inspect/install dry-run works
- doctor/status output is visible
- first-boot proof bundle appears in the WinUx session

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
