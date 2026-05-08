# venvWin / venvWin GUI Vision

## Design target

The GUI should feel familiar like Linux Mint, but darker, cleaner, more premium, and less cluttered.

The vibe is:

- dark mode first
- lightweight as hell
- Jetson friendly
- clean desktop utility, not bloated control panel
- premium industrial polish
- simple enough for normal users
- powerful enough for builders and tinkerers

## Product split

```text
venvWin Shell
  Desktop wrapper
  Start/menu experience
  system settings
  app launcher
  visual identity

venvWin GUI
  app capsule manager
  install flow
  launcher creation
  compatibility status
  repair/reset/snapshot controls
```

The first GUI should be a venvWin capsule manager. The full venvWin shell comes later.

## UI principles

1. Keep it light

No heavy Electron shell for the first pass unless there is no better option. Prefer native or near-native Linux tooling.

Candidate stacks:

- GTK4 with Python
- Qt/PySide6 if packaging is acceptable
- lightweight webview only if needed

2. Make capsules visual

Each app capsule should appear as a card:

- app name
- runner profile
- install status
- launch buttons
- repair/reset button
- snapshot state
- warning/error state

3. Make the install flow idiot-resistant

The user flow should be:

```text
Choose EXE/MSI
Pick app name
Pick profile or recommended default
Create capsule
Run installer
Pick launch target
Done
```

No prefix archaeology. No registry spelunking. No terminal hell unless the user asks for it.

4. Jetson friendly

The GUI must avoid unnecessary background services, animations, memory-heavy renderers, and GPU assumptions.

Target behavior:

- boots fast
- opens fast
- works without compositing tricks
- usable on low-power ARM Linux systems
- no giant dependency stack unless justified

5. Premium dark visual direction

Default theme:

- charcoal / near-black base
- soft gray panels
- muted blue accent
- crisp white text
- subtle borders
- no neon gamer bullshit
- no candy-colored toy controls

Inspired by:

- Linux Mint familiarity
- high-end equipment UI
- clean industrial dashboard controls

## First GUI MVP

The first graphical MVP should do five things:

1. list capsules
2. create a capsule
3. run installer or dry-run install
4. create launcher
5. inspect capsule metadata

Everything else can wait.

## Future venvWin shell goals

venvWin should eventually expose venvWin capsules as normal apps:

- searchable launcher entries
- right-click repair/reset
- compatibility status badges
- installed Windows app library
- optional app store/profile recipes
- simple system settings panel

## Hard rule

The GUI cannot become a bloated science project. The moment it gets heavy, confusing, or slow, it is failing the product.
