# Emperor Gauntlet / Puppy venvWin core ISO build request — October 20, 2026

This file is the explicit **one-time build trigger** for
`.github/workflows/puppy-emperor-core-candidate.yml`.

- Bundled sole game: **Emperor Gauntlet**, official original name.
- Source: `FUN` HTML game pinned to `49dfdb3127e6ba2fcacd610cfea211a61ee36e53`.
- Target: compact `venvwin-portable-alpha-core.iso`, with offline desktop/Games-menu launcher.
- Validation: real Debian Bookworm ISO build, SHA-256, actual filesystem
  inspection, absence of old game, QEMU guest boot/first-run proof.
- Do not call the release ready until the actual CI verdict passes.
- No Tux-branded name or second bundled game.

Only commits modifying this request file trigger the heavy build; everyday
source and README commits do not.

## Build retry

Re-trigger after correcting the flash-ready shell syntax regression detected by the first run. Gate correction commit: `ef06e6123fbdb4ab7138d1f79428d8e3269cfb1f`.
