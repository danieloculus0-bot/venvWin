# venvWin

venvWin is the Windows-app compatibility capsule engine for venvWin Portable.

venvWin Portable is the lightweight Linux-based portable OS shell. It is meant to extend the usable life of older PCs by giving them a familiar desktop, portable storage behavior, and managed compatibility paths for old Windows apps, obsolete tech, and legacy workflows.

Internal codename:

```text
WinUx
```

venvWin is the subsystem that manages isolated Windows-like app environments on Linux. It owns capsules, runner profiles, install routing, launch routing, snapshots, recovery, and compatibility backend selection.

The goal is not to rebuild Windows from scratch. The goal is to make older hardware useful again with a small, familiar Linux system where compatibility is boring, repeatable, isolated, recoverable, and easy enough that a normal user can install an app without spelunking through prefix hell.

Wine is allowed as backend number one. Wine is not the product. The product is the repeatable capsule environment and venvWin Portable shell wrapped around it.

## Product intent

venvWin Portable should feel more like a practical 2011-era lightweight Linux appliance than a bloated modern desktop distro.

Target direction:

- bootable portable OS
- Windows-familiar shell and launcher flow without impersonating Windows
- visible desktop shortcuts on first boot
- useful on older 2010-ish PCs where practical
- compatibility layer for obsolete tech and legacy apps
- low background overhead
- local dashboard, not cloud dependency
- no host hard-drive usage by default
- venvWin-owned state, logs, and capsules
- Windows app routing through venvWin capsules

Leave No Trace means no unwanted host hard-drive writes. It does not mean stealth, hidden use, or hacker bullshit. venvWin Portable should keep visible proof and logs inside its own session/storage while avoiding host desktop/browser residue.

## Current status

Pre-alpha skeleton with real plumbing:

- Python CLI package
- per-app capsule metadata
- runner profiles
- Wine backend command preparation
- installer recording
- EXE/MSI file classification
- desktop handler generation
- visible first-boot desktop launchers
- launcher generation
- capsule snapshots and reset backups
- first-run storage flow
- LNT storage reporting
- local venvWin Portable dashboard
- ISO build script for venvWin Portable profiles
- CI smoke gates and pre-ISO readiness checks

This is not native Windows compatibility yet. It is the product structure needed to make compatibility inspectable, recoverable, and less stupid than prefix chaos.

## Product split

```text
venvWin Portable
  Lightweight bootable Linux OS shell
  Windows-familiar desktop flow
  First-boot setup
  Visible desktop shortcuts
  Local dashboard
  App launcher UX
  System settings direction
  Storage policy
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

venvWin Portable Alpha is real when a user can boot the image, see venvWin controls, initialize storage, double-click or route a Windows installer into a capsule, inspect the capsule, and understand where the app state lives.

Until that boot-tested evidence exists, this project is pre-alpha with a strong skeleton.

## First milestone

Build and prove a boot-tested venvWin Portable Alpha ISO:

- ISO boots to a usable lightweight desktop
- first-run setup completes
- first-boot GUI opens automatically
- visible desktop shortcuts are present
- dashboard opens locally
- storage destination is visible
- host write risk is reported
- EXE/MSI handlers are installed
- one dummy installer dry-run routes into a capsule
- capsule create/list/inspect/install dry-run works
- doctor/status output is visible
- first-boot proof bundle appears in the venvWin Portable session

Required first-boot desktop shortcuts:

```text
venvWin-First-Boot.desktop
venvWin-Dashboard.desktop
venvWin-Capsules.desktop
venvWin-Doctor.desktop
venvWin-Private-Browser.desktop
```

## Build gates

Two GitHub Actions workflows exist:

```text
preflight-lite
flash-ready-standard
```

If workflow runs do not appear after commits, check:

```text
Settings > Actions > General
```

Expected:

```text
Actions enabled
workflow_dispatch available
push workflows allowed
artifact upload allowed
```

Manual build trigger from phone:

```text
Actions > flash-ready-standard > Run workflow > main
```

Flash-ready artifact bundle:

```text
venvwin-portable-flash-ready-standard
```

Required files:

```text
venvwin-portable-alpha-standard.iso
venvwin-portable-alpha-standard.iso.sha256
venvwin-portable-alpha-standard-manifest.txt
venvwin-flash-ready-verdict.txt
```

Do not flash until the verdict file says:

```text
status=FLASH_READY
```

## Backend philosophy

venvWin must not collapse into "Wine with a hat."

The backend layer should support:

- Wine
- Proton-style runner profiles
- Bottles-style managed runners
- containerized runners
- VM fallback
- future compatibility shims

The CLI, dashboard, capsule model, and venvWin Portable shell should survive backend changes without being rewritten from scratch.
