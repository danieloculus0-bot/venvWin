from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .capsule import create_capsule, list_capsules, load_capsule, save_capsule
from .paths import capsules_dir, default_root, ensure_runtime_dirs, profiles_dir
from .profile import RunnerProfile, load_profile, save_profile
from .runner import get_runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="venvwin", description="venvWin capsule manager")
    parser.add_argument("--root", type=Path, default=default_root(), help="venvWin runtime root")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize runtime directories and default profile")

    profile = sub.add_parser("profile", help="Manage runner profiles")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)
    profile_sub.add_parser("default", help="Write the default runner profile")

    create = sub.add_parser("create", help="Create a new app capsule")
    create.add_argument("app_name")
    create.add_argument("--profile", default="default")

    sub.add_parser("list", help="List capsules")

    inspect = sub.add_parser("inspect", help="Inspect a capsule")
    inspect.add_argument("capsule_id")

    install = sub.add_parser("install-command", help="Print the install command for an installer")
    install.add_argument("capsule_id")
    install.add_argument("installer_path")

    launch = sub.add_parser("launch-command", help="Print the launch command for an executable")
    launch.add_argument("capsule_id")
    launch.add_argument("executable_path")

    record = sub.add_parser("record-launcher", help="Record a launch target inside a capsule")
    record.add_argument("capsule_id")
    record.add_argument("name")
    record.add_argument("executable_path")

    return parser


def cmd_init(root: Path) -> int:
    ensure_runtime_dirs(root)
    save_profile(profiles_dir(root), RunnerProfile.default())
    print(f"Initialized venvWin runtime: {root}")
    return 0


def cmd_profile_default(root: Path) -> int:
    ensure_runtime_dirs(root)
    path = save_profile(profiles_dir(root), RunnerProfile.default())
    print(f"Wrote default profile: {path}")
    return 0


def cmd_create(root: Path, app_name: str, profile_name: str) -> int:
    ensure_runtime_dirs(root)
    profile = load_profile(profiles_dir(root), profile_name)
    capsule = create_capsule(capsules_dir(root), app_name, profile)
    print(json.dumps(capsule.to_dict(), indent=2))
    return 0


def cmd_list(root: Path) -> int:
    ensure_runtime_dirs(root)
    capsules = list_capsules(capsules_dir(root))
    if not capsules:
        print("No capsules found.")
        return 0
    for capsule in capsules:
        print(f"{capsule.capsule_id}\t{capsule.app_name}\t{capsule.profile.name}")
    return 0


def cmd_inspect(root: Path, capsule_id: str) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    print(json.dumps(capsule.to_dict(), indent=2))
    return 0


def cmd_install_command(root: Path, capsule_id: str, installer_path: str) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    runner = get_runner(capsule.profile.runner)
    command = runner.prepare_install(capsule, installer_path)
    print(command.shell_preview())
    return 0


def cmd_launch_command(root: Path, capsule_id: str, executable_path: str) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    runner = get_runner(capsule.profile.runner)
    command = runner.prepare_launch(capsule, executable_path)
    print(command.shell_preview())
    return 0


def cmd_record_launcher(root: Path, capsule_id: str, name: str, executable_path: str) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    capsule.launchers.append({"name": name, "executable_path": executable_path})
    save_capsule(capsules_dir(root), capsule)
    print(f"Recorded launcher '{name}' for {capsule_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()

    try:
        if args.command == "init":
            return cmd_init(root)
        if args.command == "profile" and args.profile_command == "default":
            return cmd_profile_default(root)
        if args.command == "create":
            return cmd_create(root, args.app_name, args.profile)
        if args.command == "list":
            return cmd_list(root)
        if args.command == "inspect":
            return cmd_inspect(root, args.capsule_id)
        if args.command == "install-command":
            return cmd_install_command(root, args.capsule_id, args.installer_path)
        if args.command == "launch-command":
            return cmd_launch_command(root, args.capsule_id, args.executable_path)
        if args.command == "record-launcher":
            return cmd_record_launcher(root, args.capsule_id, args.name, args.executable_path)
    except Exception as exc:
        print(f"venvwin: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
