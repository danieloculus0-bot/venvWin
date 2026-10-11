# Puppy-adjacent rebuild: BEAN evidence ledger

venvWin Portable is a Puppy-adjacent OS, **not** a Lucid Puppy fork.
Lucid Puppy 5.2.8 is an audited architecture reference: compact boot chain,
compressed SFS filesystem, removable-media discovery, RAM-optional loading,
session overlay, selected persistence, modular app SFS images, and simple UX.

## What is actually implemented here

- The useful `core` list contains 61 top-level packages (browser, AbiWord,
  Gnumeric, image tools, audio, networking, common firmware, storage utilities
  and venvWin runtime). Another 28 packages remain in the optional full
  standard/privacy build profiles. The original 89-package union is conserved;
  these counts do not measure installed dependency weight or final ISO bytes.
- The merged kernel repair enables Linux kernel packaging and introduces
  fail-closed kernel/initrd checks *before* image publication.
- `venvwin.bootstate` no longer treats a planned layer directory as a mounted
  filesystem; it reads mountinfo. A requested RAM boot remains a **request**,
  not verification that the SFS copied into RAM.
- The default builder is `core`, USB persistence is opt-in, and only `src/`
  plus a tiny user intro enter the product image; no CI/tests/docs are bundled.
- The old `standard` ISO workflow is manual-only, never triggered by push.
- `venvwin.puppy_evidence` emits source-hash-backed observations for BEAN.
- The `BEAN Puppy-adjacent evidence audit` workflow pins a verified BEAN
  Bridge revision, records five replay cycles to SQLite and uploads its
  JSON receipt. No ISO is compiled or rebuilt in this workflow.

## Hard evidence contract

| BEAN check | What qualifies |
|---|---|
| kernel_source_guard | Builder source contains kernel/initrd publication guards |
| lean_core_package_boundary | Core and optional package lists separated |
| runtime_overlay | **Observed guest** mountinfo proving actual OverlayFS session/layers |
| ram_copy_verified | **Observed guest** evidence that copy-to-RAM occurred within available memory |
| persistence_reboot | Same durable save/capsule data read after actual reboot |
| external_app_modules | App/SFS image mounted separately from compressed core |

Source inspection can satisfy only the first two. No checked box may be
derived from a design document, an LLM guess, a boot flag, or a directory
that merely exists.

As of this stage the expected BEAN result is **2/6 source checks passed,
4/6 runtime/product checks missing, overall FAIL**. A green CI result
only means the evidence compiler recorded that failure truthfully and
replayed it deterministically. The OS is **not boot-verified** and **not
Puppy-ready**.

## What must be built, in order

1. Minimal x86_64 kernel/initramfs + lean SFS core and basic desktop,
   verified in QEMU before adding application bundles.
2. Real OverlayFS root with explicit session upper/work and read-only base,
   using real mountinfo receipts.
3. Optional copy-to-RAM with measured SFS size and available RAM threshold;
   normal USB mode must continue to work without it.
4. USB UUID/PARTUUID detection, disposable session, and opt-in save media.
   Reboot proof should demonstrate no unexpected host writes.
5. Separate optional app modules, including Wine/compatibility and office
   tools, with their own SFS lifecycle and hashes.
6. Full BEAN guest, desktop, installation/capsule, and persistence gates.

The kernel/architecture/cleanup changes are now on `main`; they have NOT
created a new ISO. Do not run a heavyweight standard build as proof of
Puppy architecture. Independently boot-test the compact core and document
real size/RAM/usefulness measurements before choosing optional SFS modules.
