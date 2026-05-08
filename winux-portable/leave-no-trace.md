# WinUx Portable Leave-No-Trace Policy

## Product rule

By default, WinUx Portable should write only to the WinUx USB/install drive.

The host machine should be treated as read-only unless the user explicitly chooses otherwise.

```text
Boot WinUx.
Use WinUx.
Store state on WinUx USB.
Leave the host alone.
```

Hippie rule:

```text
Leave no trace.
```

## Default writable target

Default writable state should go to:

```text
WINUXDATA/WinUx-Capsules
```

or another detected WinUx-owned persistent storage path.

## Host machine policy

Default behavior:

- do not write to host internal disks
- do not auto-mount host internal disks read-write
- do not create host files
- do not store capsules on host drives
- do not install launchers onto host OS
- do not modify host bootloader
- do not touch host user folders

Allowed only with explicit user action:

- mount host drive read-write
- copy files to/from host drive
- choose host folder as capsule storage
- install WinUx/venvWin onto host

## Capsule storage rule

venvWin capsules should live on the portable storage by default.

```text
preferred: /media/<user>/WINUXDATA/WinUx-Capsules
fallback: /run/live/persistence/WinUx-Capsules
last resort: ~/WinUx-Capsules with disposable warning
```

The fallback home path is allowed only for testing or true persistent live-home sessions.

## Disposable warning

If WinUx cannot find writable WinUx-owned storage:

```text
Warning: no WinUx-owned persistent storage found. This session may be disposable. Installed apps may vanish after reboot. That is fine for testing and bullshit for real work.
```

## Internal disk detection

Future first-run logic should identify likely host/internal drives and avoid selecting them automatically.

Risky targets:

- `/media/<user>/<host-drive-label>` unless label is `WINUXDATA` or user confirms
- `/mnt/*` unless mounted by WinUx persistence logic
- `/dev/sd*` or `/dev/nvme*` internal partitions without user confirmation

## First-run selector rule

The first-run storage selector should offer:

1. Use detected WinUx USB storage
2. Create/use WinUx-Capsules on WINUXDATA
3. Run disposable test session
4. Advanced: choose another location

Advanced choices must warn the user if the target appears to be a host/internal disk.

## Product promise

WinUx Portable should feel safe to boot on a stranger machine:

```text
No install.
No host mess.
No mystery writes.
No residue unless chosen.
```

## Hard boundary

Do not sacrifice leave-no-trace behavior just to make persistence easier.

A portable OS that casually writes to the host is not portable. It is a rude little bastard.
