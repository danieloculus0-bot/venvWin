# WinUx Portable Package Profiles

## Purpose

WinUx should have package profiles instead of one giant pile of everything.

This keeps the product aligned with the Puppy-style benchmark:

```text
small core
portable persistence
optional capability packs
```

## Profile 1: Core

Goal: smallest useful WinUx boot image.

Includes:

- live boot tooling
- basic desktop/session
- file manager
- terminal
- Python runtime
- venvWin CLI
- venvWin doctor
- EXE/MSI association handler
- persistence detection
- quick-start docs

Does not include:

- full Wine runner if we decide to split it later
- Tor Browser
- heavy browser
- developer tools

Risk:

```text
Without a runner, Core can manage capsules but cannot launch Windows apps.
```

## Profile 2: Standard

Goal: first sellable $8 image.

Includes:

- everything in Core
- Wine-compatible runner
- basic Windows app support packages
- private browser launcher
- Firefox/Tor fallback tooling if size allows
- dark desktop theme

This is the likely first commercial build.

## Profile 3: Privacy

Goal: stronger private browsing bundle.

Includes:

- Tor Browser or Tor Browser Launcher
- Tor service tools
- torsocks
- leak warning docs
- private browser launcher

This can be bundled into Standard if size is acceptable.

## Profile 4: Maker/Pro

Goal: future higher-tier utility image.

Includes:

- more compatibility recipes
- GUI capsule manager
- profile editor
- repair recipes
- better diagnostics
- optional dev tools

## Current alpha position

The current build script is closer to Standard because it includes:

- XFCE
- Wine
- Firefox ESR
- Tor/torsocks
- venvWin

That is acceptable for the first bootable alpha, but we should measure it and trim.

## Trim candidates

If size gets stupid:

1. remove Firefox ESR and rely on Tor Browser install flow
2. reduce XFCE packages
3. remove git from product image
4. remove python3-pip from product image
5. remove extra docs/manpages/locales in chroot cleanup
6. split Wine into Runner Pack later

## Hard rule

WinUx Standard must not become a generic Linux distro with venvWin sprinkled on top like seasoning.

If a package does not help boot, persist, run capsules, recover, browse privately, or explain the system, question it.
