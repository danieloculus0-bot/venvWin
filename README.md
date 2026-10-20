# venvWin

Experimental GPL-3.0 Windows-compatibility capsule and portable Linux-system tooling. Official project use is intended to remain free of charge, including personal and business use.

## Current build state

**Reviewed:** 2026-10-20 · **Inspected main:** `9c4896392f0a`.

- [tests](https://github.com/danieloculus0-bot/venvWin/actions/runs/39489966536) — **Passed** at inspected `main`.
- [preflight-lite](https://github.com/danieloculus0-bot/venvWin/actions/runs/39489966865) — **Passed** at inspected `main`.
- [brand-audit](https://github.com/danieloculus0-bot/venvWin/actions/runs/39489966498) — **Passed** at inspected `main`.

[Live CI history](https://github.com/danieloculus0-bot/venvWin/actions) supersedes this dated report.

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

## Next work

Demonstrate verified live-boot first-run experience, persistence/isolation behavior and manifest-compliant redistributable images.

## References

- [Portable product gate](venvwin-portable/product-gate.md)
- [Project license](LICENSE)
- [Complete previous README and historical planning notes](docs/archive/README_2026-10-20_before_refresh.md)
