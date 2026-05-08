# Puppy Linux 2011 Benchmark for WinUx Portable

## Purpose

This document compares WinUx Portable against the design lessons of Puppy Linux around the 2011 era, especially Lucid Puppy 5.2.5 and Slacko Puppy 5.x.

The goal is not to clone Puppy. The goal is to steal the good survival instincts:

```text
small
fast
portable
persistent
RAM-friendly
first-run friendly
useful on ugly old hardware
```

Then add the WinUx hook:

```text
Double-click Windows EXE/MSI
venvWin creates a capsule
state survives
no normal-path VM circus
```

## Puppy 2011 elements worth matching

### 1. Small bootable ISO

Puppy Lucid 5.2.5 was around 128 MB.

WinUx Portable will not hit that size with XFCE, Wine, Firefox, Tor tooling, and venvWin. That is fine, but the size still matters.

Target:

```text
Alpha: works first
Beta: reduce size
Product: small enough to feel intentional
```

Risk:

```text
If the image feels like random Debian rescue bloat, the product loses its point.
```

## 2. Frugal-style layout

Puppy frugal installs use a small number of compressed system files plus a save layer. That is the right mental model.

WinUx target:

```text
read-only compressed OS image
persistent venvWin capsule store
optional persistent user/session layer
```

Current status:

```text
Partial
```

We have:

- live ISO build plan
- squashfs-style live image through live-build
- venvWin capsule path support
- VENVWIN_HOME support

Missing:

- explicit persistent partition setup
- savefile/savefolder equivalent
- first-boot persistence selector

## 3. Run-in-RAM behavior

Puppy can load the system into RAM in frugal mode when hardware allows.

WinUx target:

```text
toram boot option
OS loads into RAM
capsules stay on persistent storage
```

Current status:

```text
Planned / boot flag added
```

We have:

- `toram` in boot append

Missing:

- tested RAM threshold
- clear disposable-vs-persistent warning
- QEMU/real hardware validation

## 4. Persistent state

Puppy saves changes through savefiles/savefolders.

WinUx target:

```text
Capsules are the app persistence layer.
User chooses where capsule state lives.
System warns if session is disposable.
```

Current status:

```text
Partial
```

We have:

- capsule metadata
- fake Windows prefix
- filesystem mappings
- snapshots
- reset backups
- VENVWIN_HOME

Missing:

- persistent USB partition workflow
- first-run persistence detection
- savefile-style portable storage option

## 5. First-run wizard

Puppy had first-run/browser/setup wizards that made a tiny system feel usable.

WinUx target:

```text
first-run screen
capsule storage status
persistence status
private browser status
runner status
EXE/MSI association status
```

Current status:

```text
Partial
```

We have:

- first-run script
- quick-start text
- doctor output

Missing:

- graphical first-run wizard
- storage selector
- default browser/private browser selector

## 6. Diagnostics and easy fixes

Puppy had point-and-click configuration/update helpers.

WinUx target:

```text
venvwin doctor
repair/reset/snapshot
GUI buttons later
```

Current status:

```text
Good early start
```

We have:

- `venvwin doctor`
- runner check
- EXE/MSI association check
- persistence check
- privacy browser check
- capsule count
- reset command
- snapshot command

Missing:

- GUI doctor
- one-click fix commands
- actual repair recipes

## 7. Package/update convenience

Puppy had QuickPet-style convenience for updates and packages.

WinUx target:

```text
WinUx tool center
install/update runner
install/update Tor Browser
repair EXE handlers
open capsule folder
```

Current status:

```text
Missing
```

This is a future GUI/product feature.

## 8. Browser strategy

Puppy put strong attention on first browser setup.

WinUx target:

```text
normal browser for normal internet
WinUx Private Browser for Tor Browser
honest fallback only
```

Current status:

```text
Partial
```

We have:

- private browser plan
- private browser launcher
- Tor Browser preference
- torsocks + Firefox fallback with warning
- doctor privacy-browser check

Missing:

- real Tor Browser install validation
- first-run browser selector
- DNS/WebRTC leak notes for fallback mode

## 9. Hardware friendliness

Puppy was built for old hardware.

WinUx target:

```text
low idle RAM
fast boot
no bloated background services
Jetson-friendly direction
```

Current status:

```text
Needs measurement
```

Risks:

- XFCE + Wine + Firefox + Tor may be heavier than the product wants
- Jetson/ARM target will need separate work
- live-build alpha may be x86_64-first only

## WinUx Portable minimum proper elements checklist

### Must-have for first alpha ISO

- [x] bootable ISO build script
- [x] QEMU smoke test path
- [x] venvWin CLI included
- [x] fake Windows capsule state
- [x] EXE/MSI association command
- [x] doctor command
- [x] snapshot/reset commands
- [x] product voice
- [x] private browser plan
- [ ] confirmed successful ISO build
- [ ] confirmed QEMU boot
- [ ] confirmed desktop session
- [ ] confirmed first-run file creation

### Must-have for Puppy-style beta

- [ ] persistent USB partition workflow
- [ ] clear savefile/savefolder equivalent
- [ ] first-run graphical setup
- [ ] storage selector for capsules
- [ ] disposable session warning
- [ ] tested toram mode
- [ ] boot size target
- [ ] idle RAM measurement
- [ ] basic GUI capsule manager
- [ ] one-click doctor fixes

### Must-have for $8 product build

- [ ] polished dark lightweight desktop
- [ ] reliable EXE/MSI double-click behavior
- [ ] persistent capsules across reboot
- [ ] private browser launcher works
- [ ] bootable on common PCs
- [ ] quick-start guide
- [ ] known limitations page
- [ ] checksum and flashing instructions
- [ ] license/source notice

## Main conclusion

WinUx Portable is hitting the right conceptual elements, but it is not Puppy-like enough yet in persistence and first-run simplicity.

The next big engineering target should be:

```text
Puppy-style persistence for WinUx Portable
```

Specifically:

```text
read-only live OS
persistent capsule storage
first-run storage selector
clear disposable warning
optional RAM boot
```

That is the survival layer. Without it, WinUx is just a live distro with attitude. With it, WinUx becomes a portable workstation.
