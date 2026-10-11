"""Machine-evidence snapshot for BEAN Bridge's Puppy-adjacent readiness gate.

Do not equate a source-code contract with an actual boot. The 6-check report
deliberately stays FAIL until mounts, RAM copy, reboot persistence and separate
app modules have been *observed* on a running guest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _source(root: Path, relative: str) -> tuple[str, str | None]:
    file = root / relative
    try:
        raw = file.read_bytes()
        return raw.decode("utf-8"), "source:" + relative + ":sha256:" + hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeDecodeError):
        return "", None


def _check(passed: bool | None, *evidence: str | None, reason: str) -> dict:
    refs = [ref for ref in evidence if ref]
    if passed is None:
        state = "missing"
    elif passed:
        state = "pass" if refs else "unproven"
    else:
        state = "fail"
    return {"status": state, "evidence": ";".join(refs), "reason": reason}


def _heredoc_packages(text: str, filename: str) -> set[str] | None:
    pattern = re.compile(
        r"cat > config/package-lists/" + re.escape(filename) +
        r" <<'EOF'\n(?P<packages>.*?)\nEOF", re.S
    )
    found = pattern.search(text)
    if found is None:
        return None
    return {line.strip() for line in found.group("packages").splitlines()
            if line.strip() and not line.startswith("#")}


def build_report(root: Path) -> dict:
    root = Path(root)
    builder, builder_id = _source(root, "venvwin-portable/build-iso.sh")
    gate, gate_id = _source(root, "venvwin-portable/build-flash-ready-standard.sh")
    persistence, persistence_id = _source(root, "src/venvwin/persistence.py")
    bootstate, bootstate_id = _source(root, "src/venvwin/bootstate.py")
    core = _heredoc_packages(builder, "00-venvwin-core.list.chroot")
    extras = _heredoc_packages(builder, "05-venvwin-utilities.list.chroot")

    # Proves guards are present in source, NOT that any ISO was booted.
    kernel_guard = all(x in builder for x in (
        "--linux-packages linux-image", "--linux-flavours amd64",
        "ISO_KERNEL_MISSING", "ISO_INITRD_MISSING", "ISO_SQUASHFS_MISSING",
    )) and all(x in gate for x in ("STATIC_KERNEL_MISSING", "STATIC_INITRD_MISSING"))
    kernel_status = _check(
        kernel_guard if builder_id and gate_id else None, builder_id, gate_id,
        reason="source_config_guard_only; new ISO boot remains unverified",
    )

    required_core = {"linux-image-amd64", "live-boot", "live-config", "python3",
                     "lightdm", "xfce4-session", "network-manager"}
    must_be_optional = {"libreoffice-writer", "libreoffice-calc", "ffmpeg",
                        "guvcview", "gparted", "testdisk"}
    lean = (core is not None and extras is not None and required_core <= core
            and not (must_be_optional & core) and must_be_optional <= extras
            and "05-venvwin-utilities.list.chroot" in builder)
    core_status = _check(
        lean if core is not None else None, builder_id,
        reason="package-list_boundary_only; reduced ISO size not measured",
    )

    # No runtime claims may be inferred from prose, cmdline flags, or Path.exists.
    # A verified guest must supply mountinfo, overlay upper/work sources and
    # a boot identity tied to a specific checksum before this can become PASS.
    overlay_status = _check(
        None, reason="no mounted OverlayFS layer evidence from a real guest",
    )
    ram_status = _check(
        None, reason="no measured memory budget and confirmed SFS copy from a guest",
    )
    # Capsule path selection is real code; USB save/reboot proof is not yet real.
    save_status = _check(
        False if not persistence_id else None, persistence_id,
        reason="capsule storage code is not reboot-verified removable-media persistence",
    )
    modular_status = _check(
        None, builder_id if builder_id else None,
        reason="optional package lists are not independently mounted app SFS modules",
    )
    return {
        "project": "venvwin",
        "phase": "puppy",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_type": "repository_static_inspection",
        "checks": {
            "kernel_source_guard": kernel_status,
            "lean_core_package_boundary": core_status,
            "runtime_overlay": overlay_status,
            "ram_copy_verified": ram_status,
            "persistence_reboot": save_status,
            "external_app_modules": modular_status,
        },
        "scope": {
            "verified": "repository source files and package list split only",
            "not_verified": ["booted new ISO", "OverlayFS runtime mounts",
                             "safe actual copy-to-RAM", "USB persistence across reboot",
                             "modular SFS loading", "size and idle RAM"],
            "bootstate_source": bootstate_id,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    report = build_report(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
