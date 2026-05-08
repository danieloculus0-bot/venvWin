# venvWin Portable

venvWin Portable is the first shippable product target for venvWin.

It is a bootable Linux USB environment with venvWin preinstalled, persistent capsules, dark lightweight desktop styling, and EXE/MSI double-click routing.

## MVP promise

```text
Flash USB.
Boot venvWin Portable.
Double-click Windows EXE/MSI.
venvWin creates or reuses a capsule.
App state persists.
No VM required for the normal path.
```

## Build target

Start with a Debian/Ubuntu-family live image because package availability, live image tooling, and hardware compatibility matter.

## Planned image contents

- lightweight desktop environment
- dark venvWin theme
- venvWin CLI
- venvWin file associations
- Wine-compatible runner backend
- persistent capsule storage path
- offline quick-start guide

## Directory purpose

This folder is for venvWin Portable build scripts, image configuration, branding assets, boot notes, and packaging docs.

venvWin engine code stays in `src/venvwin`.
