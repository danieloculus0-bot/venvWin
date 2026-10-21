# venvWin Portable — Puppy-adjacent, not a Puppy fork

**Status: development / NOT BOOT-VERIFIED.** Do not flash as a finished product.

Lucid Puppy 5.2.8 is the architecture inspiration, not a kernel or package
source to copy. venvWin should be a ridiculous amount of usefulness packed
into a fast, compact USB-first environment on old x86_64 machines.

## The one bundled game: Emperor Gauntlet

**Emperor Gauntlet is the ONLY arcade game shipped in venvWin Portable.** It is the real, standalone HTML/Canvas/JavaScript game from [FUN](https://github.com/danieloculus0-bot/FUN) (source commit `49dfdb3127e6ba2fcacd610cfea211a61ee36e53`), vendored at `src/venvwin/games/emperor-gauntlet/play.html`. The game requires **no network connection, Python/Pygame runtime, server, or downloaded game assets**.

The ISO build creates **Emperor Gauntlet** in the desktop Applications → Games menu and places `venvWin-Emperor-Gauntlet.desktop` on the live-user desktop. The launcher opens the local `file://` game in Firefox ESR on standard/privacy images or Epiphany/WebKit on the core image. NetSurf is retained for lightweight browsing but is **not** used for this HTML5 canvas game.

The older **Frontier Trail** remains as a separate developmental Python source project and is **excluded from the live image and its Games menu**. The game is not an Axiom manufacturing module; this is a deliberately small, fun feature of the portable OS.

The game HTML is small; a capable WebKit/Firefox browser is not. Verify its installed-size impact, cold-start memory, frame rate and keyboard/audio behavior on the target Puppy hardware before approving the lean-core ISO. This source/launcher change does **not** establish a successful ISO build, QEMU boot, or physical-machine gameplay test.

## What belongs

- A small modern kernel/initramfs, compressed read-only SquashFS base and
  a compact desktop with obvious launchers
- Real everyday tools: browser, document and spreadsheet editing, graphics,
  file management, audio, storage, diagnostics and rescue utilities
- The **venvWin compatibility engine** for EXE/MSI routing, Wine capsules,
  snapshots and recovery; large runners can be independent modules
- Puppy-style sessions: a disposable writable RAM overlay by default,
  optional copy-to-RAM when measurable and safe, **opt-in saving** to USB
- Independent optional application, driver and development SFS packs
- BEAN-backed evidence for boot, mount structure, memory, persistence,
  module loading, and Windows-app behavior

## What does NOT belong in the base image

- The GitHub repository, tests, development toolchain or CI files
- Heavy duplicate browsers and LibreOffice suites just to tick a box
- Always-on persistence or unrequested host-disk writes
- A giant standard-image build on every source-control push
- Fake "boot-ready" labels inferred from shell scripts or static directory checks

The `core` profile is now the default source build target. The larger
`standard` and `privacy` package sets remain available **only as legacy
reference/testing profiles** until independent SFS app modules are verified.
We have not yet measured the new core ISO size or proved it boots.

The reusable application engine lives under `src/venvwin`. No existing
application code is discarded solely to save bytes; only the contents
packed into the always-loaded base image are cut.

See `docs/puppy-bean-evidence-contract.md` for evidence requirements.
