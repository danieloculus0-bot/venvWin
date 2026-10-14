# venvWin — Locked Windows-First Desktop Requirements

**Design decision (2026-10-13): MAXIMUM WINDOWS APPLICATION COMPATIBILITY, NOT MINIMUM ISO SIZE.**

## Product objective

venvWin is a genuine 64-bit Puppy Linux desktop that makes supported Windows software feel native to the Linux desktop using Wine. The reference to Parallels' Coherence mode describes the *seamless per-application experience only*, **not** remote desktop, a full Windows virtual machine, the macOS Dock, or a macOS skin.

### User-facing acceptance criteria

1. A normal user double-clicks a compatible Windows EXE and receives a real application window on Puppy's desktop, without opening a second operating-system desktop or Wine terminal/configuration screen by default.
2. Compatible MSI/EXE installers actually run with honest progress/errors. A successful installer creates a normal app launcher. Do not claim compatibility merely because a click handler or a launcher exists.
3. Window minimize/maximize, ordinary taskbar entries, Alt-Tab, desktop focus, clipboard and file open/save behavior operate naturally when supported by Wine and the window manager.
4. The same taskbar/application menu launches both Windows and Linux applications. Preserve existing native Puppy desktop facilities; a drawn imitation taskbar inside a first-run window does NOT satisfy this criterion.
5. The first-run Control Center is for optional configuration and diagnostics; do not require opening it every time the user runs an application. No fake controls, inert buttons or placeholder dashboards.
6. Keep the established premium dark Linux Mint-adjacent desktop, charcoal background, familiar Windows-style bottom panel, restrained orange #ff8a00 accent, and original project identity. Do not invent a replacement logo or theme.
7. Preserve real venvWin capsule functionality, separate Wine prefixes, application launcher and installation state, user-controlled persistence, and genuine error reporting.
8. Prove Windows application execution in an actual graphical Puppy guest, both PE32 and PE32+, before any claim of broad Windows support. MSI, file associations, launcher behavior, clipboard, window manager, and reboot persistence require their OWN subsequent proofs.

### Technical selection

- Maximize functional Windows application compatibility rather than minimize ISO footprint. The OS must be genuine **x86-64 Puppy**, with a version-matched **64-bit Wine that can run 64-bit Windows applications and, where supported, 32-bit Windows applications (WoW64/multilib)**.
- BookwormPup64 10.0.8 + archived Wine 9.19 is the **currently running isolated compatibility test**, not a final proven winner.
- BookwormPup64 10.0.12 is an **additional modern candidate**; its Wine package compatibility and actual 32/64 guest behavior must be demonstrated before selection. Do not assume Wine 8.0 SFS from BookwormPup64 <=10.0.7 works on 10.0.8 or newer.
- Legacy Lucid Puppy 5.2.8 is a useful compact architecture reference but its historic 32-bit Wine does not meet the modern 64-bit application requirement.
- No legacy Debian live-build rebuild, and no untested OS/runtime substitutions.
- Do not merge to main or publish a release without actual guest-origin proof.

### Deliberately out of current scope

**Windows NTFS filesystem integration** remains an **Experimental Archive**, see [windows-filesystem-integration.md](experimental-archive/windows-filesystem-integration.md). Do NOT implement host Windows filesystem mounting, native DLL redirection, Windows registry reuse, or automatic Windows partition writes until the user separately authorizes that experimental work.

### Test definitions / honest progress

- Source syntax, unit tests, and package hashes mean SOURCE/ARTIFACT VERIFIED, not a boot pass.
- Real guest startup + version-matched Wine executable + wineboot prefix + independent Windows PE32 and PE32+ execution with guest-origin receipts mean BASIC WINDOWS EXECUTION PASS.
- Seamless window UX requires guest-origin observations of taskbar, focus/Alt-Tab, minimize/maximize and clipboard; Windows MSI installation and persistence remain separate required gates.
- If a test fails, record the actual failure and keep the last working combination; do not upgrade, downgrade, or paint status green without measured evidence.

**Plain English:** EXE/MSI in, working application out; Windows programs should feel like native Puppy programs. That is the product.
