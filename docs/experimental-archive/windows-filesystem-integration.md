# Experimental Archive: Windows Filesystem Integration

**Status: ARCHIVED EXPERIMENT. Not part of the active venvWin build, boot process, or acceptance criteria.**

## Hypothesis, preserved without implementation

A lightweight native Puppy Linux desktop could provide local application launch by reading an already installed Windows NTFS filesystem. Wine would provide Windows API compatibility; the existing partition could provide application binaries, files, and resources, without copying an entire Windows installation into an ISO or RAM. Applications would appear directly in the Puppy graphical desktop rather than through Remote Desktop.

## Technical uncertainty, not established capability

- Linux reading an NTFS partition does not execute Win32/Win64 PE binaries without Wine or equivalent support.
- Windows system DLLs, the registry, services, drivers, and kernel interfaces cannot generally be reused as an operating Windows execution environment merely by mounting the partition.
- Existing installed programs might depend on Windows-specific registry keys, services, machine configuration, hardware, copy protection, or other context unavailable to Wine.
- A safely mounted read-only Windows volume should be separated from independent, writable Wine prefixes. Hibernated or Fast Startup NTFS volumes may be unsafe to write.
- The Windows partition may be absent, BitLocker locked, inaccessible, or in an incompatible state; those cases require honest failure handling, not fictitious access.
- RAM operation, permission boundaries, security, writeback, persistence, and compatibility are unknown until proven in a live guest.

## Strict sequencing

1. **Active scope now:** native 64-bit Puppy, existing independently packaged 64-bit Wine, actual in-guest Wine init and 32/64 Windows EXE execution.
2. **Do not implement this Windows filesystem hypothesis yet.** No mounting, scanning, DLL redirection, registry reuse, launcher wiring, or NTFS writes in the current branch.
3. Return to this archive only after baseline Wine actually works, and only after an explicit user instruction to resume.
4. Keep guest-origin evidence independent of ISO checksums, build success, VNC screenshots, source tests, or host-side wine execution.

This archive preserves the user's idea, not a validated design or release feature.
