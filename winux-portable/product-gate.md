# venvWin Portable Product Gate

This document defines what counts as real for venvWin Portable Alpha.

Public product name:

```text
venvWin Portable
```

Internal codename:

```text
WinUx
```

venvWin Portable is a lightweight Linux-based portable OS shell for managed Windows-app compatibility capsules. Its purpose is to extend the usable life of older PCs, especially 2010-era hardware that is too annoying or unsupported for modern Windows, while adding repeatable compatibility paths for old Windows apps, obsolete tech, and legacy workflows.

venvWin is the compatibility engine that manages isolated Windows-like app capsules. Wine can be backend number one, but Wine is not the product. The product is the lightweight portable OS, familiar shell, repeatable app environment, launcher flow, storage policy, dashboard, and recovery model wrapped into a bootable Linux system.

Leave No Trace means no host hard-drive usage by default. It does not mean stealth. Logs, proof files, and capsule metadata should remain visible inside the venvWin Portable session or venvWin-owned storage.

## Alpha must pass these gates

### 1. Bootable image gate

venvWin Portable Alpha must produce a bootable ISO or hybrid image from the repository build scripts.

Passing means:

- the ISO build script completes without manual patching
- the generated image has a checksum and manifest
- the selected profile is recorded in the manifest
- the public product name is recorded as venvWin Portable
- the internal codename is recorded as WinUx
- the image boots to a usable lightweight desktop session
- the desktop has visible venvWin Portable / venvWin entry points
- the image is not bloated beyond alpha reason without a recorded size warning

### 2. First boot gate

First boot must initialize the user-facing venvWin Portable environment.

Passing means:

- capsule storage is selected or created
- `VENVWIN_HOME` can resolve to a writable capsule store
- first-run summary files are written
- the user can see where Windows app state will live
- the first-run flow does not silently write into unsafe host paths without warning
- the desktop contains a first-boot proof bundle

Expected first-boot proof bundle:

- `venvWin-Quick-Start.txt`
- `venvWin-First-Boot-Proof.txt`
- `venvWin-Dashboard.txt`
- `venvWin-First-Boot-Checklist.txt`
- `venvwin-init.txt`
- `venvwin-associate.txt`
- `venvwin-first-run.txt`
- `venvwin-storage.txt`
- `venvwin-doctor.txt`

### 3. Leave-no-trace storage gate

venvWin Portable must treat host hard-drive avoidance as a product feature, not an accident.

Passing means:

- portable-owned storage is preferred when available
- host write risk is detected and reported
- disposable-session risk is detected and reported
- the dashboard and CLI agree on the selected storage
- resetting a capsule does not imply deleting user documents or mapped host files
- host internal disks are not selected automatically for capsules
- host desktop/browser residue is not created by default

### 4. Capsule engine gate

venvWin must manage app capsules as real persistent objects.

Passing means the CLI can:

- initialize runtime directories
- create a capsule
- list capsules
- inspect capsule metadata
- store runner profiles
- preserve filesystem mapping policy
- preserve permission policy
- record installers
- record launch targets
- create snapshots
- reset a capsule prefix while preserving a backup

### 5. Windows file handling gate

Double-click style handling must be represented, even if the desktop association still needs platform tuning.

Passing means:

- EXE files are classified
- MSI/MSIX files are classified as installers
- installer-looking EXE files are classified as installers
- portable EXE files are classified as launchable apps
- EXE/MSI desktop handlers can be generated
- dry-run open/install paths print the intended command and environment

### 6. Runner backend gate

Wine is allowed as the first backend, but the architecture must not collapse into "just Wine with a hat."

Passing means:

- runner command preparation is abstracted behind a backend interface
- capsule metadata stores the runner profile
- launch and install commands come from the selected runner
- new runner backends can be added without rewriting the CLI, dashboard, or capsule model
- backend limitations are reported honestly by doctor/status output

Backend candidates may include:

- Wine
- Proton-style runner profiles
- Bottles-style managed runners
- containerized runners
- VM fallback
- future compatibility shims

### 7. Dashboard gate

The venvWin Portable dashboard must expose product state in a human-usable way.

Passing means:

- dashboard launches locally
- dashboard binds to `127.0.0.1` by default
- dashboard shows capsule count
- dashboard shows storage destination
- dashboard shows LNT storage status
- dashboard shows host write risk
- dashboard exposes status JSON
- dashboard exposes doctor JSON
- LAN binding must require a token or equivalent access control
- dashboard uses familiar desktop-control patterns without impersonating Windows

### 8. CI gate

The repository must fail loudly when the basic product shape breaks.

Passing means CI runs:

- package install
- Python import checks
- CLI smoke commands
- first-run checks
- storage checks
- doctor checks
- association generation
- capsule create/list/inspect
- install dry-run
- open dry-run
- launcher generation
- snapshot creation
- reset operation
- pre-ISO readiness script

### 9. Honesty gate

The repo must clearly separate what works from what is aspirational.

Passing means:

- README says venvWin is currently plumbing
- docs do not claim native Windows compatibility until it exists
- Wine is described as a backend, not a magic replacement
- ISO scripts are labeled alpha until boot-tested
- dashboards, launchers, and first-boot flows are described as product shell pieces
- future roadmap items are not presented as finished features
- obsolete-tech compatibility is described as a direction, not a completed universal guarantee
- WinUx is treated as internal codename only

## Current alpha definition

venvWin Portable Alpha is real when a user can boot the image, see venvWin controls, initialize storage, double-click or route a Windows installer into a capsule, inspect the capsule, and understand where the app state lives.

It does not need to beat Windows compatibility yet.

It does need to make old hardware useful, compatibility boring, storage inspectable, recovery understandable, and host hard-drive usage avoidable by default.

## Next hard milestone

The next hard milestone is a boot-tested Alpha ISO with screenshots or logs proving:

- first boot desktop loads
- first-run setup completes
- dashboard opens at `http://127.0.0.1:8787`
- doctor output is visible in `venvwin-doctor.txt`
- capsule storage is writable
- EXE/MSI handlers are installed or attempted with visible output
- one dummy installer dry-run is routed into a capsule
- `venvWin-First-Boot-Proof.txt` exists on the desktop
- `venvWin-First-Boot-Checklist.txt` exists on the desktop

Until that evidence exists, the project is pre-alpha with a strong skeleton. Once that evidence exists, it becomes venvWin Portable Alpha.
