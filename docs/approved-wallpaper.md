# Approved venvWin Amber Arc wallpaper — October 14, 2026

**User-approved artwork; no redesign authorized.**

- Exact full-resolution wallpaper source: **venvwin_amber_arc_wallpaper.png** (1586 × 992; SHA-256 `1041179413b25a3b2e5be25614dc22d5e6e46a4e18aaeae4df9585d08e1ab670`).
- Space-optimized source: **venvwin-amber-arc.webp**, 1586 × 992, visually corresponding to the approved PNG, 50,288 bytes, SHA-256 `6187575271bf955ba4daaca6db01f168fdead49b4abce22c7f3275a1b004b6ab`. Encoded as ASCII base64 at `puppy-native/art/venvwin-amber-arc.webp.b64` for the automated builder.
- The previous `venvwin-wallpaper.svg` is historical, NOT the approved wallpaper and must never silently replace the new asset.
- At image assembly, `puppy-native/build-puppy.sh` must decode the pinned WebP, verify SHA-256, and install a PNG at `/usr/share/backgrounds/venvwin-wallpaper.png`.
- After Puppy first-run Quick Setup and Welcome finish, `/usr/local/bin/venvwin-wallpaper-apply` changes only the ROX-Filer PuppyPin backdrop property and reloads real ROX. Desktop icons, their positions, JWM controls, Puppy boot and Wine libraries must remain unchanged.
- The bounded startup reassertion only runs during startup and stops; it is not a fake drawn desktop and not an always-on polling daemon.

## Build / test gate

The CI action must fail if the approved source base64 is missing or checksum-invalid. A successful build does **not** by itself prove the wallpaper remains after first-run dialogs. Capture screenshots from genuine QEMU in-guest Puppy; show before/after setup and Start menu. Require no stock Puppy wallpaper in final screenshot, guest serial startup proof, and then separate Wine/WoW64 EXE/MSI tests.

## Current state

Original branded Puppy 10.0.12 boot proof passed in run #38507149795 before this wallpaper revision. New wallpaper code and source checks are committed on the isolated UI branch. **Until the approved binary image has been committed and retested in a real guest, do not call the image installed in the GitHub bootable ISO or release ready.**

The original full-resolution approved source is retained in the ChatGPT-generated project package, separate from the remote repository.
