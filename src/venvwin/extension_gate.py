from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CAPABILITIES: tuple[str, ...] = (
    "read_status",
    "read_capsules",
    "run_doctor",
)

FORBIDDEN_CAPABILITIES: tuple[str, ...] = (
    "covert_access",
    "silent_host_write",
    "credential_access",
    "persistence_without_owner_consent",
    "remote_control_without_owner_consent",
)


@dataclass(frozen=True, slots=True)
class ExtensionGateStatus:
    enabled: bool
    owner_confirmed: bool
    local_visible: bool
    audit_log: Path
    capabilities: tuple[str, ...]
    forbidden_capabilities: tuple[str, ...]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "owner_confirmed": self.owner_confirmed,
            "local_visible": self.local_visible,
            "audit_log": str(self.audit_log),
            "capabilities": list(self.capabilities),
            "forbidden_capabilities": list(self.forbidden_capabilities),
            "message": self.message,
        }


def default_extension_gate_dir(home: Path | None = None) -> Path:
    user_home = home or Path.home()
    return user_home / ".config" / "venvwin" / "extension-gate"


def default_config_path(home: Path | None = None) -> Path:
    return default_extension_gate_dir(home) / "config.json"


def default_audit_log(home: Path | None = None) -> Path:
    return default_extension_gate_dir(home) / "audit.log"


def default_config(home: Path | None = None) -> dict[str, Any]:
    return {
        "enabled": False,
        "owner_confirmed": False,
        "local_visible": True,
        "capabilities": list(DEFAULT_CAPABILITIES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "audit_log": str(default_audit_log(home)),
        "policy": "No covert access. No silent host writes. No credential access. No remote control without explicit owner consent.",
    }


def write_default_config(home: Path | None = None) -> Path:
    path = default_config_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default_config(home), indent=2), encoding="utf-8")
    audit = default_audit_log(home)
    audit.touch(exist_ok=True)
    return path


def load_config(home: Path | None = None) -> dict[str, Any]:
    path = write_default_config(home)
    return json.loads(path.read_text(encoding="utf-8"))


def extension_gate_status(home: Path | None = None) -> ExtensionGateStatus:
    config = load_config(home)
    enabled = bool(config.get("enabled", False))
    owner_confirmed = bool(config.get("owner_confirmed", False))
    local_visible = bool(config.get("local_visible", True))
    raw_capabilities = tuple(str(item) for item in config.get("capabilities", DEFAULT_CAPABILITIES))
    forbidden = tuple(str(item) for item in config.get("forbidden_capabilities", FORBIDDEN_CAPABILITIES))
    safe_capabilities = tuple(item for item in raw_capabilities if item not in forbidden)
    audit_log = Path(str(config.get("audit_log", default_audit_log(home))))

    active = enabled and owner_confirmed and local_visible
    message = (
        "Extension gate enabled with explicit owner confirmation."
        if active
        else "Extension gate disabled. Future expansion point exists, but no access is active."
    )

    return ExtensionGateStatus(
        enabled=active,
        owner_confirmed=owner_confirmed,
        local_visible=local_visible,
        audit_log=audit_log,
        capabilities=safe_capabilities,
        forbidden_capabilities=forbidden,
        message=message,
    )


def record_audit_event(event: str, home: Path | None = None) -> Path:
    status = extension_gate_status(home)
    status.audit_log.parent.mkdir(parents=True, exist_ok=True)
    with status.audit_log.open("a", encoding="utf-8") as handle:
        handle.write(event.strip() + "\n")
    return status.audit_log
