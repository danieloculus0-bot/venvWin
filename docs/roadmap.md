# venvWin / WinUx Roadmap

## Phase 0: Foundation

Status: in progress

Goals:

- Define WinUx and venvWin boundary
- Build Python CLI skeleton
- Create capsule metadata model
- Create runner profile model
- Generate runner commands without executing them
- Add basic tests and CI

## Phase 1: WinUx Portable MVP

Status: first shippable target

Goals:

- Build bootable USB image plan
- Support persistent venvWin capsule storage
- Support optional RAM boot mode
- Use a dark lightweight desktop
- Preinstall venvWin
- Enable EXE/MSI double-click routing into venvWin
- Keep VM fallback out of the normal path
- Aim for a small sellable $8 utility image

Docs:

- `docs/product-plan.md`
- `docs/portable-live-boot.md`

## Phase 2: Local install workflow

Goals:

- Add `venvwin install` command
- Copy installer into capsule history
- Execute selected runner command
- Record installer metadata
- Record exit status
- Add basic logging

## Phase 3: Launcher workflow

Goals:

- Detect installed executable targets
- Record launch targets
- Generate `.desktop` launchers
- Add file association support
- Add icon discovery/capture

## Phase 4: Snapshot and rollback

Goals:

- Snapshot capsule metadata
- Snapshot prefix directory
- Roll back to known-good state
- Add repair/reset commands

## Phase 5: Compatibility profiles

Goals:

- Add app-specific profiles
- Add dependency recipes
- Add runner version pinning
- Add known-good install notes

## Phase 6: venvWin GUI

Goals:

- Build a dark, clean, lightweight graphical capsule manager
- Keep the feel familiar like Linux Mint but more premium
- Stay Jetson friendly and avoid heavyweight UI stacks unless justified
- List capsules as app cards
- Create capsules from EXE/MSI installers
- Run install or dry-run install flows
- Create launchers visually
- Show health, errors, runner profile, and capsule metadata

Design doc: `docs/gui-vision.md`

## Phase 7: WinUx shell integration

Goals:

- Provide venvWin API/service layer
- Surface capsules in WinUx app launcher
- Add graphical install flow
- Add health/report view
- Expose venvWin apps as normal desktop applications

## Phase 8: Fallback backends

Goals:

- Add VM fallback runner only as a last resort
- Surface remote/VM apps like native launchers when needed
- Preserve the same capsule metadata model

## Hard truth

venvWin should not claim magic compatibility. It should claim controlled compatibility: isolated, repairable, profile-driven app environments that feel native from the user's perspective.

WinUx Portable should be the first sellable form because it is smaller, clearer, and easier to test than a full OS replacement.
