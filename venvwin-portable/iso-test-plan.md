# venvWin Portable ISO Test Plan

## Goal

Prove the ISO actually boots and the product hook works.

## Test 1: ISO artifact exists

Expected:

```text
dist/venvwin-portable-alpha-standard.iso
dist/venvwin-portable-alpha-standard.iso.sha256
```

## Test 2: VM boot smoke test

Boot in VirtualBox, VMware, GNOME Boxes, or QEMU.

Expected:

- ISO reaches graphical desktop
- XFCE session starts
- desktop does not look completely cursed
- first-run creates quick-start text file
- first-run creates doctor output file

## Test 3: venvWin CLI

Run:

```bash
venvwin doctor
venvwin init
venvwin create "Test App"
venvwin list
```

Expected:

- commands run
- capsule is created under `~/venvWin-Capsules`
- doctor output is understandable

## Test 4: EXE/MSI association

Run:

```bash
venvwin associate
```

Then double-click a simple Windows EXE installer or portable EXE.

Expected:

- file routes to venvWin
- capsule is created or reused
- state is recorded

## Test 5: persistence

Boot with persistence enabled on USB.

Expected:

- `~/venvWin-Capsules` survives reboot
- capsule metadata survives reboot
- snapshots survive reboot

## Test 6: RAM mode

Boot with `toram` when the machine has enough memory.

Expected:

- OS continues running after heavy USB reads stop
- capsule storage still writes to persistent storage

## Known alpha risks

- Wine package availability may vary by architecture/repo
- live-build may need package list tuning
- desktop association defaults may need DE-specific commands
- persistence partition setup is not fully automated yet
- first ISO may boot but look ugly as hell

## Product-ready rule

If it boots but double-click EXE does not route into venvWin, it is not product-ready.

If it routes EXE but loses capsule state after reboot, it is not product-ready.

If it works but looks like random rescue Linux from 2009, it is not product-ready.
