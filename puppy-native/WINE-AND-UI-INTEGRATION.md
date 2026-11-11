# Native Puppy venvWin Wine/UI integration (experimental)

Source-only integration on top of BookwormPup64 10.0.12. **Not a verified product.**

## UI identity

Match the original May control center: dark Linux-Mint-inspired charcoal
with **orange** (#ff8a00) replacing green, soft panels, crisp lettering,
no heavy desktop environment. `src/venvwin/gui_first_run.py` retains the original
Tk interface. The native /root/Startup/venvwin-session opens it when Python/Tk
works, with YAD fallback when not installed. GTK custom CSS is applied only
when no existing per-user stylesheet would be overwritten. Puppy's JWM and
ROX configuration, upstream wallpaper and boot chain are NOT silently replaced.

## Wine policy

Wine is the core compatibility feature, **not an always-on background process**.
On startup `venvwin-wine --status` records real Wine availability, WITHOUT
installing packages or creating a default Wine prefix. The user explicitly
runs `venvwin-wine --install` to use Puppy apt or
`venvwin-wine --load-sfs FILE.sfs` for a separately chosen compatible SFS.
Never silently load an unknown legacy Wine SFS; compatibility must be verified
on the current guest kernel/glibc and the exact image.

EXE/MSI wrappers hand off to the real venvWin capsule engine and its per-app
Wine prefixes, never imply an absent runner works. Wine installations in
unsaved Puppy sessions may disappear after reboot. Linux host mounts are NOT
automatically sandboxed just by setting WINEPREFIX.

## Acceptance evidence still required

1. Authentic remastered ISO graphical BIOS **and** UEFI boot observations.
2. Native desktop opens Control Center; exact themed display screenshot.
3. Actual /proc/self/mountinfo roots and ydrv recognition, Python/Tk or YAD.
4. Wine --version in guest, actual Windows EXE/MSI installer, capsule rollback.
5. Explicit chosen persistence, reboot survival, RAM measurement and SFS modules.
6. Six BEAN source/runtime gate proofs, separate full product acceptance.

The patch does **not** download or rebuild the ~791 MiB ISO and does NOT
auto-trigger legacy Debian workflows. Merge remains prohibited until evidence.
