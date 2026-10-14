# venvWin — Slacko-style application optimization (locked user choices)

**Scope:** BookwormPup64 x86-64 only; preserve the genuine Puppy kernel, firmware, bootloader, SFS/OverlayFS boot and persistence behavior. Preserve separate 64-bit Wine runner and any 32-bit libraries necessary for WoW64. No NTFS-host filesystem experiment.

## Strict trimming boundary — user's final decision

**ONLY THE BLOAT.** Preserve functional Puppy programs and small useful utilities, even if they are not essential to the core Windows-first experience. Do not remove an app because its category sounds nonessential or because it is rarely used.

Safe targets are narrowly defined: redundant players after choosing one working replacement; audio/video editors explicitly declined by the user; standalone packaged games; and obsolete or duplicate menu entries. Preserve functional recording, troubleshooting, diagnostics, PDF, file/archive, storage, backup, network, terminal, code/text editor, security, printing/scanning, media playback, office, browser and software-management utilities. Do not prune a tool merely because one person's workflow does not need it.

If removal breaks any default handler, dependency, file association, package database, boot behavior, Wine, or everyday utility, undo it. In ambiguous cases **keep the app**. Compressed megabytes saved are secondary to functionality. No forced browser/package-manager/network downgrades.

## Approved app selection (2026-10-13)

| Class | Decision | Implementation rule |
| --- | --- | --- |
| Spreadsheet | **KEEP** Gnumeric, modern Bookworm-compatible build; must open, edit and save basic XLS/XLSX files | Prefer shipped package. If missing, use compatible Bookworm package and measure dependencies. Do not use old Slacko binary. |
| Word processor | **KEEP** AbiWord, modern Bookworm-compatible build, for basic DOC/DOCX/ODT editing | Prefer shipped build; same ABI rule. |
| Browser | **ONE** GUI browser; prefer Firefox ESR for robustness, Chromium if lighter *in real measurement* | Keep browser plus CA certificates/TLS, network stack, download integration; no browserless default. |
| Network | **KEEP** GUI Wi-Fi, Ethernet, IP/DHCP, DNS, VPN/client configuration where supported | Protect Network Wizard/Frisbee-style controls, DHCP, resolvers, wireless firmware; never cut network libraries. |
| Email/chat | Optional / removable duplicates | Keep networking GUI and protocols, so mail isn't required as a baked-in client. |
| Audio/video | **REMOVE standalone audio/video editing suites**, keep playback, conversion or recording utilities where useful, volume/mixer and codecs needed by Wine | Do not confuse a useful recorder with an editor. Never remove PipeWire/ALSA or shared ffmpeg codecs to save space. |
| Image | **KEEP** tiny mtPaint if included and basic image viewer | Working Puppy tradition, minimal size. |
| Games/demos | REMOVE standalone bundled games | No shared UI, menu framework or system-library deletion. |
| Developer SDK | Keep separate devx/kernel-source SFS, not bundled in main ISO | Original Puppy modular loading intact. |
| Printer/scanner | Keep practical client functionality unless later opted out | Do not remove system print APIs Wine apps might call. |
| Desktop | **KEEP** JWM, ROX-Filer, actual bottom panel, file associations | No fake GUI/taskbar. |
| Themes | One approved dark charcoal/orange venvWin design plus accessibility fallback | Preserve essential GTK/icon libraries. |

## Safety and evidence gates

1. Inventory **actual original ISO** and read the included compressed system packages before naming exact removable files. Current official 10.0.12 ISO SHA256 `ae65f6e6d70a96f48bdbb291c2426f8a2fd77a73692e149e81a5eecb6fe7509f`.
2. Package-removal candidate is NOT an authorization to delete shared libraries. Never prune `/lib`, `/usr/lib`, `/usr/lib32`, `/usr/lib64`, `/etc`, kernel/firmware modules, init, Wine, Python dependencies, Puppy `/root/.packages` database, desktop server or networking stack via name heuristics.
3. Favor dropping optional standalone package assets or optionalizing apps to independent SFS modules rather than mass-deleting installed files.
4. Preserve original ISO and immutable squashfs; modifications only on isolated branch or isolated *test* remaster with measured reversible evidence.
5. After each cut: test real Puppy graphical boot, network GUI presence, office import/edit/export, browser launch, and 32-bit/64-bit Windows PE execution inside Wine. No "PASS" for source inspection alone.
6. Separate **known installed** / **missing** / **measured** / **candidate** / **reliably verified in guest**. Reproduce all sizes; do not guess compression savings from file sizes.
7. Keep Windows-first seamless UX requirements from `docs/windows-first-desktop-requirements.md`.

**Current status:** original ISO app inventory and experimental test-SFS slimming performed. This is **not** a released, boot-and-Wine-verified build. Preserve original upstream image and do not merge without guest proof.
