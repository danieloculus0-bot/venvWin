# WinUx Portable Debug Checklist

## Purpose

Use this when a build fails, boots weird, or smells like cursed USB smoke.

## 1. Build script sanity

Check:

```bash
bash -n winux-portable/build-iso.sh
bash -n winux-portable/test-iso-qemu.sh
bash -n winux-portable/compare-profiles.sh
```

Expected:

```text
No syntax errors.
```

## 2. Profile build check

Run one at a time:

```bash
WINUX_PROFILE=core ./winux-portable/build-iso.sh
WINUX_PROFILE=standard ./winux-portable/build-iso.sh
WINUX_PROFILE=privacy ./winux-portable/build-iso.sh
```

Expected:

```text
ISO + checksum + manifest created in dist/
```

## 3. Profile comparison

Run:

```bash
./winux-portable/compare-profiles.sh
```

Expected:

```text
size_mb for each built profile
checksum status
size flag
```

## 4. Static ISO inspection

Run:

```bash
xorriso -indev dist/winux-portable-alpha-standard.iso -report_el_torito as_mkisofs
xorriso -indev dist/winux-portable-alpha-standard.iso -find / -name filesystem.squashfs -print
xorriso -indev dist/winux-portable-alpha-standard.iso -find / -name vmlinuz -print
xorriso -indev dist/winux-portable-alpha-standard.iso -find / -name initrd.img -print
```

Expected:

```text
boot info exists
filesystem.squashfs exists
kernel/initrd paths exist
```

## 5. QEMU smoke

Run:

```bash
./winux-portable/test-iso-qemu.sh dist/winux-portable-alpha-standard.iso
```

Expected:

```text
QEMU survives timeout or shows useful boot logs.
```

## 6. First-run validation

Inside booted environment, check:

```bash
which venvwin
venvwin doctor
cat ~/Desktop/WinUx-Quick-Start.txt
cat ~/Desktop/venvwin-doctor.txt
cat ~/.winux-capsule-store
```

Expected:

```text
venvwin exists
quick-start exists
doctor output exists
capsule store selected
```

## 7. Persistence validation

Create a capsule:

```bash
venvwin create "Persistence Test"
venvwin list
```

Reboot with persistence enabled.

Run:

```bash
venvwin list
```

Expected:

```text
Persistence Test still exists.
```

If not, WinUx is running as a disposable goblin and must warn harder.

## 8. EXE/MSI validation

Run:

```bash
venvwin associate
venvwin open ~/Downloads/setup.exe --dry-run
```

Expected:

```text
capsule created or reused
install command produced
state recorded
```

Then test file manager double-click.

Expected:

```text
same route without terminal work
```

## 9. Recovery validation

Run:

```bash
venvwin snapshot create persistence-test --label before-chaos
venvwin reset persistence-test
venvwin inspect persistence-test
```

Expected:

```text
snapshot exists
reset backup exists
capsule metadata still readable
```

## 10. Size tuning questions

If ISO is too large, ask:

- Is Firefox ESR necessary in this profile?
- Is Tor Browser bundled or just launcher-installed?
- Can Wine move out of core?
- Is full XFCE needed or can we keep session/panel/window manager only?
- Did trim hook remove docs/manpages/locales/cache?
- Are we carrying source/dev junk into `/opt/venvwin`?

## 11. Product voice check

Messages should be:

```text
clear first
useful always
mildly feral only after the actual information
```

Bad:

```text
funny but unclear
```

Good:

```text
EXE/MSI handlers are missing. Run `venvwin associate` so double-clicking Windows files stops being bullshit.
```

## Debug rule

Fix one failure class at a time.

Do not shotgun 14 changes and then act surprised when the corpse grows antlers.
