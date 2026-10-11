# venvWin Portable Package Profiles

## Design law

We are building a **Puppy-adjacent Swiss Army knife**, not a stripped-down
Debian rescue shell and not a literal Lucid Puppy fork. Functionality per
megabyte, fast USB/RAM sessions, user-chosen persistence and small add-on
layers matter more than the number of included package names.

## Core: default source build

The source-level core has 61 listed packages. It retains a browser,
file manager, terminal, networking, useful old-hardware firmware,
USB/NTFS/exFAT tools, AbiWord, Gnumeric, simple graphics, audio,
Python and the venvWin engine. The underlying dependencies and actual
image size have **not been measured**; this is a package-list count.

The core must launch a real desktop and accept an EXE/MSI capsule;
without the Wine runner installed it should explain that Windows app
execution requires an optional runner. A source-level GUI promise does
not prove working native compatibility.

## Standard and privacy: historical laboratory profiles

The remaining 28 source-level packages stay in the larger conditional
`05-venvwin-utilities.list.chroot` list, and the standard/private runner
lists supply Wine, browsers and tools used by the prior 1.5 GB prototype.

These are for **explicit manual testing**, not the default product image.
The standard GitHub ISO workflow is manual-only. Do not ship or auto-build
these monolithic profiles as the end goal.

## Actual target: load useful packs independently

Future `venvwin-runner.sfs`, `venvwin-apps.sfs`,
`venvwin-drivers.sfs`, and `venvwin-dev.sfs` packs should be separately
mountable, hash-verified and removable. Merely separating APT package
lists does NOT implement this behavior.

The package split exists to measure and preserve functions while a
Puppy-style OverlayFS/SquashFS architecture is built and boot-tested.

## Packaging/boot rules

- Only application runtime code and one short user README belong in the
  base image; never the full development repository, tests or CI files.
- Never enable persistence by default; do not write to a host disk without
  a specific user choice.
- Copying the compressed root into RAM is optional, memory-budgeted and
  must be observed before BEAN calls it implemented.
- Core size target: <=512 MiB; core hard rejection above 900 MiB.
  Those are budget goals, **not actual measured results**.
- BEAN's 2/6 source checks do not establish runtime boot readiness.

**No application code is deleted to fake a smaller product.** Large
dependencies can move out of the always-loaded base, while preserving a
simple UI for installing/mounting additional capabilities.
