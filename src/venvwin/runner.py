from __future__ import annotations

from dataclasses import dataclass

from .capsule import Capsule


@dataclass(slots=True)
class PreparedCommand:
    env: dict[str, str]
    args: list[str]

    def shell_preview(self) -> str:
        env_part = " ".join(f'{key}="{value}"' for key, value in self.env.items())
        arg_part = " ".join(self.args)
        return f"{env_part} {arg_part}".strip()


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

    def prepare_install(self, capsule: Capsule, installer_path: str) -> PreparedCommand:
        return PreparedCommand(
            env=self._base_env(capsule),
            args=[capsule.profile.runner, *capsule.profile.args, installer_path],
        )

    def prepare_launch(self, capsule: Capsule, executable_path: str) -> PreparedCommand:
        return PreparedCommand(
            env=self._base_env(capsule),
            args=[capsule.profile.runner, *capsule.profile.args, executable_path],
        )


def get_runner(name: str) -> Runner:
    normalized = name.strip().lower()
    if normalized in {"wine", "wine64"}:
        return WineRunner()
    raise ValueError(f"Unsupported runner: {name}")
