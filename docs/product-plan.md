# venvWin Portable Product Plan

## Product concept

venvWin Portable is the first sellable version of the venvWin idea.

It is a lightweight bootable Linux USB image with venvWin preinstalled, dark premium desktop styling, and EXE/MSI double-click handling.

The first product is not a full Windows replacement. It is a portable compatibility workstation.

## Target price

Initial target: $8 digital download.

The goal is impulse-buy pricing for tinkerers, repair people, Linux users, makers, students, and anyone who wants a pocketable Windows-app-friendly Linux environment.

## First user promise

```text
Download image.
Flash USB.
Boot venvWin Portable.
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

## Technical foundation: native Puppy Linux

Use the genuine SHA-256-pinned BookwormPup64 10.0.12 image, keeping its proven live bootloader, kernel, initramfs, SFS and OverlayFS mechanism. The previous custom Debian/XFCE image remains available only in `archive/debian-live-build-20261011`.

Add the venvWin capsule manager through an independent Puppy SFS layer. Do not redesign Puppy's live init or replace it with a made-up package profile. More desktop applications, Wine, development tools and firmware can be independent modules after guest-side proof.

The core should stay around the upstream ~791 MiB unless actual measured use justifies additions. The interface can evolve toward a dark Linux-Mint-adjacent appearance without replacing the lightweight Puppy desktop. Packaging a working Python runtime and Wine runners must be verified from inside the live Puppy guest.

**Not yet sellable:** current CI proves an upstream Puppy boot through the overlay switch but has not verified the venvWin desktop or end-to-end Windows capsule workflow. Flash-ready/persistence/reboot, RAM measurement and modules require separate acceptance tests.

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
