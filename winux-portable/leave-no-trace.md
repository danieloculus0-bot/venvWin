# WinUx Portable Traceable State Policy

## Product rule

WinUx Portable should be portable, lightweight, and respectful of the host machine.

That does not mean stealth. WinUx must be traceable to the user who booted it. It should avoid unwanted host changes while still keeping clear logs, proof files, and audit records inside the WinUx session and portable storage.

The correct promise is:

```text
No unwanted host writes.
No hidden desktop/browser residue.
Clear WinUx-owned proof and logs.
Traceable use, not stealth use.
```

## Better name

Do not market this as "leave no trace."

Use:

```text
Traceable Portable State
```

or:

```text
Host-respectful portable mode
```

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
- do not create random host desktop icons
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

These artifacts are for clarity and debugging, not concealment.

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

WinUx Portable should feel safe to boot on another machine without making a mess:

```text
No install by default.
No host mess.
No mystery writes.
No fake stealth claims.
Proof and logs remain in WinUx-owned storage.
```

## Hard boundary

Do not sacrifice traceability just to sound privacy-forward.

A portable OS that hides its own use is suspicious. A portable OS that avoids unwanted host writes while keeping honest logs is useful.
