# Run venvWin Portable Flash-Ready Build From Phone

## Current verdict

```text
NOT FLASH READY
```

## Phone steps

1. Open GitHub on phone.
2. Go to repo:

```text
danieloculus0-bot/venvWin
```

3. Tap:

```text
Actions
```

4. Open workflow:

```text
flash-ready-standard
```

5. Tap:

```text
Run workflow
```

6. Use branch:

```text
main
```

7. Wait for the run to finish.

## Success condition

The run must complete green and upload artifact:

```text
venvwin-portable-flash-ready-standard
```

Inside that artifact must be:

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

## Failure condition

If the workflow fails, do not flash anything.

The failure log will show one of these likely stages:

```text
pre-ISO readiness gate
build standard ISO
static ISO inspection
QEMU boot smoke
artifact upload
```

## Flash rule

Only flash the USB after the verdict file says:

```text
status=FLASH_READY
```

Anything else is not ready.
