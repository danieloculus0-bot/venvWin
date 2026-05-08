# WinUx Product Doctrine

## Core rule

WinUx is not LinuxDIY.

WinUx is not an alacarte distro stuffed with every clever package we can find.

WinUx is a working, neat, lightweight Linux-based OS wrapper for venvWin.

```text
Everything needed.
Nothing extra.
```

## What WinUx is

WinUx is:

- bootable
- clean
- dark
- lightweight
- portable
- leave-no-trace by default
- focused on Windows-app capsules
- useful on first boot
- readable by normal users
- repairable by technical users

## What WinUx is not

WinUx is not:

- a bloated rescue distro
- a pile of random tools
- a full desktop replacement for every possible user
- a Linux hobby playground
- a 9 GB monster ISO
- a package buffet
- a generic privacy distro
- a generic hacking distro

## Product focus

The core product must only include what supports the mission:

```text
Boot cleanly.
Protect the host.
Run/manage venvWin capsules.
Show storage state.
Recover broken capsules.
Provide a private browser path.
Offer a phone-visible dashboard.
Get out of the way.
```

## Required core components

Keep:

- lightweight desktop shell
- file manager
- terminal
- network manager
- venvWin runtime
- first-boot GUI
- dashboard
- doctor/check tools
- EXE/MSI handlers
- persistence tooling
- minimum browser/private browser path
- minimum runtime dependencies for selected compatibility profiles

## Avoid by default

Do not include by default:

- office suites
- games
- media bundles
- dev toolchains unless required
- heavy IDEs
- random rescue utilities
- multiple browsers
- multiple desktops
- redundant file managers
- package-manager clutter
- broad forensic/security toolsets
- novelty apps

## Dependency rule

Dependencies are allowed only when tied to a purpose:

```text
Windows app execution
capsule repair
first boot
dashboard
networking
storage safety
privacy browser path
```

If a package does not serve one of those, it does not belong in core WinUx.

## Edition rule

Future editions may exist.

### WinUx Portable

Core product.

Lean. Useful. Sellable. Minimal.

### WinUx Maker

Possible future edition with maker tools and 3D workflows.

### SwissArmyLinux

Possible future fork/edition.

Broad utility distro. More tools. More bloat allowed intentionally.

SwissArmyLinux must not contaminate core WinUx.

## Size rule

Small is a feature.

Puppy-style discipline matters:

```text
fast boot
low RAM
USB friendly
older machine friendly
Jetson friendly later
```

The target is not to be as tiny as Puppy at the cost of function.

The target is to keep only what the product needs.

## User experience rule

On first boot, the user should see:

```text
WinUx is running.
venvWin is ready or tells me what is missing.
My app state location is visible.
Host write risk is visible.
I can run or install a Windows app.
I can recover if it breaks.
```

Anything beyond that must earn its place.

## Summary

WinUx is the clean OS wrapper.

venvWin is the method.

The core product must stay lean enough to trust, boot, sell, and use.
