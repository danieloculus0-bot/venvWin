# venvWin — Puppy-native migration candidate

**Status: unreleased experimental Puppy remaster, not yet boot-proven.**

The legacy Debian/XFCE live-build implementation has been preserved on [archive/debian-live-pre-puppy-20261011](https://github.com/danieloculus0-bot/venvWin/tree/archive/debian-live-pre-puppy-20261011). The new system is being built from **actual BookwormPup64 10.0.12**, inheriting its upstream bootloader, initramfs, SFS layers, RAM options and Puppy persistence infrastructure.

## Puppy-native build and evidence

- Source: [official BookwormPup64 10.0.12 distribution](https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.12/), pinned ISO SHA-256 ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f.
- Build script: puppy-native/build.sh. It verifies upstream bytes, adds original venvWin source as an independent Puppy adrv/ydrv SFS, and replays the upstream ISO boot records without injecting Debian live-build.
- Test workflow: .github/workflows/puppy-native-boot.yml. Source-only tests first, then the real ISO and a diskless QEMU boot test. Only guest-generated serial proof is accepted.
- Readiness: **not ready until successful real boot, live layer checks, optional copy to RAM, persistence across a reboot, modular SFS use, and Windows-app capsules in the guest.** Python source being packaged does not prove that Puppy has its Python, Wine or GUI dependencies.
- Size: optimize only after confirming boot and function. A 900 MiB target is not a reason to reject an otherwise functional experimental image.
- Promotion: no deletion of legacy or merge into main before verified boots and the product gates. Until then, this branch is a **release candidate**, not a release.

The previous Debian build remains documented below for historical context. Its paths are not the intended future boot architecture.

---

## Archived implementation README (legacy)

# venvWin

Experimental GPL-3.0 Windows-compatibility capsule and portable Linux-system tooling. Official project use is intended to remain free of charge, including personal and business use.

## Current build state

**Reviewed:** 2026-10-20 · **Inspected main:** `55bb11d1644f`.

- [tests](https://github.com/danieloculus0-bot/venvWin/actions/runs/39516239383) — **Passed** after README contract repair at inspected `main`.
- [preflight-lite](https://github.com/danieloculus0-bot/venvWin/actions/runs/39516239457) — **Passed** at inspected `main`.
- [brand-audit](https://github.com/danieloculus0-bot/venvWin/actions/runs/39516239415) — **Passed** at inspected `main`.

[Live CI history](https://github.com/danieloculus0-bot/venvWin/actions) supersedes this dated report.

## Implemented or recorded today

- Windows compatibility-capsule tooling, local filesystem/state abstractions and experimental image/first-run build tooling.
- Automated project tests, lightweight preflight and branding checks in GitHub Actions.
- Experimental venvWin Portable Linux path; the current source/build tools do not prove a universally bootable hardware image.

## Bundled offline games: Emperor Gauntlet and Cletus Saves Candy

Both [Emperor Gauntlet](https://github.com/danieloculus0-bot/FUN/blob/main/emperor-gauntlet/play.html) and [Cletus Saves Candy](https://github.com/danieloculus0-bot/FUN/blob/main/docs/cletus/play.html) are included as local HTML/JavaScript games in venvWin Portable. Each has a **branded Applications > Games icon and its own desktop launcher**; Cletus uses an offline replacement cover image and local font fallbacks. The compact core uses Epiphany/WebKit; standard/privacy use Firefox ESR. No separate server, game runtime install, or internet is required for gameplay. Frontier Trail stays in source, excluded from the live image.

This verifies source and ISO build-recipe integration only, **not** a booted ISO or tested guest gameplay. [Integration limitations](venvwin-portable/README.md#bundled-offline-games).

## venvWin Portable product and release gate

**venvWin Portable** is the proposed USB-first lightweight Linux desktop product. The compatibility-capsule engine is a component; **Wine is allowed as backend number one. Wine is not the product.** Native Windows application compatibility and live boot remain subject to real hardware validation.

**Windows PowerShell WSL build runner** (repo root, Windows with WSL installed):

```powershell
.\venvwin-portable\run-wsl-flash-ready.ps1
```

- [Local WSL/Linux flash-ready build instructions](venvwin-portable/local-flash-ready-build.md)
- [USB flash and verification guide](venvwin-portable/usb-flash-guide.md)
- [Independent boot/product acceptance gates](venvwin-portable/product-gate.md)

The intended **first-boot desktop launchers** are `venvWin-First-Boot.desktop`, `venvWin-Dashboard.desktop`, `venvWin-Capsules.desktop`, `venvWin-Doctor.desktop`, and `venvWin-Private-Browser.desktop`. These are artifact-contract requirements, **not evidence that a bootable release is already available**.

The **standard-image gate** describes the expected filenames, not downloads certified by this README:

- `venvwin-portable-alpha-standard.iso`
- `venvwin-portable-alpha-standard.iso.sha256`
- `venvwin-portable-alpha-standard-manifest.txt`
- `venvwin-flash-ready-verdict.txt`
- `venvwin-portable-flash-ready-standard` (the expected gate/artifact label)

A genuine, independently verified verdict must contain `status=FLASH_READY` before describing a particular build as flash-ready. No such current artifact is implied here. The new compact/core packaging direction is still experimental; older standard-image requirements remain in the regression/compatibility contract until consciously versioned.

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
