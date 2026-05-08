# WinUx Portable Product Gate

This document defines what counts as "real" for WinUx Portable Alpha.

WinUx is the Linux-based OS wrapper and product shell. venvWin is the compatibility engine that manages isolated Windows-like app capsules. Wine can be backend number one, but Wine is not the product. The product is the repeatable app environment, launcher flow, storage policy, dashboard, and recovery model wrapped into a bootable Linux system.

## Alpha must pass these gates

### 1. Bootable image gate

WinUx Portable Alpha must produce a bootable ISO or hybrid image from the repository build scripts.

Passing means:

- the ISO build script completes without manual patching
- the generated image has a checksum and manifest
- the selected profile is recorded in the manifest
- the image boots to a usable desktop session
- the desktop has visible WinUx / venvWin entry points

### 2. First boot gate

First boot must initialize the user-facing WinUx environment.

Passing means:

- capsule storage is selected or created
- `VENVWIN_HOME` can resolve to a writable capsule store
- first-run summary files are written
- the user can see where Windows app state will live
- the first-run flow does not silently write into unsafe host paths without warning

### 3. Leave-no-trace gate

WinUx Portable must treat storage location as a product feature, not an accident.

Passing means:

- portable-owned storage is preferred when available
- host write risk is detected and reported
- disposable-session risk is detected and reported
- the dashboard and CLI agree on the selected storage
- resetting a capsule does not imply deleting user documents or mapped host files

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

The WinUx dashboard must expose product state in a human-usable way.

Passing means:

- dashboard launches locally
- dashboard shows capsule count
- dashboard shows storage destination
- dashboard shows leave-no-trace status
- dashboard shows host write risk
- dashboard exposes status JSON
- dashboard exposes doctor JSON
- LAN binding must require a token or equivalent access control

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

## Current alpha definition

WinUx Portable Alpha is real when a user can boot the image, see WinUx controls, initialize storage, double-click or route a Windows installer into a capsule, inspect the capsule, and understand where the app state lives.

It does not need to beat Windows compatibility yet.

It does need to make compatibility boring, inspectable, recoverable, and less stupid than prefix spelunking.

## Next hard milestone

The next hard milestone is a boot-tested Alpha ISO with screenshots or logs proving:

- first boot desktop loads
- first-run setup completes
- dashboard opens
- doctor output is visible
- capsule storage is writable
- EXE/MSI handlers are installed
- one dummy installer dry-run is routed into a capsule

Until that evidence exists, the project is pre-alpha with a strong skeleton. Once that evidence exists, it becomes WinUx Portable Alpha.
