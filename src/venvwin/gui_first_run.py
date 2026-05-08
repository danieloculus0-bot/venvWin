from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .first_run import PUBLIC_PRODUCT_NAME, first_run_summary, write_first_run_files

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - GUI runtime dependency may be absent in headless preflight
    tk = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]

BG = "#070b10"
PANEL = "#111827"
CARD = "#1f2937"
CARD_SOFT = "#16202b"
TEXT = "#eef6ff"
MUTED = "#a7b4c0"
ACCENT = "#38bdf8"
GOOD = "#22c55e"
WARN = "#f59e0b"
BAD = "#ef4444"
BUTTON = "#263449"
BUTTON_ACTIVE = "#334762"
START = "#1f6feb"


def status_color(status: str) -> str:
    if status == "leave-no-trace-ok":
        return GOOD
    if "warning" in status:
        return WARN
    return BAD


def display_model(home: Path | None = None) -> dict[str, str]:
    summary = first_run_summary(home)
    return {
        "product_name": str(summary["product_name"]),
        "capsule_store": str(summary["capsule_store"]),
        "storage_status": str(summary["storage_status"]),
        "storage_message": str(summary["storage_message"]),
        "dashboard_url": str(summary["dashboard_url"]),
        "leave_no_trace": "ON" if summary["leave_no_trace"] else "CHECK STORAGE",
        "portable_owned": "YES" if summary["portable_owned"] else "NO",
        "host_risk": "YES" if summary["host_risk"] else "NO",
    }


class VenvWinFirstRunApp:
    def __init__(self, root, home: Path | None = None) -> None:
        if tk is None:
            raise RuntimeError(f"Tkinter is not available. Install python3-tk before launching the {PUBLIC_PRODUCT_NAME} first-boot GUI.")
        self.root = root
        self.home = home
        self.model = display_model(home)
        self.summary = first_run_summary(home)
        self.capsule_store = Path(self.summary["capsule_store"])

        self.root.title(f"{PUBLIC_PRODUCT_NAME} First Boot")
        self.root.geometry("980x640")
        self.root.minsize(900, 590)
        self.root.configure(bg=BG)
        self.build_ui()

    def label(self, parent, text: str, size: int = 11, color: str = TEXT, bold: bool = False, wrap: int = 720):
        weight = "bold" if bold else "normal"
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color, font=("Sans", size, weight), anchor="w", justify="left", wraplength=wrap)

    def button(self, parent, text: str, command, primary: bool = False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=START if primary else BUTTON,
            fg=TEXT,
            activebackground=BUTTON_ACTIVE,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=16,
            pady=10,
            font=("Sans", 10, "bold"),
            cursor="hand2",
        )

    def build_ui(self) -> None:
        shell = tk.Frame(self.root, bg=BG, padx=26, pady=24)
        shell.pack(fill="both", expand=True)

        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x")
        self.label(header, PUBLIC_PRODUCT_NAME, 30, TEXT, True).pack(anchor="w")
        self.label(header, "First boot setup for portable Windows-app capsules.", 13, MUTED).pack(anchor="w", pady=(6, 0))

        main = tk.Frame(shell, bg=BG)
        main.pack(fill="both", expand=True, pady=(20, 0))

        start_panel = tk.Frame(main, bg=PANEL, padx=16, pady=16, width=220)
        start_panel.pack(side="left", fill="y", padx=(0, 14))
        start_panel.pack_propagate(False)

        center = tk.Frame(main, bg=PANEL, padx=20, pady=20)
        center.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right = tk.Frame(main, bg=PANEL, padx=20, pady=20, width=300)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.start_panel(start_panel)
        self.storage_card(center)
        self.action_card(center)
        self.status_panel(right)

        footer = tk.Frame(shell, bg=BG)
        footer.pack(fill="x", pady=(14, 0))
        self.label(footer, "Default promise: app state goes to the portable capsule store, host storage stays clean, and broken app bullshit stays recoverable.", 10, MUTED).pack(anchor="w")

    def start_panel(self, parent) -> None:
        self.label(parent, "Start", 18, TEXT, True).pack(anchor="w")
        self.label(parent, "Quick launch", 10, MUTED).pack(anchor="w", pady=(2, 12))
        self.button(parent, "Initialize Storage", self.initialize, True).pack(fill="x", pady=(0, 9))
        self.button(parent, "Open Dashboard", self.open_dashboard).pack(fill="x", pady=(0, 9))
        self.button(parent, "Open Capsules", self.open_capsules).pack(fill="x", pady=(0, 9))
        self.button(parent, "Run Doctor", self.run_doctor).pack(fill="x", pady=(0, 9))
        self.button(parent, "Private Browser", self.private_browser).pack(fill="x")

        spacer = tk.Frame(parent, bg=PANEL)
        spacer.pack(fill="both", expand=True)
        info = tk.Frame(parent, bg=CARD_SOFT, padx=12, pady=12)
        info.pack(fill="x", pady=(14, 0))
        self.label(info, "Familiar desktop flow. Not a Windows clone.", 9, MUTED, wrap=170).pack(anchor="w")

    def storage_card(self, parent) -> None:
        card = tk.Frame(parent, bg=CARD, padx=18, pady=18)
        card.pack(fill="x")
        self.label(card, "This PC: Capsule Storage", 17, TEXT, True).pack(anchor="w")
        self.label(card, self.model["storage_message"], 11, MUTED).pack(anchor="w", pady=(8, 14))

        path = tk.Frame(card, bg=BG, padx=12, pady=12)
        path.pack(fill="x")
        self.label(path, self.model["capsule_store"], 10, ACCENT).pack(anchor="w")

        dash = tk.Frame(card, bg=CARD_SOFT, padx=12, pady=10)
        dash.pack(fill="x", pady=(12, 0))
        self.label(dash, f"Dashboard: {self.model['dashboard_url']}", 10, MUTED).pack(anchor="w")

    def action_card(self, parent) -> None:
        card = tk.Frame(parent, bg=CARD, padx=18, pady=18)
        card.pack(fill="x", pady=(16, 0))
        self.label(card, "Control Panel", 17, TEXT, True).pack(anchor="w")
        self.label(card, "Initialize storage, verify the system, then run apps from capsules.", 11, MUTED).pack(anchor="w", pady=(7, 12))

        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x")
        self.button(row, "Initialize", self.initialize, True).pack(side="left", padx=(0, 10))
        self.button(row, "Dashboard", self.open_dashboard).pack(side="left", padx=(0, 10))
        self.button(row, "Doctor", self.run_doctor).pack(side="left", padx=(0, 10))
        self.button(row, "Capsules", self.open_capsules).pack(side="left")

    def status_panel(self, parent) -> None:
        self.label(parent, "System Status", 17, TEXT, True).pack(anchor="w")
        self.badge(parent, "Leave no trace", self.model["leave_no_trace"], status_color(self.model["storage_status"]))
        self.badge(parent, "Portable storage", self.model["portable_owned"], GOOD if self.model["portable_owned"] == "YES" else WARN)
        self.badge(parent, "Host write risk", self.model["host_risk"], BAD if self.model["host_risk"] == "YES" else GOOD)

        note = tk.Frame(parent, bg=CARD_SOFT, padx=14, pady=14)
        note.pack(fill="x", pady=(18, 0))
        self.label(note, "If host risk says YES, do not install apps until storage is corrected or intentionally selected.", 10, MUTED, wrap=250).pack(anchor="w")

    def badge(self, parent, title: str, value: str, color: str) -> None:
        box = tk.Frame(parent, bg=CARD, padx=14, pady=12)
        box.pack(fill="x", pady=(12, 0))
        self.label(box, title, 10, MUTED).pack(anchor="w")
        self.label(box, value, 19, color, True).pack(anchor="w", pady=(2, 0))

    def initialize(self) -> None:
        summary = write_first_run_files(self.home)
        messagebox.showinfo(f"{PUBLIC_PRODUCT_NAME} ready", f"Capsule storage initialized:\n{summary['capsule_store']}")

    def open_dashboard(self) -> None:
        for command in (["xdg-open", self.model["dashboard_url"]],):
            try:
                subprocess.Popen(command)
                return
            except OSError:
                continue
        messagebox.showwarning("Open dashboard", f"Open manually:\n{self.model['dashboard_url']}")

    def open_capsules(self) -> None:
        self.capsule_store.mkdir(parents=True, exist_ok=True)
        for command in (["xdg-open", str(self.capsule_store)], ["thunar", str(self.capsule_store)]):
            try:
                subprocess.Popen(command)
                return
            except OSError:
                continue
        messagebox.showwarning("Open folder", f"Open manually:\n{self.capsule_store}")

    def run_doctor(self) -> None:
        for command in (["xfce4-terminal", "-e", "venvwin doctor"], ["x-terminal-emulator", "-e", "venvwin doctor"]):
            try:
                subprocess.Popen(command)
                return
            except OSError:
                continue
        messagebox.showwarning("Run Doctor", "Open a terminal and run: venvwin doctor")

    def private_browser(self) -> None:
        try:
            subprocess.Popen(["venvwin-private-browser"])
        except OSError:
            messagebox.showwarning("Private browser", "Open a terminal and run: venvwin-private-browser")


def main(argv: list[str] | None = None) -> int:
    if tk is None:
        print(f"{PUBLIC_PRODUCT_NAME} first-boot GUI requires Tkinter. Install python3-tk.", file=sys.stderr)
        return 1
    args = argv or sys.argv[1:]
    home = Path(args[0]).expanduser().resolve() if args else None
    root = tk.Tk()
    VenvWinFirstRunApp(root, home)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
