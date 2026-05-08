# WinUx Portable Leave-No-Trace Policy

## Product rule

WinUx Portable is a lightweight portable Linux environment for making old PCs useful again.

Leave No Trace means no host hard-drive writes by default. It does not mean stealth, hidden use, hacking, secrecy, or pretending the machine was never booted.

The selling point is simple:

```text
Boot from USB.
Run from USB/RAM.
Store WinUx state on WinUx-owned storage.
Do not consume or modify the host PC hard drive unless the user explicitly chooses it.
```

## Target feel

WinUx should feel closer to the useful old Puppy Linux era than a bloated modern desktop distro.

Design targets:

- boots on older 2010-ish PCs where practical
- lightweight desktop
- simple launcher model
- portable state
- minimal background nonsense
- clear logs and proof inside WinUx storage/session
- no host desktop or browser spam

## What LNT means here

LNT means:

- do not write to host internal drives by default
- do not install onto the host by default
- do not modify host browser settings
- do not drop host desktop icons
- do not alter host startup entries
- do not mount internal disks read-write unless explicitly chosen
- keep capsules, logs, and proof files on WinUx-owned storage when possible

LNT does not mean:

- hiding activity
- disabling logs
- removing evidence from WinUx-owned storage
- bypassing auditability
- behaving like hacker trash

## Default writable target

Default writable state should go to WinUx-owned storage:

```text
WINUXDATA/WinUx-Capsules
```

or another detected WinUx-owned persistent storage path.

## Host machine policy

Default behavior:

- do not write to host internal disks unless the user explicitly chooses it
- do not auto-mount host internal disks read-write
- do not create host files
- do not create host desktop icons
- do not modify host browser settings
- do not install launchers onto the host OS
- do not modify the host bootloader
- do not touch host user folders without explicit user action

Allowed only with explicit user action:

- mount host drive read-write
- copy files to/from host drive
- choose host folder as capsule storage
- install WinUx/venvWin onto host

## Traceability policy

WinUx should create and preserve evidence of use in WinUx-owned locations.

Required traceable artifacts:

- desktop first-boot proof files during live session
- storage selection marker
- persistence report
- venvWin doctor output
- first-run logs
- association attempt logs
- storage status logs
- capsule metadata
- install/open dry-run records when applicable

These artifacts are for clarity, debugging, support, and honest traceability. They should live in the WinUx session or WinUx-owned storage, not sprayed across the host PC.

## Desktop/browser residue rule

WinUx should not leave annoying residue on the host.

Default behavior:

- no host desktop shortcut spam
- no host browser homepage changes
- no host browser bookmark injection
- no silent shell integration into the host OS
- no hidden host startup entries

WinUx desktop proof files are acceptable because they exist inside the WinUx live desktop/session, not on the host OS desktop.

## Capsule storage rule

venvWin capsules should live on portable storage by default.

```text
preferred: /media/<user>/WINUXDATA/WinUx-Capsules
fallback: /run/live/persistence/WinUx-Capsules
last resort: ~/WinUx-Capsules with disposable warning
```

The fallback home path is allowed only for testing or true persistent live-home sessions.

## Disposable warning

If WinUx cannot find writable WinUx-owned storage:

```text
Warning: no WinUx-owned persistent storage found. This session may be disposable. Installed apps may vanish after reboot. Use this for testing, not real work.
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

WinUx Portable should feel safe to boot on an old or borrowed machine without making a mess:

```text
No install by default.
No host disk usage by default.
No browser/desktop residue on the host.
No mystery writes.
Proof and logs remain in WinUx-owned storage/session.
```

## Hard boundary

Do not sacrifice LNT just to make persistence easier.

A portable OS that casually writes to the host hard drive is not portable. It is just a rude little bastard with a boot menu.
