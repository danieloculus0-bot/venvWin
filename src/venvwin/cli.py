from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .associate import default_applications_dir, write_file_association_handlers
from .bootstate import bootstate_json, bootstate_text, write_bootstate
from .capsule import create_capsule, list_capsules, load_capsule, save_capsule
from .dashboard import DEFAULT_HOST, DEFAULT_PORT, run_dashboard
from .desktop import generate_desktop_launcher
from .first_run import wizard_text, write_first_run_files
from .health import health_report
from .install import install_into_capsule
from .open import open_windows_file
from .paths import capsules_dir, default_root, ensure_runtime_dirs, profiles_dir
from .persistence import persistence_report
from .profile import RunnerProfile, load_profile, save_profile
from .runner import get_runner
from .snapshot import create_snapshot, reset_capsule_prefix, restore_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="venvwin", description="venvWin capsule manager")
    parser.add_argument("--root", type=Path, default=default_root(), help="venvWin runtime root")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize runtime directories and default profile")
    sub.add_parser("frontier-trail", help="Play Daniel Boone: Frontier Trail")

    bootstate = sub.add_parser("bootstate", help="Show Puppy-style venvWin boot/session layer state")
    bootstate.add_argument("--json", action="store_true", help="Print raw JSON report")
    bootstate.add_argument("--write", action="store_true", help="Write BOOTSTATE to /etc/venvwin/BOOTSTATE or user fallback")

    first_run = sub.add_parser("first-run", help="Create first-run files and show storage summary")
    first_run.add_argument("--home", type=Path, help="Override home path for testing")
    first_run.add_argument("--wizard-text", action="store_true", help="Print planned GUI-lite wizard text")
    first_run.add_argument("--json", action="store_true", help="Print raw JSON summary")

    dashboard = sub.add_parser("dashboard", help="Run the local venvWin dashboard app")
    dashboard.add_argument("--host", default=DEFAULT_HOST, help="Dashboard bind host")
    dashboard.add_argument("--port", type=int, default=DEFAULT_PORT, help="Dashboard port")
    dashboard.add_argument("--home", type=Path, help="Override home path for testing")

    doctor = sub.add_parser("doctor", help="Check venvWin health and setup status")
    doctor.add_argument("--applications-dir", type=Path)
    doctor.add_argument("--json", action="store_true", help="Print raw JSON report")

    storage = sub.add_parser("storage", help="Show capsule storage and leave-no-trace status")
    storage.add_argument("--json", action="store_true", help="Print raw JSON report")

    associate = sub.add_parser("associate", help="Install desktop handlers for EXE/MSI double-click support")
    associate.add_argument("--applications-dir", type=Path)

    open_cmd = sub.add_parser("open", help="Open an EXE/MSI through venvWin")
    open_cmd.add_argument("file_path", type=Path)
    open_cmd.add_argument("--dry-run", action="store_true")
    open_cmd.add_argument("--profile", default="default")

    profile = sub.add_parser("profile", help="Manage runner profiles")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)
    profile_sub.add_parser("default", help="Write the default runner profile")

    create = sub.add_parser("create", help="Create a new app capsule")
    create.add_argument("app_name")
    create.add_argument("--profile", default="default")

    sub.add_parser("list", help="List capsules")

    inspect = sub.add_parser("inspect", help="Inspect a capsule")
    inspect.add_argument("capsule_id")

    install = sub.add_parser("install", help="Run an installer inside a capsule")
    install.add_argument("capsule_id")
    install.add_argument("installer_path", type=Path)
    install.add_argument("--dry-run", action="store_true", help="Record and print command without executing")
    install.add_argument("--no-copy", action="store_true", help="Do not copy installer into capsule history")

    snapshot = sub.add_parser("snapshot", help="Create or restore capsule snapshots")
    snapshot_sub = snapshot.add_subparsers(dest="snapshot_command", required=True)
    snapshot_create = snapshot_sub.add_parser("create", help="Create a capsule snapshot")
    snapshot_create.add_argument("capsule_id")
    snapshot_create.add_argument("--label")
    snapshot_restore = snapshot_sub.add_parser("restore", help="Restore a capsule snapshot")
    snapshot_restore.add_argument("capsule_id")
    snapshot_restore.add_argument("snapshot_file", type=Path)

    reset = sub.add_parser("reset", help="Reset capsule prefix while preserving a backup")
    reset.add_argument("capsule_id")

    install_command = sub.add_parser("install-command", help="Print the install command for an installer")
    install_command.add_argument("capsule_id")
    install_command.add_argument("installer_path")

    launch = sub.add_parser("launch-command", help="Print the launch command for an executable")
    launch.add_argument("capsule_id")
    launch.add_argument("executable_path")

    launcher = sub.add_parser("launcher", help="Manage desktop launchers")
    launcher_sub = launcher.add_subparsers(dest="launcher_command", required=True)
    launcher_create = launcher_sub.add_parser("create", help="Create a Linux .desktop launcher")
    launcher_create.add_argument("capsule_id")
    launcher_create.add_argument("name")
    launcher_create.add_argument("executable_path")
    launcher_create.add_argument("--output-dir", type=Path)

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


def cmd_bootstate(as_json: bool, write: bool) -> int:
    if write:
        path = write_bootstate()
        print(f"Wrote BOOTSTATE: {path}")
        return 0
    if as_json:
        print(bootstate_json())
    else:
        print(bootstate_text(), end="")
    return 0


def cmd_first_run(home: Path | None, wizard: bool, as_json: bool) -> int:
    target_home = home.expanduser().resolve() if home else None
    if wizard:
        print(wizard_text(target_home))
        return 0
    summary = write_first_run_files(target_home)
    if as_json:
        print(json.dumps(summary, indent=2))
    else:
        print("venvWin first-run files created")
        print(f"capsule store: {summary['capsule_store']}")
        print(f"storage: {summary['storage_status']}")
        print(summary["storage_message"])
    return 0


def cmd_dashboard(root: Path, host: str, port: int, home: Path | None) -> int:
    target_home = home.expanduser().resolve() if home else None
    run_dashboard(host=host, port=port, root=root, home=target_home)
    return 0


def cmd_frontier_trail() -> int:
    from .frontier_trail.pitfall import launch_cli

    return launch_cli()


def cmd_doctor(root: Path, applications_dir: Path | None, as_json: bool) -> int:
    ensure_runtime_dirs(root)
    app_dir = applications_dir.expanduser().resolve() if applications_dir else None
    report = health_report(root, app_dir)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"venvWin health: {report['overall']}")
        print(f"runtime root: {report['root']}")
        for check in report["checks"]:
            print(f"[{check['status']}] {check['name']}: {check['message']}")
    return 1 if report["overall"] == "error" else 0


def cmd_storage(as_json: bool) -> int:
    report = persistence_report()
    if as_json:
        print(json.dumps(report, indent=2))
        return 0

    chosen = report["chosen"]
    print("venvWin storage")
    print(f"chosen: {chosen['path']}")
    print(f"source: {chosen['source']}")
    print(f"writable: {chosen['writable']}")
    print(f"portable-owned: {chosen['portable_owned']}")
    print(f"host-risk: {chosen['host_risk']}")
    if report["leave_no_trace"]:
        print("leave-no-trace: ok, writing to venvWin-owned portable storage")
    elif report["disposable_warning"]:
        print("leave-no-trace: warning, no venvWin-owned persistent storage found; this may be disposable")
    elif report["host_write_warning"]:
        print("leave-no-trace: warning, selected storage may be a host path; choose that only on purpose")
    else:
        print("leave-no-trace: unknown, inspect before trusting this environment")
    return 0


def cmd_associate(applications_dir: Path | None) -> int:
    target_dir = applications_dir.expanduser().resolve() if applications_dir else default_applications_dir()
    paths = write_file_association_handlers(target_dir)
    for path in paths:
        print(f"Wrote handler: {path}")
    print("Set these handlers as defaults for EXE/MSI in your desktop environment if needed.")
    return 0


def cmd_open(root: Path, file_path: Path, dry_run: bool, profile_name: str) -> int:
    ensure_runtime_dirs(root)
    result = open_windows_file(
        capsules_dir(root),
        profiles_dir(root),
        file_path.expanduser().resolve(),
        dry_run=dry_run,
        profile_name=profile_name,
    )
    print(json.dumps(result, indent=2))
    return int(result.get("exit_code") or 0)


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


def cmd_install(root: Path, capsule_id: str, installer_path: Path, dry_run: bool, no_copy: bool) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    result = install_into_capsule(
        capsules_dir(root),
        capsule,
        installer_path.expanduser().resolve(),
        dry_run=dry_run,
        copy_installer=not no_copy,
    )
    print(json.dumps(result, indent=2))
    return int(result.get("exit_code") or 0)


def cmd_snapshot_create(root: Path, capsule_id: str, label: str | None) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    record = create_snapshot(capsules_dir(root), capsule, label)
    print(json.dumps(record, indent=2))
    return 0


def cmd_snapshot_restore(root: Path, capsule_id: str, snapshot_file: Path) -> int:
    ensure_runtime_dirs(root)
    record = restore_snapshot(capsules_dir(root), capsule_id, snapshot_file.expanduser().resolve())
    print(json.dumps(record, indent=2))
    return 0


def cmd_reset(root: Path, capsule_id: str) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    record = reset_capsule_prefix(capsules_dir(root), capsule)
    print(json.dumps(record, indent=2))
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


def cmd_launcher_create(root: Path, capsule_id: str, name: str, executable_path: str, output_dir: Path | None) -> int:
    ensure_runtime_dirs(root)
    capsule = load_capsule(capsules_dir(root), capsule_id)
    path = generate_desktop_launcher(
        capsules_dir(root),
        capsule,
        name,
        executable_path,
        output_dir.expanduser().resolve() if output_dir else None,
    )
    print(f"Created launcher: {path}")
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
        if args.command == "bootstate":
            return cmd_bootstate(args.json, args.write)
        if args.command == "frontier-trail":
            return cmd_frontier_trail()
        if args.command == "first-run":
            return cmd_first_run(args.home, args.wizard_text, args.json)
        if args.command == "dashboard":
            return cmd_dashboard(root, args.host, args.port, args.home)
        if args.command == "doctor":
            return cmd_doctor(root, args.applications_dir, args.json)
        if args.command == "storage":
            return cmd_storage(args.json)
        if args.command == "associate":
            return cmd_associate(args.applications_dir)
        if args.command == "open":
            return cmd_open(root, args.file_path, args.dry_run, args.profile)
        if args.command == "profile" and args.profile_command == "default":
            return cmd_profile_default(root)
        if args.command == "create":
            return cmd_create(root, args.app_name, args.profile)
        if args.command == "list":
            return cmd_list(root)
        if args.command == "inspect":
            return cmd_inspect(root, args.capsule_id)
        if args.command == "install":
            return cmd_install(root, args.capsule_id, args.installer_path, args.dry_run, args.no_copy)
        if args.command == "snapshot" and args.snapshot_command == "create":
            return cmd_snapshot_create(root, args.capsule_id, args.label)
        if args.command == "snapshot" and args.snapshot_command == "restore":
            return cmd_snapshot_restore(root, args.capsule_id, args.snapshot_file)
        if args.command == "reset":
            return cmd_reset(root, args.capsule_id)
        if args.command == "install-command":
            return cmd_install_command(root, args.capsule_id, args.installer_path)
        if args.command == "launch-command":
            return cmd_launch_command(root, args.capsule_id, args.executable_path)
        if args.command == "launcher" and args.launcher_command == "create":
            return cmd_launcher_create(root, args.capsule_id, args.name, args.executable_path, args.output_dir)
        if args.command == "record-launcher":
            return cmd_record_launcher(root, args.capsule_id, args.name, args.executable_path)
    except Exception as exc:
        print(f"venvwin: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
