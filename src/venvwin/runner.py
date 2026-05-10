from __future__ import annotations

import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path

from .capsule import Capsule


@dataclass(slots=True)
class PreparedCommand:
    env: dict[str, str]
    args: list[str]

    def shell_preview(self) -> str:
        env_part = " ".join(f"{key}={shlex.quote(value)}" for key, value in self.env.items())
        arg_part = " ".join(shlex.quote(arg) for arg in self.args)
        return f"{env_part} {arg_part}".strip()


def _runner_binary_available(binary: str) -> str | None:
    path = Path(binary)
    if path.is_absolute() and path.exists():
        return str(path)
    if any(separator in binary for separator in ("/", "\\")) and path.exists():
        return str(path)
    return shutil.which(binary)


def require_command_runner(command: PreparedCommand) -> str:
    if not command.args:
        raise ValueError("Cannot run an empty venvWin command")

    binary = command.args[0]
    found = _runner_binary_available(binary)
    if found:
        return found

    raise FileNotFoundError(
        f"Runner not found on PATH: {binary}. Install Wine or use a venvWin Portable profile that includes Wine before launching Windows apps."
    )


class Runner:
    def prepare_install(self, capsule: Capsule, installer_path: str) -> PreparedCommand:
        raise NotImplementedError

    def prepare_launch(self, capsule: Capsule, executable_path: str) -> PreparedCommand:
        raise NotImplementedError


class WineRunner(Runner):
    def _base_env(self, capsule: Capsule) -> dict[str, str]:
        env = {
            "WINEPREFIX": capsule.prefix_path,
            "WINEARCH": capsule.profile.arch,
        }
        env.update(capsule.profile.env)
        return env

    def _runner_args(self, capsule: Capsule) -> list[str]:
        return [capsule.profile.runner, *capsule.profile.args]

    def prepare_install(self, capsule: Capsule, installer_path: str) -> PreparedCommand:
        suffix = Path(installer_path).suffix.lower()
        runner_args = self._runner_args(capsule)

        if suffix == ".msi":
            args = [*runner_args, "msiexec", "/i", installer_path]
        elif suffix == ".exe":
            args = [*runner_args, installer_path]
        elif suffix == ".msix":
            raise ValueError(
                "MSIX/AppX installers are not supported by Wine-backed venvWin capsules yet. Use a classic EXE or MSI installer."
            )
        else:
            raise ValueError(f"Unsupported installer type for Wine runner: {suffix or '<none>'}")

        return PreparedCommand(env=self._base_env(capsule), args=args)

    def prepare_launch(self, capsule: Capsule, executable_path: str) -> PreparedCommand:
        return PreparedCommand(
            env=self._base_env(capsule),
            args=[*self._runner_args(capsule), executable_path],
        )


def get_runner(name: str) -> Runner:
    normalized = name.strip().lower()
    if normalized in {"wine", "wine64"}:
        return WineRunner()
    raise ValueError(f"Unsupported runner: {name}")
