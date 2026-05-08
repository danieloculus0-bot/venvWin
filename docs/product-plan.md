# WinUx Portable Product Plan

## Product concept

WinUx Portable is the first sellable version of the WinUx idea.

It is a lightweight bootable Linux USB image with venvWin preinstalled, dark premium desktop styling, and EXE/MSI double-click handling.

The first product is not a full Windows replacement. It is a portable compatibility workstation.

## Target price

Initial target: $8 digital download.

The goal is impulse-buy pricing for tinkerers, repair people, Linux users, makers, students, and anyone who wants a pocketable Windows-app-friendly Linux environment.

## First user promise

```text
Download image.
Flash USB.
Boot WinUx Portable.
Double-click Windows installers/apps.
Keep state in venvWin capsules.
```

## MVP feature set

- bootable USB image
- dark lightweight desktop
- venvWin installed
- persistent venvWin capsule storage
- EXE/MSI file association
- simple capsule manager GUI planned
- offline-friendly documentation
- repair/reset commands

## Design direction

Visual target:

- Linux Mint familiarity
- dark premium finish
- charcoal panels
- muted blue accent
- clean app launcher
- no bloated theme gimmicks
- Jetson-friendly and low-spec friendly

## Technical base candidates

Start with a Debian/Ubuntu-family live image because tooling and package availability matter more than being exotic.

Likely desktop targets:

- XFCE for lightweight builds
- Cinnamon-like visual direction if performance allows
- GTK-based venvWin GUI for low overhead

## Packaging idea

Sell as:

- downloadable image
- checksum
- quick-start PDF or markdown guide
- optional free community/dev build later
- paid polished portable build

## GPL note

The repo is GPL-3.0, so selling is allowed, but source availability and license compliance must be handled cleanly.

The sellable value should be packaging, polish, convenience, documentation, tested profiles, and easy setup rather than pretending open-source code is locked down.

## First commercial milestone

A believable $8 build only needs to do this well:

1. boot from USB
2. look clean and intentional
3. launch venvWin
4. double-click EXE/MSI into a capsule flow
5. save app state persistently
6. avoid VM dependency
7. include one or two tested app demos

## Hard rule

Do not build a bloated distro. Build a slick portable tool first.
