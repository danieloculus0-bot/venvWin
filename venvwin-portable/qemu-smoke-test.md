# venvWin Portable QEMU smoke and BEAN Bridge evidence

The canonical build is `.github/workflows/flash-ready-standard.yml`. It uses
`venvwin-portable/build-in-bookworm.sh`, building Debian Bookworm inside a
Docker container with GRUB BIOS/EFI boot files.

## Actual acceptance

The job must complete the Python tests, generate an ISO/checksum/manifest,
verify the extracted SquashFS contents and boot the **actual ISO** with QEMU.

A systemd one-shot probe **inside the guest**, enabled at boot, waits for:
- a running XFCE desktop session for the live user
- first-run completion and a desktop proof file
- an HTTP response from the local dashboard
- a functioning venvWin CLI entrypoint

Only when all checks succeed does it write the literal serial markers:
`BEAN_GUEST_FIRST_RUN_PASS` and `BEAN_GUEST_READY`.

The parent host checks the serial log for both markers. QEMU remaining alive
for 270 seconds **does not count as success**. Missing markers, an aborted ISO
build or an absent checksum is failure.

## BEAN AI Bridge laboratory

The workflow checks out the pinned BEAN AI Bridge smoke lab, constructs a
machine-evidence report and processes it with `ezbean.smoke_lab`.

Four required ISO checks:
- preflight package installation
- static boot structure and built ISO
- in-VM guest readiness
- in-VM first-run readiness

BEAN replays the evidence assessment five times against the append-only
SQLite ledger and rejects missing proofs. Its ratio is evidence coverage,
not a confidence probability.

Actions uploads ISO files and the BEAN report, receipt, ledger, and QEMU
serial evidence even on build failure. A failed build will *never* be
silently promoted to `status=FLASH_READY`.

## Puppy Linux comparison

This builds a Debian `filesystem.squashfs` image, rather than copying
Puppy's exact names. The frugal Puppy reference is still useful: compressed
OS, separate save layer, and a kernel/initramfs managed by the bootloader.

USB persistence across a full reboot is **a separate release gate**. One
successful desktop boot proves Alpha readiness only, not product readiness.
