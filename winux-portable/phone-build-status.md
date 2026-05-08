# venvWin Portable Phone Build Status

## Current verdict

```text
NOT FLASH READY
```

## Public name

```text
venvWin Portable
```

Internal codename:

```text
WinUx
```

## Latest build attempt

```text
status=REQUESTED
path=GitHub Actions push trigger
workflow=flash-ready-standard
reason=actual flash-ready gate attempt after repo contract sweep
```

## What must happen before Daniel flashes a USB

The GitHub Actions workflow must complete successfully:

```text
flash-ready-standard
```

It must upload this artifact bundle:

```text
venvwin-portable-flash-ready-standard
```

That bundle must contain:

```text
venvwin-portable-alpha-standard.iso
venvwin-portable-alpha-standard.iso.sha256
venvwin-portable-alpha-standard-manifest.txt
venvwin-flash-ready-verdict.txt
```

The verdict file must say:

```text
status=FLASH_READY
```

## What the workflow checks

```text
pre-ISO readiness
public branding audit
Python tests
standard ISO build
checksum generation
manifest generation
filesystem.squashfs extraction
squashfs static inspection
QEMU boot smoke
flash-ready verdict
```

## What first boot should show

```text
venvWin Portable desktop
venvWin Portable First Boot GUI
venvWin Portable Dashboard at http://127.0.0.1:8787
venvWin-Quick-Start.txt
venvWin-First-Boot-Proof.txt
venvWin-Dashboard.txt
venvWin-First-Boot-Checklist.txt
venvWin-First-Boot.desktop
venvWin-Dashboard.desktop
venvWin-Capsules.desktop
venvWin-Doctor.desktop
venvWin-Private-Browser.desktop
venvwin doctor output
storage status output
capsule storage path
leave-no-trace status
host-risk status
```

## Phone dashboard behavior

Default dashboard:

```text
local-only
http://127.0.0.1:8787
```

LAN dashboard:

```text
explicit token required
started manually with winux-dashboard-lan
```

## Rules

Do not flash until verdict is `FLASH_READY`.

Do not call it a product until USB persistence proves:

```text
create capsule
reboot
capsule still exists
```

## Next build target

The next build target is no longer feature creep.

It is the actual `flash-ready-standard` workflow run.
