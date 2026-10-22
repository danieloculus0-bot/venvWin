# venvWin Portable — Puppy-adjacent, not a Puppy fork

**Status: development / NOT BOOT-VERIFIED.** Do not flash as a finished product.

Lucid Puppy 5.2.8 is the architecture inspiration, not a kernel or package
source to copy. venvWin should be a ridiculous amount of usefulness packed
into a fast, compact USB-first environment on old x86_64 machines.

## Bundled offline games

venvWin Portable packages two [FUN](https://github.com/danieloculus0-bot/FUN) games: **Emperor Gauntlet** and **Cletus Saves Candy**. They are vendored under `src/venvwin/games/`. The Cletus edition replaces online font dependencies and its remote cover-art dependency with offline-safe assets. No network, Python/Pygame runtime, or game server is required.

Each game has a **branded SVG icon** in Applications > Games and an independent desktop shortcut (`venvWin-Emperor-Gauntlet.desktop` and `venvWin-Cletus-Saves-Candy.desktop`). Launchers use Firefox ESR on standard/privacy images and Epiphany/WebKit on the core image; lightweight NetSurf does not support these games.

The older **Frontier Trail** remains excluded from the live image. A modern browser's installed footprint is considerably larger than the game files, so validate cold-start memory, frame rate, offline artwork, audio and keyboard/controller behavior on actual hardware. These source and builder changes **do not prove ISO boot success or in-guest gameplay**.

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
