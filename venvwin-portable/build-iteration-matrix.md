# venvWin Portable Build Iteration Matrix

## Purpose

venvWin Portable needs a repeatable comparison loop so each build gets judged against the right target instead of vibes, caffeine, and goblin prophecy.

The benchmark is Puppy-style portable utility design:

```text
small enough to feel intentional
fast enough to feel alive
persistent enough to trust
simple enough for normal people
useful enough to sell
```

## Build profiles

| Profile | Purpose | Expected size | Product role | Main risk |
|---|---:|---:|---|---|
| core | smallest useful venvWin shell | lowest | rescue/dev/minimal base | no Windows runner if Wine omitted |
| standard | first $8 product target | medium | sellable default | size creep |
| privacy | privacy-heavy build | highest | privacy edition / future add-on | browser/Tor bloat |

## Current target priorities

### Core profile

Must prove:

- boots
- opens desktop
- runs `venvwin doctor`
- detects persistence
- creates capsule metadata
- explains missing runner cleanly

Core is allowed to warn that Windows apps cannot launch if the runner is absent.

### Standard profile

Must prove:

- boots
- runs venvWin
- includes Wine-compatible runner
- routes EXE/MSI to venvWin
- persists capsule state
- provides recovery tools
- includes private-browser path if size remains sane

Standard is the first commercial target.

### Privacy profile

Must prove:

- everything Standard proves
- private browser launcher works
- Tor Browser or honest fallback is available
- privacy claims stay honest

Privacy is not allowed to become fake anonymity marketing bullshit.

## Scoring model

Each build gets scored 0-2 per category.

```text
0 = missing / broken
1 = partial / ugly / manual workaround
2 = working / documented / user-visible
```

| Category | Core | Standard | Privacy | Notes |
|---|---:|---:|---:|---|
| ISO builds |  |  |  | CI/local build result |
| ISO boots in QEMU |  |  |  | headless smoke first, GUI later |
| Desktop reaches usable state |  |  |  | visual proof later |
| Size within target |  |  |  | compare against size-budget.md |
| venvWin CLI works |  |  |  | `venvwin doctor`, `init`, `create` |
| Persistence detected |  |  |  | store selected correctly |
| Disposable warning works |  |  |  | user warned when state may vanish |
| EXE/MSI handler present |  |  |  | `venvwin associate` |
| Runner available |  |  |  | expected false/warn on core if runner omitted |
| Snapshot/reset available |  |  |  | recovery layer |
| Private browser status |  |  |  | honest check, no fake claims |
| First-run output useful |  |  |  | Quick Start + doctor output |
| Product voice controlled |  |  |  | useful, not clown software |

## Iteration loop

Every build iteration should follow this loop:

```text
1. Build selected profile
2. Record ISO size + checksum
3. Inspect ISO boot structure
4. QEMU smoke test
5. Capture manifest
6. Compare against previous profile/build
7. Fix one major failure class
8. Repeat
```

## Failure classes

### Build failure

Likely causes:

- unavailable package
- live-build config issue
- hook error
- repo mismatch
- chroot cleanup too aggressive

### Boot failure

Likely causes:

- bad bootloader package
- missing kernel/initrd path
- broken live-boot config
- ISO hybrid issue

### Desktop failure

Likely causes:

- LightDM/session mismatch
- missing XFCE component
- autostart issue
- user/session config issue

### venvWin failure

Likely causes:

- PYTHONPATH not set
- package files not copied
- CLI wrapper broken
- missing Python dependency

### Persistence failure

Likely causes:

- wrong mount path
- USB partition not mounted
- label mismatch
- permissions issue
- fallback to disposable home folder

### EXE/MSI handler failure

Likely causes:

- desktop file not installed
- MIME database not updated
- desktop environment did not set default handler
- handler exists but command path broken

## Product-ready gates

### Alpha gate

- ISO builds
- QEMU smoke survives
- venvWin command exists
- doctor runs
- first-run creates files

### Beta gate

- desktop boot validated visually
- persistence survives reboot
- EXE/MSI double-click routes to venvWin
- reset/snapshot works inside live environment
- size is not embarrassing

### $8 gate

- standard profile boots on multiple PCs
- clear flashing instructions
- persistent capsule store guide
- known limitations page
- checksum included
- no fake compatibility claims
- no fake privacy claims

## Current best next fixes

1. first-run storage selector
2. build all three profiles and compare sizes
3. validate QEMU boot logs
4. add GUI-lite first-run screen later
5. trim Standard profile without killing the product hook

## Rule

If the build gets smaller but loses the reason venvWin exists, that is not optimization. That is self-sabotage with a file-size fetish.
