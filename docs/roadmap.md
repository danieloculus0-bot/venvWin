# venvWin Roadmap

## Phase 0: Foundation

Status: in progress

Goals:

- Define WinUx and venvWin boundary
- Build Python CLI skeleton
- Create capsule metadata model
- Create runner profile model
- Generate runner commands without executing them
- Add basic tests and CI

## Phase 1: Local install workflow

Goals:

- Add `venvwin install` command
- Copy installer into capsule history
- Execute selected runner command
- Record installer metadata
- Record exit status
- Add basic logging

## Phase 2: Launcher workflow

Goals:

- Detect installed executable targets
- Record launch targets
- Generate `.desktop` launchers
- Add file association support
- Add icon discovery/capture

## Phase 3: Snapshot and rollback

Goals:

- Snapshot capsule metadata
- Snapshot prefix directory
- Roll back to known-good state
- Add repair/reset commands

## Phase 4: Compatibility profiles

Goals:

- Add app-specific profiles
- Add dependency recipes
- Add runner version pinning
- Add known-good install notes

## Phase 5: WinUx integration

Goals:

- Provide venvWin API/service layer
- Surface capsules in WinUx app launcher
- Add graphical install flow
- Add health/report view

## Phase 6: Fallback backends

Goals:

- Add VM fallback runner
- Surface remote/VM apps like native launchers
- Preserve the same capsule metadata model

## Hard truth

venvWin should not claim magic compatibility. It should claim controlled compatibility: isolated, repairable, profile-driven app environments that feel native from the user's perspective.
