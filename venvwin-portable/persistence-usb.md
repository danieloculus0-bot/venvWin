# venvWin Portable USB Persistence

## Purpose

This is the Puppy-style survival trick:

```text
The OS can be read-only, live, or loaded into RAM.
The venvWin capsule store must survive reboot.
```

## Recommended USB layout

```text
Partition 1: VENVWINBOOT
  bootable ISO / live image

Partition 2: VENVWINDATA
  writable storage
  contains venvWin-Capsules/
```

## Capsule path

venvWin looks for capsule storage in this order:

```text
/run/live/persistence/venvWin-Capsules
/persistence/venvWin-Capsules
/mnt/venvwin-persistence/venvWin-Capsules
/media/<user>/VENVWINDATA/venvWin-Capsules
/media/<user>/venvWinData/venvWin-Capsules
~/venvWin-Capsules
```

The last one is fallback. It may be disposable unless the live system has persistence enabled.

## Recommended label

Use this label for the writable partition:

```text
VENVWINDATA
```

Then create:

```text
venvWin-Capsules/
```

## Linux setup example

Warning: this can wipe a USB drive if you target the wrong device. Do not be stupid with `sdX`.

```bash
sudo mkfs.ext4 -L VENVWINDATA /dev/sdX2
sudo mkdir -p /mnt/venvwindata
sudo mount /dev/disk/by-label/VENVWINDATA /mnt/venvwindata
sudo mkdir -p /mnt/venvwindata/venvWin-Capsules
sudo chown -R 1000:1000 /mnt/venvwindata/venvWin-Capsules
sync
```

## Disposable warning

If venvWin falls back to:

```text
~/venvWin-Capsules
```

and the home folder is not persistent, anything installed may vanish after reboot.

That is acceptable for testing and absolute bullshit for real use.

## Product target

The $8 build should eventually include a first-run storage selector:

```text
Use detected VENVWINDATA partition
Create capsule store
Use existing capsule store
Run disposable test session
```

## Rule

Never let RAM mode eat app state.

`toram` should speed up the OS. It should not turn the capsule store into a pumpkin at reboot.
