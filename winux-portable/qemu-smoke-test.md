# WinUx Portable QEMU Smoke Test

## Purpose

This is the first virtual learing loop for the ISO.

The test does not prove the desktop is beautiful or that every app works. It proves the ISO is not obviously dead on arrival.

## Current GitHub Actions flow

The `build-winux-iso` workflow now does this:

```text
Install live-build and QEMU tooling
Build WinUx Portable ISO
Verify checksum
Inspect ISO boot structure with xorriso
Look for filesystem.squashfs
Look for kernel/initrd paths
Boot ISO headless in QEMU for 150 seconds
Upload ISO artifact if the smoke test survives
```

## Why timeout can pass

For the alpha smoke test, QEMU staying alive for 150 seconds is treated as a pass.

That means:

```text
The ISO booted far enough not to instantly crash, panic, or exit.
```

It does not mean:

```text
The GUI is good.
Persistence works.
EXE double-click is perfect.
The product is ready.
```

## Next virtual test upgrades

Future improvements:

- boot with serial console target
- grep boot logs for Linux kernel startup
- test boot menu behavior
- run a tiny VM disk for persistence testing
- use QEMU screenshots or VNC for desktop proof
- run a guest-side first-run marker check

## Product-ready rule

Passing QEMU smoke means only one thing:

```text
The corpse twitched. Now we see if it can walk.
```
