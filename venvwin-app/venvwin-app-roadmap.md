# venvWin App Roadmap

## Concept

venvWin App is the lighter, more realistic mobile/desktop path before trying to become a full phone OS.

Instead of booting an entire venvWin operating system, the app provides the venvWin control layer:

```text
capsule manager
storage status
leave-no-trace visibility
doctor/repair actions
private browser launcher
Windows-app compatibility profiles
remote/portable venvWin session control
```

## Why this matters

A full phone OS has hard problems:

```text
bootloaders
kernels
drivers
cell modem support
battery/power management
camera/audio stacks
ARM vs x86 Windows compatibility
```

A venvWin App avoids most of that at first.

## Product split

### venvWin Portable

Bootable USB live OS.

```text
Best for PCs
Best first $8 product
Full portable environment
Capsules live on USB
```

### venvWin App

Control and management app.

```text
Best for phones/tablets/desktops
Shows capsule state
Runs doctor checks
Manages storage
Can control a venvWin machine remotely later
Can become the UI shell for venvWin Mobile later
```

### venvWin Mobile OS

Future phone/tablet OS target.

```text
Hardest path
Requires hardware-specific work
Only realistic after the app and portable OS mature
```

## venvWin App first version

Minimum useful version:

- dark premium UI
- storage status screen
- leave-no-trace badge
- host-risk warning
- capsule list
- doctor results
- repair/reset/snapshot buttons
- app profile browser
- quick-start instructions

## Possible app targets

### Desktop app

Most realistic first.

Options:

```text
Python Tkinter/PySide
lightweight web UI
Tauri later if needed
```

Purpose:

```text
local venvWin control panel
first-run wizard
capsule manager
```

### Android app

Good later target.

Purpose:

```text
control a venvWin USB/box remotely
show status
manage profiles
download docs
maybe prepare USB instructions
```

### Web app

Very practical.

Purpose:

```text
venvWin local dashboard
runs on the live OS
phone can connect over LAN
no install needed on phone
```

## Best near-term path

Build a local venvWin dashboard served from the live OS:

```text
http://venvwin.local:8787
```

Phone/tablet/browser can open it.

This gives a phone-like app experience without needing to become a phone OS yet.

## Product idea

venvWin App can become the pretty face of the project:

```text
storage
capsules
doctor
repair
profiles
privacy
updates
```

The OS does the hard work. The app makes it feel beautiful and controlled.

## Rule

Do not make the app just another settings panel.

It should answer the user’s first questions immediately:

```text
Where is my app state going?
Am I writing to the host?
What capsules exist?
What is broken?
How do I fix it?
Can I run this Windows app?
```

## Conclusion

venvWin App is likely the best bridge between venvWin Portable and a future venvWin Mobile OS.

It is cheaper, safer, easier to polish, and much more realistic as an early product.
