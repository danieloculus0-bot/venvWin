# WinUx Phone Build Status

## Current verdict

```text
NOT FLASH READY
```

## What must happen before Daniel flashes a USB

The GitHub Actions workflow must complete successfully:

```text
flash-ready-standard
```

It must upload this artifact bundle:

```text
winux-portable-flash-ready-standard
```

That bundle must contain:

```text
winux-portable-alpha-standard.iso
winux-portable-alpha-standard.iso.sha256
winux-portable-alpha-standard-manifest.txt
winux-flash-ready-verdict.txt
```

The verdict file must say:

```text
status=FLASH_READY
```

## What the workflow checks

```text
pre-ISO readiness
standard ISO build
checksum generation
manifest generation
static ISO inspection
QEMU boot smoke
flash-ready verdict
```

## What first boot should show

```text
WinUx desktop
WinUx First Boot GUI
WinUx Dashboard at http://127.0.0.1:8787
WinUx-Quick-Start.txt
WinUx-First-Boot-Proof.txt
WinUx-Dashboard.txt
WinUx-First-Boot-Checklist.txt
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

The next build target is not more feature creep.

It is proving the standard ISO gate.
