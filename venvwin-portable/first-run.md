# venvWin Portable First Run Flow

## First boot user experience

The first boot should be simple, useful, and mildly feral:

```text
Welcome to venvWin Portable
Capsule storage: <path>
EXE/MSI double-click support: enabled/disabled
Persistence: enabled/disposable
Open a Windows installer to begin. If it misbehaves, venvWin will keep the mess in its own little cave.
```

## Required checks

On first boot, venvWin Portable should check:

- venvWin is installed
- `venvwin init` has run
- EXE/MSI handlers exist
- `VENVWIN_HOME` points to persistent storage when available
- storage has enough free space
- Wine-compatible runner exists or missing-runner warning is shown

## First-run actions

```text
venvwin init
venvwin associate
venvwin doctor
write first-run status file
show quick-start screen
```

## Desktop shortcuts

The desktop should include:

- venvWin Capsule Manager
- Quick Start
- Capsule Storage Folder
- Run venvWin Doctor

## Warning states

### Disposable mode

If no persistence is available:

```text
Warning: disposable session detected. Anything you install may vanish after reboot. Fine for testing, terrible for keeping your work.
```

### Missing runner

If the runner is missing:

```text
Warning: no Windows app runner was found. venvWin can create capsules, but cannot launch Windows apps yet. Plumbing yes, engine no.
```

### Missing double-click handlers

```text
Warning: EXE/MSI double-click handlers are missing. Run `venvwin associate` so opening Windows files stops being bullshit.
```

## Design rule

Do not overwhelm the user with compatibility guts. Show status, next action, and where state is saved.

## Voice rule

First-run copy can have attitude, but every message still needs to say exactly what happened and what the user should do next.
