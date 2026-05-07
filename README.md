# venvWin

venvWin is the app compatibility engine for WinUx.

WinUx is the Linux-based OS wrapper and product shell. venvWin is the subsystem that manages isolated Windows-like app environments on Linux.

The goal is not to rebuild Windows from scratch. The goal is to make Windows app compatibility boring, repeatable, isolated, recoverable, and easy enough that a normal user can install an app without spelunking through prefix hell.

## Product split

```text
WinUx
  OS wrapper
  Desktop shell
  App launcher
  System settings
  Update manager
  venvWin integration

venvWin
  Per-app capsules
  Runner profiles
  Isolated prefixes
  Installer capture
  Launcher generation
  Snapshots and rollback
  VM fallback later
```

## First milestone

Build a working Python CLI that can:

- create a capsule
- list capsules
- inspect capsule metadata
- store runner profiles
- prepare install and launch commands without hardcoding the runner

This starts as plumbing. The shiny WinUx shell comes later.
