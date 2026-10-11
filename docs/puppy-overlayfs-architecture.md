# venvWin native Puppy filesystem architecture

**Platform:** authentic BookwormPup64 10.0.12, based on the established Puppy live boot environment. The previous custom Debian `live-build` implementation is preserved on the `archive/debian-live-build-20261011` branch, not used as the new OS.

## Verified facts vs product requirements

The [upstream-only QEMU diagnostic](https://github.com/danieloculus0-bot/venvWin/actions/runs/38168125218) captured actual frame data. Its ~75-second frame visibly states:
- Puppy Linux 6.1.148 started;
- Puppy copied its main, adrv, bdrv, fdrv, zdrv and kbuild SFS layers to RAM;
- Puppy completed `switch_root` into its overlay filesystem.

This **visual boot log is not yet independent inspection of in-guest `/proc/self/mountinfo` or a measurement of free memory**, and was gathered from the unmodified upstream ISO. The [first native venvWin remaster](https://github.com/danieloculus0-bot/venvWin/actions/runs/38166940199) was ~791 MiB and preserved boot records, but did not produce the required guest-origin application/desktop proof. The subsequent corrected native boot attempt is a separate CI gate.

## Genuine native Puppy structure

```text
Authentic BookwormPup64 10.0.12 live ISO
  original bootloader, kernel, initrd / native init logic
  puppy_dpupbw64_10.0.12.sfs     original main read-only OS
  adrv/bdrv/fdrv/zdrv/*          original native upstream SFS components
  ydrv_dpupbw64_10.0.12.sfs      extra venvWin app layer (our addition)
    /opt/venvwin/src/venvwin     existing Python capsule manager
    /usr/local/bin/venvwin       launcher requiring Python 3.10+
    /root/Startup/...           desktop-origin evidence probe
  Puppy writable live overlay    actual mount requires guest proof
```

Puppy's real working mount locations and actual overlay upperdir/workdir must be read from the live system (e.g. `/proc/self/mountinfo`). Never claim imaginary `/initrd/venvwin/*` directories are mounted.

The new OS must run without writing to the host's installed hard disk. QEMU core proof attaches **only a read-only ISO CD-ROM and no virtual hard disk/network**. Future save tests deliberately attach dedicated disposable save media; those tests must prove user choice and unchanged host state.

## Still-required runtime experiments

1. Observe a venvWin desktop session and verify guest-origin `/proc/self/mountinfo` for true OverlayFS and its writable upper layer.
2. Measure compressed SFS bytes, actual copied RAM bytes and remaining free RAM; distinguish default copy from user-selected `pfix=copy`/`pfix=nocopy` modes.
3. Test `pfix=ram` or equivalent leave-no-save mode, then explicitly choose a USB-owned savefile/savefolder and verify a known unique marker **after reboot**.
4. Independently mount and unmount a non-core application SFS, verify actual binary execution, record hashes and ensure no modification of the upstream Puppy base.
5. Package a compatible Wine runner module, route a real .exe/.msi installer through venvWin, verify isolated capsule state, reset, backup, and repeat behavior **inside Puppy**, not on an unrelated Ubuntu CI runner.
6. Re-run the six BEAN Puppy gates and separately test the full end-to-end product experience. A verified ISO is not automatically a verified or saleable product.

All acceptance evidence must include exact image SHA-256, executed boot mode, kernel version, guest-origin logs, observed mounts, and enough reproducible steps to rerun independently.

No automatic rewrite of upstream Puppy kernel/initramfs is necessary. Keep the authentic live architecture and add small, independently verifiable modules.
