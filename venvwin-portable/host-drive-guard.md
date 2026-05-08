# venvWin Portable Host Drive Guard

## Purpose

Leave-no-trace mode needs a practical guardrail:

```text
Do not write to host internal disks by default.
```

This document defines the next layer after storage selection.

## Default behavior

venvWin Portable should default to:

- portable USB storage for capsules
- no automatic host writes
- host/internal drives treated as risky targets
- user-visible warnings before advanced host storage choices

## Desktop behavior target

The file manager may show host drives, but venvWin should not silently use them for capsule storage.

Future hardening options:

- disable automount of internal drives
- mount internal drives read-only by default
- require explicit user action for read-write mount
- show a warning before selecting host paths for `VENVWIN_HOME`

## First implementation already added

The persistence detector marks storage candidates with:

```text
portable_owned
host_risk
leave_no_trace
host_write_warning
```

`venvwin storage` exposes those flags so the user can see where writes are going.

## Future command idea

```bash
venvwin host-guard status
venvwin host-guard strict
venvwin host-guard relaxed
```

### strict

- avoid automounting internal drives
- prefer read-only internal mounts
- warn before host writes

### relaxed

- allow normal file manager mounting
- still do not use host storage for capsules unless explicitly selected

## Rule

The OS can read from the host when the user asks.

It should not scribble on the host like a drunk raccoon with root privileges.
