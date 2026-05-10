from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

PUBLIC_BOOTSTATE_PATH = Path("/etc/venvwin/BOOTSTATE")
USER_BOOTSTATE_PATH = Path.home() / ".venvwin-bootstate"
LAYER_ROOT = Path("/initrd/venvwin")

VALID_BOOT_MODES = {"normal", "ram", "nosave", "repair", "developer"}
VALID_SAVE_MODES = {"plain", "encrypted", "none", "developer", "unknown"}


@dataclass(frozen=True)
class LayerState:
    name: str
    role: str
    path: str
    writable: bool
    required: bool
    mounted: bool = False
    source: str = "planned"


@dataclass(frozen=True)
class BootState:
    product: str = "venvWin Portable"
    architecture: str = "puppy-style-overlayfs"
    boot_mode: str = "normal"
    save_mode: str = "unknown"
    session_layer: str = "tmpfs"
    copy_to_ram: bool = False
    usb_first: bool = True
    root_device_hint: str = "UUID/PARTUUID/label preferred; never hard-code /dev/sdX"
    system_sfs: str = "venvwin-system.sfs"
    drivers_sfs: str = "venvwin-drivers.sfs"
    dev_sfs: str = "venvwin-dev.sfs"
    save_target: str = "venvwin-save partition or save image"
    kernel: str = field(default_factory=platform.release)
    cmdline: str = ""
    layers: list[LayerState] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["layers"] = [asdict(layer) for layer in self.layers]
        return data

    def to_lines(self) -> list[str]:
        lines = [
            f"product={self.product}",
            f"architecture={self.architecture}",
            f"boot_mode={self.boot_mode}",
            f"save_mode={self.save_mode}",
            f"session_layer={self.session_layer}",
            f"copy_to_ram={str(self.copy_to_ram).lower()}",
            f"usb_first={str(self.usb_first).lower()}",
            f"root_device_hint={self.root_device_hint}",
            f"system_sfs={self.system_sfs}",
            f"drivers_sfs={self.drivers_sfs}",
            f"dev_sfs={self.dev_sfs}",
            f"save_target={self.save_target}",
            f"kernel={self.kernel}",
            f"cmdline={self.cmdline}",
        ]
        for layer in self.layers:
            safe_name = layer.name.replace("-", "_")
            lines.append(f"layer.{safe_name}.role={layer.role}")
            lines.append(f"layer.{safe_name}.path={layer.path}")
            lines.append(f"layer.{safe_name}.writable={str(layer.writable).lower()}")
            lines.append(f"layer.{safe_name}.required={str(layer.required).lower()}")
            lines.append(f"layer.{safe_name}.mounted={str(layer.mounted).lower()}")
            lines.append(f"layer.{safe_name}.source={layer.source}")
        return lines


def read_kernel_cmdline(path: Path = Path("/proc/cmdline")) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _tokens(cmdline: str) -> set[str]:
    return {token.strip() for token in cmdline.split() if token.strip()}


def _value(tokens: Iterable[str], key: str) -> str | None:
    prefix = f"{key}="
    for token in tokens:
        if token.startswith(prefix):
            return token[len(prefix) :]
    return None


def detect_boot_mode(cmdline: str | None = None, environ: dict[str, str] | None = None) -> str:
    env = environ if environ is not None else os.environ
    requested = env.get("VENVWIN_BOOT_MODE")
    tokens = _tokens(cmdline if cmdline is not None else read_kernel_cmdline())
    requested = requested or _value(tokens, "venvwin.mode") or _value(tokens, "boot_mode")

    if requested:
        normalized = requested.lower().strip()
        if normalized in VALID_BOOT_MODES:
            return normalized

    if "venvwin.repair" in tokens or "single" in tokens or "rescue" in tokens:
        return "repair"
    if "venvwin.nosave" in tokens or "pfix=ram" in tokens:
        return "nosave"
    if "venvwin.ram" in tokens or "toram" in tokens or "pfix=copy" in tokens:
        return "ram"
    if "venvwin.dev" in tokens or "developer" in tokens:
        return "developer"
    return "normal"


def detect_save_mode(cmdline: str | None = None, environ: dict[str, str] | None = None) -> str:
    env = environ if environ is not None else os.environ
    requested = env.get("VENVWIN_SAVE_MODE")
    tokens = _tokens(cmdline if cmdline is not None else read_kernel_cmdline())
    requested = requested or _value(tokens, "venvwin.save")
    if requested:
        normalized = requested.lower().strip()
        if normalized in VALID_SAVE_MODES:
            return normalized
    if "venvwin.nosave" in tokens or "pfix=ram" in tokens:
        return "none"
    if "persistence" in tokens:
        return "plain"
    return "unknown"


def detect_copy_to_ram(cmdline: str | None = None, environ: dict[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    requested = env.get("VENVWIN_COPY_TO_RAM")
    if requested is not None:
        return requested.lower() in {"1", "true", "yes", "on"}
    tokens = _tokens(cmdline if cmdline is not None else read_kernel_cmdline())
    if "venvwin.nocopy" in tokens or "pfix=nocopy" in tokens:
        return False
    return "venvwin.ram" in tokens or "toram" in tokens or "pfix=copy" in tokens


def planned_layers() -> list[LayerState]:
    return [
        LayerState("session_rw", "top writable tmpfs session layer", str(LAYER_ROOT / "session_rw"), True, True),
        LayerState("save_rw", "USB persistence layer or encrypted save image", str(LAYER_ROOT / "save_rw"), True, False),
        LayerState("system_ro", "pristine compressed base system image", str(LAYER_ROOT / "system_ro"), False, True),
        LayerState("drivers_ro", "optional driver and firmware module image", str(LAYER_ROOT / "drivers_ro"), False, False),
        LayerState("apps_ro", "optional read-only app capsule or module layers", str(LAYER_ROOT / "apps_ro"), False, False),
        LayerState("dev_ro", "optional developer SDK module", str(LAYER_ROOT / "dev_ro"), False, False),
    ]


def runtime_layers() -> list[LayerState]:
    layers: list[LayerState] = []
    for layer in planned_layers():
        path = Path(layer.path)
        layers.append(
            LayerState(
                name=layer.name,
                role=layer.role,
                path=layer.path,
                writable=layer.writable,
                required=layer.required,
                mounted=path.exists(),
                source="runtime" if path.exists() else "planned",
            )
        )
    return layers


def bootstate_report() -> BootState:
    cmdline = read_kernel_cmdline()
    boot_mode = detect_boot_mode(cmdline)
    return BootState(
        boot_mode=boot_mode,
        save_mode=detect_save_mode(cmdline),
        copy_to_ram=detect_copy_to_ram(cmdline) or boot_mode == "ram",
        cmdline=cmdline,
        layers=runtime_layers(),
    )


def write_bootstate(path: Path | None = None) -> Path:
    target = path or PUBLIC_BOOTSTATE_PATH
    state = bootstate_report()
    content = "\n".join(state.to_lines()) + "\n"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target
    except OSError:
        USER_BOOTSTATE_PATH.write_text(content, encoding="utf-8")
        return USER_BOOTSTATE_PATH


def bootstate_json() -> str:
    return json.dumps(bootstate_report().to_dict(), indent=2)


def bootstate_text() -> str:
    return "\n".join(bootstate_report().to_lines()) + "\n"
