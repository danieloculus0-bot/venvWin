# WinUx Portable Build Plan

## Stage 1: Prototype image

Goal: bootable USB image with venvWin installed and runnable.

Tasks:

- choose live-image toolchain
- choose lightweight desktop
- add venvWin package install step
- enable persistent storage target
- add EXE/MSI association command
- boot test on normal x86_64 PC

## Stage 2: Product polish

Goal: make it look and feel intentional.

Tasks:

- dark desktop theme
- WinUx wallpaper
- venvWin launcher icon
- quick-start shortcut on desktop
- app menu entries
- first-run welcome note

## Stage 3: RAM mode

Goal: support loading the compressed OS image into RAM when enough memory exists.

Tasks:

- document boot parameter
- test memory threshold
- keep capsule storage persistent
- prevent accidental disposable state confusion

## Stage 4: Persistence

Goal: make state survival obvious and reliable.

Tasks:

- default `VENVWIN_HOME` to persistent partition when available
- expose current capsule storage path
- warn when running disposable session
- add reset/repair docs

## Stage 5: Sellable $8 build

Goal: create a small, understandable, shippable digital product.

Tasks:

- image file
- checksum
- flashing instructions
- quick-start guide
- tested app demo list
- known limitations
- license/source notice

## Technical preference

Use boring proven tooling first. Weird clever tooling can wait.

## Hardware targets

Primary:

- x86_64 laptop/desktop
- USB 3.0 flash drive or SSD stick

Secondary:

- Jetson-class ARM Linux target later
- old PCs with enough RAM for live boot

## Failure rule

If it boots but looks like random Linux junk, it is not product-ready.

If it looks good but double-click EXE does not route into venvWin, it is not product-ready.
