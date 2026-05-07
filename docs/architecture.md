# venvWin Architecture

## One-line definition

venvWin is a capsule manager for Windows applications on Linux.

It does not try to become Windows. It creates reproducible, isolated, per-application environments that can be installed, repaired, snapshotted, launched, exported, and eventually surfaced through WinUx.

## Core philosophy

Windows app compatibility is usually treated like one giant global mess. venvWin treats every app like its own environment.

The model is closer to Python virtual environments than a traditional compatibility launcher.

Each application receives a capsule containing:

- metadata
- runner profile
- environment variables
- prefix path
- installer records
- launch records
- snapshot records
- repair history

## Product boundary

```text
WinUx
  The Linux-based OS wrapper and desktop product.
  It owns the user's operating experience.

venvWin
  The compatibility subsystem.
  It owns app capsules, launch behavior, runner profiles, snapshots, and compatibility plumbing.
```

## Capsule lifecycle

```text
create
  make capsule directory
  write capsule metadata
  assign runner profile

install
  record installer
  run through selected runner
  capture changed state later

launch
  use capsule metadata
  apply runner profile
  execute configured target

snapshot
  archive capsule state
  allow rollback

repair
  reset known-bad state
  reapply profile
  optionally reinstall dependencies
```

## Runner abstraction

venvWin should not hardcode one compatibility tool forever.

A runner is any backend capable of preparing, installing, or launching a Windows application inside a capsule.

Initial runner targets:

- wine-compatible command runner
- proton-compatible command runner
- scripted custom runner
- VM fallback runner later

## Non-goals for the first milestone

- replacing the Windows API
- building a Linux distribution
- solving every Windows app
- pretending compatibility is magic
- hiding errors before we understand them

## First useful MVP

A successful MVP can:

1. create a capsule
2. list capsules
3. inspect capsule metadata
4. define profiles
5. generate install commands
6. generate launch commands
7. keep each app isolated

After that, WinUx can wrap it in a friendly shell.
