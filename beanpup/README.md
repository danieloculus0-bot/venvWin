# BEANpup migration candidate

BEANpup is the new **Puppy Linux-derived** portable desktop home for BEAN. It is independent of the original venvWin product. The original project and its branches are preserved.

## Verified vs pending
- **Source imported:** only a minimal Puppy-native image build recipe, diagnostics launcher and guest-side boot probe.
- **Pinned base:** official BookwormPup64 10.0.12, checked against its SHA-256.
- **Not claimed:** a released bootable BEANpup ISO, a successful QEMU guest boot, persistence across reboot, physical USB compatibility, Windows recovery, or integrated BEAN Core.
- This branch builds a **candidate only**. A failing boot job must remain a failure; do not publish an ISO on static tests alone.

## Build
On an x86_64 Linux builder with curl, xorriso and squashfs-tools:

```sh
bash -n beanpup/build.sh
bash beanpup/build.sh
```

Output: `dist/beanpup-candidate.iso` and its SHA-256. Source ISO is fetched once and cached in `build/beanpup/`. Never commit build outputs.

The `.github/workflows/beanpup-boot.yml` job creates an image from the pinned upstream source and requires a **guest-emitted GUI startup marker** from booting that image. This is a virtualized **test bench only**, not a VM shipped in BEANpup.

## Product constraints
- Linux Mint-inspired UX, while remaining Puppy-native and lightweight.
- Use the canonical logo from the BEAN GitHub project **only after verifying the actual artwork**.
- BEAN Core is the native resident intelligence, once independently proven on this base.
- Optional tools, rescue utilities, packages, and coding features are **à la carte**, activated at point of use.
- Do not install optional package libraries into the base merely because they are available offline.
- Do not add background services without functional and resource evidence.
- No included VM or hypervisor.
- Recovery tooling must support offline filesystem inspection and non-destructive backup before modification.

## Separate repository migration
Target repository: `danieloculus0-bot/BEANpup` (not yet created). The GitHub connector cannot provision new repositories. After it exists, migrate this minimal candidate and its successful boot evidence into it, keeping venvWin history and unrelated compatibility experiments out of the new tree.

## Next acceptance checkpoints
1. Candidate ISO static repack and QEMU guest GUI startup pass.
2. Reboot with persistent save and verify state; RAM/copy-to-RAM behavior measured.
3. Verify physical boot on representative UEFI and legacy BIOS x86_64 machines.
4. Add BEAN Core and local terminal coding as separate tested modules.
5. Add system recovery and offline package activation individually, with tests.
6. Apply the validated BEAN logo and Mint-inspired theme without disturbing boot.
