# venvWin Portable — Puppy Linux native core

**Status: experimental Puppy-native branch, not a released operating system.**

venvWin is a modular Windows-application capsule system intended for a real,
lightweight, portable Puppy Linux desktop. We are moving away from the previous
homegrown Debian live-build OS. The entire old main-branch implementation is
preserved at [archive/debian-live-build-20261011](../../tree/archive/debian-live-build-20261011).
The existing [GRUB repair draft PR #17](../../pull/17) is historical comparison,
not the foundation for this Puppy implementation.

## Genuine upstream operating-system foundation

- **BookwormPup64 10.0.12** from the official Puppy Linux distributor:
  https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.12/
- Expected upstream ISO SHA-256:
  `ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f`
- Upstream is roughly 791 MiB. Actual remastered size requires measured CI results.
- Puppy already provides a real bootloader, kernel, initramfs, modular compressed
  SFS system, OverlayFS live root, desktop, and Puppy persistence mechanisms.
- venvWin is added as an **independent `ydrv_dpupbw64_10.0.12.sfs` layer**,
  not by replacing the official base, its firmware, initramfs, or bootloader.
- `xorriso` remasters the ISO with its original El Torito/EFI boot records
  replayed. Real BIOS and UEFI guest boots remain separate tests.

## What venvWin adds

The Python app source under `src/venvwin` stays intact and is integrated as
`/opt/venvwin/src`. The small wrapper at `/usr/local/bin/venvwin` supports
the same capsule create/list/inspect, installer routing, snapshots, recovery,
EXE/MSI association handling, CLI tools and local dashboard architecture.

Actual Windows EXE execution requires a compatible **Wine runner**; it is not
silently assumed to be included with the Puppy core. Wine support can be
packaged later as its own independent SFS module.

If Python 3.10+ is missing in a live Puppy guest, venvWin reports the missing
dependency instead of claiming working application integration. The guest
boot probe must actually execute the capsule CLI before core boot is accepted.

## Tested stages and gates

Source-only checks:
`python -m pytest -q tests/test_puppy_native_contract.py`.

One isolated real ISO/QEMU experiment:
`puppy-native/build-puppy.sh` and
`puppy-native/prove-puppy-qemu.sh`, run by
[the native Puppy guest build workflow](../../actions/workflows/puppy-native-boot-lab.yml)
on the isolated branch.

The CI gate rejects images with a bad upstream SHA-256, missing Puppy files,
an already-used `ydrv` filename, missing remaster boot records, or absent
**guest-origin serial markers**. A QEMU window or successful shell syntax
check is never treated as proof that the desktop booted.

| Product gate | Proof still required |
| --- | --- |
| Genuine upstream Puppy kernel, bootloader and SFS | Pinned ISO checksum and remaster inventory |
| Guest Linux and graphical session | Guest-origin QEMU serial marker |
| Actual writable live OverlayFS | Guest mount evidence |
| venvWin capsule engine in the live desktop | Guest-origin init/list tests |
| Optional copy-to-RAM | Measured SFS sizes, available RAM and actual copy |
| User-chosen persistence | Savefile/savefolder proven after genuine reboot |
| External app modules | Independently loaded/unloaded SFS with hash and behavior |
| Windows compatibility | End-to-end EXE installation and rollback inside live Puppy |

Passing the first three live checks is **not** evidence that the full product
gates passed. Full six-gate BEAN readiness requires additional repeated
post-reboot verification and real application tests.

## Build locally

Requires Linux and `curl`, `xorriso`, `squashfs-tools`, `rsync`, QEMU,
Python 3.10+, and optional KVM for faster tests.

```sh
python -m pip install -e . pytest
python -m pytest -q tests/test_puppy_native_contract.py
bash puppy-native/build-puppy.sh
bash puppy-native/prove-puppy-qemu.sh
```

The build downloads an **unchanged authenticated upstream Puppy ISO** and adds
a small version-specific SFS. It does not run the old Debian `live-build`
system. The QEMU experiment has an isolated CD-ROM and no attached hard drive
or guest networking.

**Release policy:** no ISO uploaded as a release candidate, no replacement
of `main`, and no deletion of legacy code until native boot and application
integration evidence genuinely pass. Even then, missing persistence, RAM,
module and Wine gates must be explicitly documented, not disguised as success.

## Development history

All prior Debian/XFCE scripts, historical Windows compatibility tests,
documentation, and proof attempts remain recoverable in the archive branch.
Once the native product passes its release criteria, the new main branch can
be cleaned of the obsolete Debian builder and its workflows. Never delete
`src/venvwin`, the tests for its actual functionality, or BEAN evidence
contracts merely to save repository bytes.
