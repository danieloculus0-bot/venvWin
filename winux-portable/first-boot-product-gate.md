# venvWin Portable First-Boot Product Gate

## Purpose

venvWin Portable must feel functional on first boot. Not theoretical. Not promising. Working.

The first boot experience is the product gate.

Internal codename:

```text
WinUx
```

## Required first boot sequence

```text
1. Live desktop reaches usable state
2. First-run setup initializes storage
3. First-boot GUI opens automatically
4. Start panel is visible
5. Capsule storage path is visible
6. Dashboard URL is visible
7. Leave-no-trace status is visible
8. Host write risk is visible
9. User can open dashboard
10. User can open capsule folder
11. User can run doctor
12. User can launch private browser path when installed in the selected profile
13. EXE/MSI association setup runs
14. Quick-start file exists on desktop
```

## Pass criteria

### Storage

Pass if:

- `~/.winux-capsule-store` exists
- selected path is visible in GUI
- `venvwin storage` reports leave-no-trace state
- host-risk warning appears when applicable
- the user can open the capsule folder from the GUI

Fail if:

- storage path is hidden
- host-risk is not visible
- user cannot tell where app state is going

## GUI

Pass if:

- `winux-first-boot-gui` launches
- GUI title says venvWin Portable
- Start panel is visible
- Control Panel section is visible
- System Status section is visible
- storage destination is shown
- dashboard URL is shown
- leave-no-trace badge is shown
- host write risk is shown
- Initialize Storage action is visible
- Open Dashboard action is visible
- Open Capsules action is visible
- Run Doctor action is visible
- Private Browser action is visible
- GUI feels familiar to Windows users without impersonating Windows

Fail if:

- GUI does not open
- GUI opens but storage status is missing
- GUI opens but dashboard path is missing
- user has to understand Linux paths before using the product

## Dashboard

Pass if:

- local dashboard starts automatically
- dashboard opens at `http://127.0.0.1:8787`
- GUI exposes an Open Dashboard action
- dashboard shows storage destination
- dashboard shows capsule count
- dashboard shows health checks
- dashboard shows leave-no-trace status
- LAN dashboard remains explicit and token-protected

Fail if:

- dashboard does not start
- dashboard binds to LAN by default
- dashboard does not show storage risk

## Doctor

Pass if:

- `venvwin doctor` runs
- first-run writes doctor output to desktop
- GUI exposes a Run Doctor action
- runner/privacy/storage/association status is clear

Fail if:

- doctor crashes
- output hides important setup failures

## EXE/MSI handling

Pass if:

- `venvwin associate` runs on first boot
- handler desktop files exist
- user can run `venvwin open app.exe --dry-run`

Beta pass requires file manager double-click confirmation.

## Leave-no-trace

Pass if:

- default capsule storage prefers venvWin-owned USB/install storage
- host writes are not selected silently
- host-risk is flagged visibly
- GUI says where app state goes
- dashboard and GUI agree on the storage destination

Fail if:

- venvWin Portable silently chooses a host/internal disk
- app state is written to host storage without explicit user choice

## Size

Pass if:

- ISO size is reported in manifest
- profile is named
- checksum is generated

Fail if:

- no manifest
- no checksum
- size is unknown

## First product gate verdicts

```text
FAIL
BOOT PASS
FIRST-BOOT PASS
BETA CANDIDATE
$8 CANDIDATE
```

## $8 candidate minimum

The first $8 candidate must satisfy:

- Standard profile ISO builds
- graphical desktop boots
- first-boot GUI opens automatically
- Start panel is visible
- dashboard opens locally
- storage selection is visible
- leave-no-trace policy is visible
- host-risk status is visible
- capsules survive reboot with USB persistence
- EXE/MSI handling works
- doctor works
- known limitations are documented

## Rule

First boot must show confidence.

If the user sees a blank desktop and has to guess what to do, the product gate fails.
