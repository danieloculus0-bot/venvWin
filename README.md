# venvWin

Experimental GPL-3.0 Windows-compatibility capsule and portable Linux-system tooling. Official project use is intended to remain free of charge, including personal and business use.

## Current build state

**Reviewed:** 2026-10-20. The current README contract tests on main were out of date after the documentation refresh. This branch updates those tests; [live CI history](https://github.com/danieloculus0-bot/venvWin/actions) is the authority for pass/fail status.

## Implemented or recorded today

- Windows compatibility-capsule tooling, local filesystem/state abstractions and experimental image/first-run build tooling.
- Automated project tests, lightweight preflight and branding checks in GitHub Actions.
- Experimental venvWin Portable Linux path; the current source/build tools do not prove a universally bootable hardware image.

## Run and verification

See [archived README and build instructions](docs/archive/README_2026-10-20_before_refresh.md) plus `venvwin-portable/product-gate.md` for image validation criteria. Run repository-provided test and preflight scripts before distribution.

## Known boundaries

- Physical hardware boots and application compatibility must be measured on target devices; CI alone does not demonstrate them.
- Linux distributions, Wine, kernel and bundled dependencies keep **their own upstream licenses**. The project [GPL-3.0 license](LICENSE) does not relicense those works.
- No-fee distribution is project policy, not a restriction on lawful GPL redistribution.

## Native Puppy migration and acceptance

The native BookwormPup64 migration is being developed on separate experimental branches, not on main. Genuine graphical guest boot and capsule CLI have been observed, but this does **not** establish release readiness. The approved Amber Arc desktop wallpaper still needs guest verification after start-menu interaction and reboot. The Wine EXE/MSI installation and launch path inside a live Puppy guest remains unproven; Ubuntu-host Wine tests are not substitutes.

Release requires separate guest-origin evidence for: BIOS/EFI boot, OverlayFS mounts, optional RAM-copy measurements, explicitly chosen persistence surviving reboot, independent SFS application loading, and Windows EXE/MSI capsule installation and launch with BEAN hash-chained receipts. Draft migration PRs must remain unmerged until these gates pass.

## Next work

Repair and validate native Puppy wallpaper persistence in a real guest; continue independent Wine integration testing; demonstrate live-boot first-run experience, persistence/isolation behavior and manifest-compliant redistributable images. Preserve the approved Amber Arc artwork. venvWin is intended to remain free of charge for personal and small-business use, while honoring upstream Linux and Wine licenses.

## References

- [Portable product gate](venvwin-portable/product-gate.md)
- [Project license](LICENSE)
- [Complete previous README and historical planning notes](docs/archive/README_2026-10-20_before_refresh.md)
