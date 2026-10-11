"""Source-hash-backed evidence contract for ACTUAL native BookwormPup64 design.

Static source review permits two of six BEAN gates. Runtime gates require
independent guest-origin observations and may never be inferred from scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _source(root: Path, relative: str) -> tuple[str, str | None]:
    path = root / relative
    try:
        raw = path.read_bytes()
        return raw.decode("utf-8"), (
            "source:" + relative + ":sha256:" + hashlib.sha256(raw).hexdigest()
        )
    except (OSError, UnicodeDecodeError):
        return "", None


def _check(ok: bool | None, refs: list[str | None], *, reason: str) -> dict:
    refs = [r for r in refs if r]
    if ok is None:
        state = "missing"
    elif ok:
        state = "pass" if refs else "unproven"
    else:
        state = "fail"
    return {"status": state, "evidence": ";".join(refs), "reason": reason}


def build_report(root: Path) -> dict:
    root = Path(root)
    build, build_ref = _source(root, "puppy-native/build-puppy.sh")
    qemu, qemu_ref = _source(root, "puppy-native/prove-puppy-qemu.sh")
    probe, probe_ref = _source(root, "puppy-native/venvwin-guest-probe")
    launcher, launcher_ref = _source(root, "puppy-native/venvwin-launcher")
    python_source, source_ref = _source(root, "src/venvwin/cli.py")

    # Source only: does NOT prove an ISO has booted, mounted, or survived reboot.
    boot_contract = all(token in build for token in (
        "BookwormPup64_10.0.12.iso", "UPSTREAM_SHA256=",
        "sha256sum -c -", "-boot_image any replay -commit",
        "UPSTREAM_PUPPY_PAYLOAD_MISSING",
    )) and all(token in qemu for token in (
        '-cdrom "$ISO"', "-net none", "PUPPY_GUEST_BOOT_PROVEN",
        "PUPPY_VENVWIN_CAPSULE_CLI_PASS",
    ))
    package_boundary = all(token in build for token in (
        "ydrv_dpupbw64_10.0.12.sfs",
        "REFUSE_TO_REPLACE_EXISTING_UPSTREAM_YDRV",
        'mksquashfs "$STAGE" "$SFS"',
        '"$ROOT/src/venvwin"',
    )) and all(token in probe for token in (
        "/proc/mounts", "PUPPY_OVERLAY_NOT_OBSERVED", "/dev/ttyS0",
    )) and bool(launcher_ref and source_ref)

    checks = {
        "kernel_source_guard": _check(
            boot_contract if build_ref and qemu_ref else None,
            [build_ref, qemu_ref],
            reason="source-only real Puppy bootloader checksum and QEMU proof requirements",
        ),
        "lean_core_package_boundary": _check(
            package_boundary if build_ref and probe_ref else None,
            [build_ref, probe_ref, launcher_ref, source_ref],
            reason="separate Puppy ydrv app module source; actual SFS boot still requires guest proof",
        ),
        "runtime_overlay": _check(
            None, [], reason="no independently imported actual guest mount report",
        ),
        "ram_copy_verified": _check(
            None, [], reason="no actual guest measurement of copied SFS and memory budget",
        ),
        "persistence_reboot": _check(
            None, [], reason="no separately observed user-chosen save data across real guest reboot",
        ),
        "external_app_modules": _check(
            None, [], reason="no separately observed optional SFS load, app execution and unload",
        ),
    }
    return {
        "project": "venvwin", "phase": "puppy",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_type": "repository_static_inspection",
        "checks": checks,
        "scope": {
            "verified": "only source-level pinned native Puppy build and SFS layering design",
            "not_verified": [
                "booted ISO", "live desktop", "OverlayFS guest mount",
                "real copy-to-RAM", "user-chosen save surviving reboot",
                "external app modules", "in-Puppy Wine runner and installation",
            ],
            "original_debian_builder_archived": True,
            "source_artifacts_not_runtime_proof": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_report(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
