# venvWin Portable — size and usefulness budget

## Mission

Lucid Puppy 5.2.8 proved that a small portable image can include tools for
real work. **A smaller useless system is not a win.** venvWin prioritizes
useful capabilities per installed megabyte and per megabyte of idle RAM.

The old 1.5 GB Debian/XFCE standard prototype is **historical evidence of
architectural drift**, not the release-size baseline.

## Current source policy

- Default `core`: kernel, initramfs, compressed root, lightweight desktop,
  browser, AbiWord/Gnumeric, imaging, audio, storage and practical diagnostics,
  Python plus venvWin
- `standard` and `privacy`: legacy manual validation profiles, not the
  default or a model for the primary image
- Wine, full office suites, privacy tools and developer packages should
  eventually load as optional SFS modules; separate package lists alone are
  **not** independently loadable modules
- Never embed the GitHub repository, tests, CI workflows, development docs or
  build scripts in the OS; include only the runtime source and user intro
- Disposable USB live session by default; no forced persistence or `toram`

## Measurable core goals (not current results)

| Measurement | Early target | Gate |
|---|---|---|
| Compressed core ISO size | Aim for 512 MiB or less | Above 512 MiB: warning; above 900 MiB: fail core packaging |
| Guest boot | Linux and desktop confirmed by guest-side evidence | Mandatory |
| RAM mode | Enough available RAM after SFS copy and runtime reserve | Mandatory before enablement |
| Persistence | Save only after choosing persistence; reboot tests | Mandatory before release |
| Features | Browser, docs, sheets, graphics, storage, sound, capsules | Verify functionality, not package names |
| Host disks | No unrequested writes in live mode | Evidence required |
| SFS modules | Independently mountable, integrity-checked add-ons | Not implemented |

Size targets are engineering constraints, **not** claims that an image of this
size already exists. Record actual ISO size, compressed SFS bytes, total
guest RAM, idle RAM, boot duration and functionality coverage from the same
reproducible image digest. If a leaner replacement loses necessary functions,
either restore the compact feature or implement an on-demand module.

## Historical builds

Older `standard` documentation permitted 2500-3500 MB and packed the
whole repository into the product. Those allowances are obsolete. The
remaining historical scripts exist for comparison and regression only;
manual execution does not turn an image into a release.

## BEAN release policy

Static build guards and package boundaries are only *source gates*.
Guest boot, OverlayFS, RAM copy, save/reboot, application SFS and capsule
functionality all require actual machine evidence and independent receipts.
No green badge for an unbooted system.
