# venvWin Package Management and Database — Required Infrastructure

**Status: locked design requirement (2026-10-13). Not an optional/deletable app.**

## Already confirmed in original checksum-verified BookwormPup64 10.0.12 ISO

- **Synaptic graphical package manager**: real executable `usr/sbin/synaptic` (in bdrv), `usr/bin/synaptic-pkexec` (in bdrv), and native GUI desktop menu launcher (main SFS).
- **APT**: apt, apt-get, apt-cache (bdrv); real Debian Bookworm package repository configuration and downloaded package lists (bdrv).
- **dpkg database and tools**: dpkg and dpkg-query executables (main SFS) with `/var/lib/dpkg/status` and `/var/lib/dpkg/available` in the unmodified bdrv.
- **Puppy legacy package manager**: PET gui and chooser (`/usr/local/petget/pkg_chooser.sh`), and SFS-Load menu integration. Don't assume optional runtime repository database works until guest tested.
- **SQLite for venvWin**: Python 3.11 sqlite3 package and real `_sqlite3` shared extension present. CLI `/usr/bin/sqlite3` was not observed; not needed to use sqlite3 from Python. Actual runtime DB transaction still untested.
- **Potential conflicts**: Repo original ISO has multiple menu launchers for Puppy legacy package manager in distinct SFS layers. Real JWM menu and GUI launch should be verified; don't fabricate a new storefront.

See inventory: https://github.com/danieloculus0-bot/venvWin/actions/runs/38503497986 .
The separate package status audit, https://github.com/danieloculus0-bot/venvWin/actions/runs/38503572348 , found no installed dpkg package entries with the names of currently proposed standalone app removals. This is NOT a general package ownership audit.

## UX contract

Primary venvWin desktop software management should expose **Synaptic** as Software Manager (launch real existing Synaptic, don't imitate it). Puppy PET and SFS-Load remain in Advanced/Utilities or native Puppy menus. Normal users should be able to search, review dependencies, install, uninstall, update and inspect failures using the existing real package management infrastructure. If a manager is missing or broken, show a real error; never substitute a fake catalog.

## Database contract

1. Preserve installed dpkg status, available package data, APT sources/indexes and package-management executables across image trimming. No deletion, fake generated package inventory, or unsupported foreign repository mixing.
2. Keep the entire bdrv (APT / dpkg installed database), adrv (browser), fdrv (hardware firmware), and zdrv (kernel driver modules) **byte-for-byte untouched** when making an experimental trimmed main-SFS remaster. Do not strip system libraries, network tools, package DB or Wine compatibility libraries.
3. APT package installation/update modifies Puppy's live writable layer. **Persistent package installs require an explicitly chosen, functioning save folder/savefile or installed Puppy root.** Test that installed package state and its dpkg records survive reboot; don't claim persistence from file existence.
4. Keep venvWin Windows capsule metadata separate from dpkg and PET. Current app capsules have individual `venvwin.json` metadata; SQLite can support future indexing, but no SQLite conversion without migration and data-integrity tests. Wine prefixes live under explicitly chosen user storage, not in the package-manager database.
5. Ensure file associations and default app handlers never launch programs removed from the trimmed image. The trim script rewires default audio playback to mpv, makes audio editor absence explicit, and requires guest validation of CDDA support before shipping that default.
6. Synaptic/PET/SFS and SQLite are *presence confirmed*, not actual working GUI transactions or durable storage. Required later evidence: original package metadata, Synaptic GUI launch, package search, verified install/uninstall of a tiny test package with dependencies, SFS module mount/unmount, package DB consistency and reboot persistence, while Wine PE32 and PE32+ continue to run.

## Release rule

Fail release if actual Puppy package management is broken or cannot persist when save mode is enabled, even if the slimmed SFS is smaller. Do NOT merge this app-trim branch before package-manager and Wine guest tests pass.
