# venvWin Filesystem and State Model

## Goal

A Windows app should feel like it is running in its own Windows-like environment while still living on Linux.

No VM should be required for the primary path.

## Capsule filesystem

Each capsule owns a persistent fake Windows environment.

```text
capsules/<app>/
  venvwin.json
  prefix/
    drive_c/
      Program Files/
      Program Files (x86)/
      users/<user>/
        Desktop/
        Documents/
        Downloads/
        AppData/
          Local/
          Roaming/
    system.reg
    user.reg
    userdef.reg
  installers/
  launchers/
  snapshots/
  logs/
```

The prefix is the saved state. It is not disposable unless the user resets it.

## User file access

Apps need normal user-level access to expected folders without getting the keys to the whole damn machine.

Default mapping target:

```text
Windows path                  Linux target
C:\\users\\<user>\\Desktop      ~/Desktop
C:\\users\\<user>\\Documents    ~/Documents
C:\\users\\<user>\\Downloads    ~/Downloads
C:\\users\\<user>\\Pictures     ~/Pictures
C:\\users\\<user>\\Music        ~/Music
C:\\users\\<user>\\Videos       ~/Videos
```

The capsule should remember these mappings.

## Permissions model

venvWin should run with normal Linux user permissions by default.

Rules:

- no root by default
- no system-wide writes unless explicitly approved
- app state stays inside the capsule prefix
- user folder mappings are explicit
- repair/reset should never delete user documents
- launcher creation should write only user-local desktop/application files by default

## Double-click behavior

Double-clicking an `.exe` or `.msi` should route into venvWin.

Expected flow:

```text
User double-clicks setup.exe
venvWin receives file path
venvWin creates or reuses capsule
venvWin runs installer/open flow
venvWin records state
venvWin offers launcher creation
```

The user should not need to understand prefixes, env vars, or runner commands.

## State persistence

A capsule must preserve:

- installed app files
- registry files
- runner profile
- install history
- launch history
- filesystem mappings
- generated launchers
- snapshots
- repair history

## Snapshot rule

Snapshots are for app state, not user documents.

A rollback should restore the capsule prefix and metadata, but it should not destroy files in mapped Linux user folders.

## Product promise

From the user's point of view:

```text
Double-click EXE.
Install app.
Launch app.
State is remembered.
Files are where expected.
No VM circus.
```
