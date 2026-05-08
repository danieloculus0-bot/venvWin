# WinUx Portable First Run Flow

## First boot user experience

The first boot should be simple:

```text
Welcome to WinUx Portable
Your venvWin capsule storage is: <path>
EXE/MSI double-click support is: enabled/disabled
Persistence is: enabled/disposable
Open a Windows installer to begin
```

## Required checks

On first boot, WinUx Portable should check:

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
write first-run status file
show quick-start screen
```

## Desktop shortcuts

The desktop should include:

- venvWin Capsule Manager
- Quick Start
- Capsule Storage Folder

## Warning states

### Disposable mode

If no persistence is available:

```text
Warning: this session is disposable. Installed apps and capsule state may be lost after reboot.
```

### Missing runner

If the runner is missing:

```text
Warning: no Windows app runner was found. venvWin can create capsules, but cannot launch Windows apps until a runner is installed.
```

## Design rule

Do not overwhelm the user with compatibility guts. Show status, next action, and where state is saved.
