# BEAN OS: Desktop-first master milestone ledger
Updated: 2026-11-15 (UTC)
Status: experiment; not a bootable BEAN OS release.

## Mission / constraints
BEAN OS is BEAN's computer. **BEAN Python Core is the primary resident
system service**, capable of booting and carrying out supported offline tasks
without any LLM or external cloud session. The OS must remain usable if Core
fails. ChatGPT via the existing BEAN plugin is an optional authenticated
human-language translation and remote-operation interface, not the owner
of BEAN's reasoning.

- Desktop first; server edition later.
- Bootable on portable USB, SD (on supported hardware), and installed disks.
- Shared BEAN desktop/Core code across x86-64 and Jetson ARM64 wherever feasible.
- Lightweight composable packages, installed on demand; do not start
  unnecessary modules at boot.
- BEAN may observe, diagnose, operate, verify, recover, and remember real PC
  tasks once a **separately tested** local computer-control adapter is built.
- Preserve BEAN Core memory/history across reboots and connectivity loss.
- No private EZ Fabricating, WMF, or other customer material in public sources.
- Keep OS work in this independent branch, based on the existing venvWin
  experimental branch. Reuse proven tooling selectively, do not rename or
  overwrite the original venvWin product.

## Checklist and acceptance criteria

### M0: Evidence-driven simulated computer (BEAN Core repo)
- [x] Isolated single-step simulation with real BEAN learning journal.
- [x] Blind test after persistence/reopen, >=80% optimal action criterion.
- [x] Five-subsystem virtual desktop; storage, services, network, files, apps.
- [x] Multi-step synthetic repairs and verification; 36/36 completed,
  144/144 repaired, no unnecessary repairs **in the specified fixture**.
- [x] CI test and case-level downloadable evidence in BEAN.
- [ ] Fix active probe selector degeneracy (BEAN issue #380).
- [ ] Add previously unseen fault classes and dependency-coupled goals.
- [ ] Add restart/recovery tests across interrupted simulated sessions.

Source: https://github.com/danieloculus0-bot/BEAN/pull/379
Verified branch CI:
https://github.com/danieloculus0-bot/BEAN/actions/runs/43680313673

### M1: Native BEAN OS system foundation
- [ ] Confirm desktop distro foundation by tested resource budget.
  Candidate x86-64: Debian minimal, with relevant Puppy/vemvWin recipes
  evaluated rather than copied blindly.
- [ ] ARM64 Jetson: use board-supported NVIDIA Jetson Linux image and native
  firmware/drivers; do not assume PC ISO boots on Jetson.
- [ ] Define kernel, bootloader, filesystem layout, persistence, update
  method, package/repository licenses.
- [ ] Establish reproducible x86-64 image build and boot smoke test.
- [ ] Establish supported Jetson ARM64 build/install procedure.

### M1A: Actual GUI navigation by BEAN Core
- [x] Linux X11 graphical test desktop boots under Xvfb + Openbox.
- [x] Existing BEAN GoalCycle invokes a registered OS mouse/keyboard
  control adapter, enumerates real windows and captures screens.
- [x] Demonstrate clicking an application, typing/saving a text document,
  reopening it through file manager, and verifying real file output.
- [x] Verify screenshot artifacts and persistent GoalCycle receipt on CI.
- [ ] Discover and click **unknown** controls through accessibility metadata,
  instead of fixture-specific relative button positions.
- [ ] Implement generic cross-application task plans and recovery after
  navigation failures, including focus and window placement changes.
- [ ] Support Wayland and Jetson-specific graphical sessions.

Evidence: https://github.com/danieloculus0-bot/BEAN/actions/runs/43689023636
Scope: isolated GUI proof on an actual Linux graphical session, not a
bootable BEAN OS or a connection to the owner's computer.

### M2: Functional desktop
- [ ] Working login, desktop session and custom BEAN UI shell.
- [ ] Modern web browser and internet connectivity.
- [ ] File manager, settings, audio, graphics, removable storage.
- [ ] Clean shutdown, restart and recovery.

### M3: BEAN Core as primary resident agent
- [ ] Boot Core with existing memory, reasoning and learning service.
- [ ] Independent supervisor restarts Core after failure.
- [ ] Native observe/act/verify computer-control interface.
- [ ] Memory continuity survives reboot and offline operation.
- [ ] Machine-readable task receipts for every executed action.

### M4: Language translation and remote plugin
- [ ] Use existing BEAN ChatGPT plugin, do not duplicate it.
- [ ] Bridge authenticated plugin to local Core over a narrowly exposed
  secure endpoint or outbound connection.
- [ ] Local lightweight language parsing for offline new instructions,
  with structured commands where no model is needed.
- [ ] Verify degradation and recovery when cloud is disconnected.

### M5: Acceptance and release
- [ ] VM and actual x86-64 boot tests.
- [ ] Physical Jetson Orin Nano test; GPU inference independently verified.
- [ ] Stress, power-loss, memory, update and crash-recovery tests.
- [ ] Publish BEAN OS Alpha image/checksum and reproducible build provenance.

### Deferred
- [ ] Server edition sharing Core and management interfaces.

## Evidence policy
"Planned" is not "implemented"; simulated results cannot be described as
physical PC control, general intelligence, an OS boot, or an independently
authenticated outside benchmark. Retain failures and unknowns. This file is
the stable project checklist to revise as each milestone earns evidence.
