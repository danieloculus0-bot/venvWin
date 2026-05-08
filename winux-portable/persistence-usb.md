# WinUx Portable USB Persistence

## Purpose

This is the Puppy-style survival trick:

```text
The OS can be read-only, live, or loaded into RAM.
The venvWin capsule store must survive reboot.
```

## Recommended USB layout

```text
Partition 1: WINUXBOOT
  bootable ISO / live image

Partition 2: WINUXDATA
  writable storage
  contains WinUx-Capsules/
```

## Capsule path

WinUx looks for capsule storage in this order:

```text
/run/live/persistence/WinUx-Capsules
/persistence/WinUx-Capsules
/mnt/winux-persistence/WinUx-Capsules
/media/<user>/WINUXDATA/WinUx-Capsules
/media/<user>/WinUxData/WinUx-Capsules
~/WinUx-Capsules
```

The last one is fallback. It may be disposable unless the live system has persistence enabled.

## Recommended label

Use this label for the writable partition:

```text
WINUXDATA
```

Then create:

```text
WinUx-Capsules/
```

## Linux setup example

Warning: this can wipe a USB drive if you target the wrong device. Do not be stupid with `sdX`.

```bash
sudo mkfs.ext4 -L WINUXDATA /dev/sdX2
sudo mkdir -p /mnt/winuxdata
sudo mount /dev/disk/by-label/WINUXDATA /mnt/winuxdata
sudo mkdir -p /mnt/winuxdata/WinUx-Capsules
sudo chown -R 1000:1000 /mnt/winuxdata/WinUx-Capsules
sync
```

## Disposable warning

If WinUx falls back to:

```text
~/WinUx-Capsules
```

and the home folder is not persistent, anything installed may vanish after reboot.

That is acceptable for testing and absolute bullshit for real use.

## Product target

The $8 build should eventually include a first-run storage selector:

```text
Use detected WINUXDATA partition
Create capsule store
Use existing capsule store
Run disposable test session
```

## Rule

Never let RAM mode eat app state.

`toram` should speed up the OS. It should not turn the capsule store into a pumpkin at reboot.
