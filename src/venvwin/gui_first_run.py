from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .first_run import PUBLIC_PRODUCT_NAME, first_run_summary, write_first_run_files

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:  # pragma: no cover - GUI runtime dependency may be absent in headless preflight
    tk = None  # type: ignore[assignment]
    filedialog = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]

BG = "#050505"
DESKTOP = "#090909"
TITLE = "#242424"
PANEL = "#121212"
CARD = "#181818"
CARD_SOFT = "#202020"
BORDER = "#4a4a4a"
TEXT = "#f4f1ea"
MUTED = "#aaa39a"
ACCENT = "#ff8a00"
ACCENT_DARK = "#b65300"
GOOD = "#68b957"
BAD = "#e04436"
BUTTON = "#242424"
BUTTON_ACTIVE = "#333333"
FONT = "Segoe UI"


def status_color(status: str) -> str:
    return GOOD if status == "leave-no-trace-ok" else BAD


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

        self.root.title(f"{PUBLIC_PRODUCT_NAME} Control Center")
        self.root.geometry("1040x650")
        self.root.minsize(940, 600)
        self.root.configure(bg=BG)
        self.build_ui()

    def label(self, parent, text: str, size: int = 10, color: str = TEXT, bold: bool = False, wrap: int = 720):
        weight = "bold" if bold else "normal"
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color, font=(FONT, size, weight), anchor="w", justify="left", wraplength=wrap)

    def frame(self, parent, bg: str = PANEL, padx: int = 0, pady: int = 0):
        return tk.Frame(parent, bg=bg, padx=padx, pady=pady, highlightbackground=BORDER, highlightthickness=1)

    def button(self, parent, text: str, command, primary: bool = False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=ACCENT if primary else BUTTON,
            fg="#111111" if primary else TEXT,
            activebackground=ACCENT_DARK if primary else BUTTON_ACTIVE,
            activeforeground="#111111" if primary else TEXT,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground="#ffb45b" if primary else BORDER,
            padx=14,
            pady=9,
            font=(FONT, 10, "bold"),
            cursor="hand2",
        )

    def build_ui(self) -> None:
        shell = tk.Frame(self.root, bg=BG, padx=18, pady=18)
        shell.pack(fill="both", expand=True)

        window = self.frame(shell, DESKTOP, 0, 0)
        window.pack(fill="both", expand=True)

        titlebar = tk.Frame(window, bg=TITLE, height=34)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)
        self.draw_mini_logo(titlebar).pack(side="left", padx=(10, 8), pady=7)
        self.label(titlebar, f"{PUBLIC_PRODUCT_NAME} Control Center", 11, TEXT, True).pack(side="left", fill="y")
        for mark, close in [("_", False), ("□", False), ("×", True)]:
            b = tk.Label(titlebar, text=mark, bg=BAD if close else "#303030", fg="#ffffff", width=4, font=(FONT, 10, "bold"), relief="solid", bd=1)
            b.pack(side="right", padx=(0, 6), pady=5)

        main = tk.Frame(window, bg=DESKTOP, padx=12, pady=12)
        main.pack(fill="both", expand=True)

        left = self.frame(main, PANEL, 10, 10)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=230)
        left.pack_propagate(False)

        center = tk.Frame(main, bg=DESKTOP)
        center.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = self.frame(main, PANEL, 12, 12)
        right.pack(side="right", fill="y")
        right.configure(width=310)
        right.pack_propagate(False)

        self.start_panel(left)
        self.splash_card(center)
        self.storage_card(center)
        self.status_panel(right)
        self.taskbar(window)

    def draw_mini_logo(self, parent):
        c = tk.Canvas(parent, width=22, height=18, bg=TITLE, highlightthickness=0)
        c.create_rectangle(2, 2, 9, 9, fill=ACCENT, outline=ACCENT)
        c.create_rectangle(12, 2, 19, 9, fill="#555555", outline="#666666")
        c.create_rectangle(2, 12, 9, 17, fill="#555555", outline="#666666")
        c.create_rectangle(12, 12, 19, 17, fill="#555555", outline="#666666")
        return c

    def start_panel(self, parent) -> None:
        self.label(parent, "Menu", 18, TEXT, True).pack(anchor="w")
        self.label(parent, "venvWin tasks", 10, MUTED).pack(anchor="w", pady=(2, 12))
        self.button(parent, "▶  Run Windows App", self.run_windows_app, True).pack(fill="x", pady=(0, 9))
        self.button(parent, "▤  Initialize Storage", self.initialize).pack(fill="x", pady=(0, 9))
        self.button(parent, "◷  Open Dashboard", self.open_dashboard).pack(fill="x", pady=(0, 9))
        self.button(parent, "▧  Open Capsules", self.open_capsules).pack(fill="x", pady=(0, 9))
        self.button(parent, "+  Run Doctor", self.run_doctor).pack(fill="x", pady=(0, 9))
        self.button(parent, "◌  Private Browser", self.private_browser).pack(fill="x")

        spacer = tk.Frame(parent, bg=PANEL)
        spacer.pack(fill="both", expand=True)
        note = tk.Frame(parent, bg=CARD_SOFT, padx=10, pady=10, highlightbackground=BORDER, highlightthickness=1)
        note.pack(fill="x", pady=(12, 0))
        self.label(note, "Dark desktop shell. Orange actions. Red only when something is actually wrong.", 9, MUTED, wrap=175).pack(anchor="w")

    def splash_card(self, parent) -> None:
        card = self.frame(parent, CARD, 18, 16)
        card.pack(fill="x")
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x")
        logo = tk.Canvas(row, width=112, height=78, bg=CARD, highlightthickness=0)
        logo.pack(side="left", padx=(0, 18))
        logo.create_oval(7, 5, 70, 68, fill="#222222", outline="#555555")
        logo.create_arc(8, 11, 66, 75, start=210, extent=250, outline="#dddddd", width=4)
        logo.create_polygon(1, 34, 28, 23, 42, 37, 28, 48, fill=ACCENT, outline=ACCENT)
        logo.create_rectangle(66, 24, 94, 52, fill=ACCENT, outline="#7c3b00")
        logo.create_rectangle(98, 24, 126, 52, fill="#555555", outline="#666666")
        copy = tk.Frame(row, bg=CARD)
        copy.pack(side="left", fill="both", expand=True)
        self.label(copy, "venvWin Portable", 28, TEXT, True).pack(anchor="w")
        self.label(copy, "Windows app environments for Linux", 14, MUTED).pack(anchor="w", pady=(4, 0))

    def storage_card(self, parent) -> None:
        card = self.frame(parent, CARD, 18, 16)
        card.pack(fill="both", expand=True, pady=(12, 0))
        self.label(card, "Capsule Storage", 18, TEXT, True).pack(anchor="w")
        self.label(card, self.model["storage_message"], 10, MUTED).pack(anchor="w", pady=(7, 12))
        drive = tk.Canvas(card, width=132, height=88, bg=CARD, highlightthickness=0)
        drive.pack(anchor="center", pady=(4, 12))
        drive.create_rectangle(18, 18, 114, 72, fill="#444444", outline="#777777")
        drive.create_rectangle(42, 34, 90, 58, fill="#1a1a1a", outline="#111111")
        path = tk.Frame(card, bg=BG, padx=10, pady=9, highlightbackground=BORDER, highlightthickness=1)
        path.pack(fill="x")
        self.label(path, self.model["capsule_store"], 10, ACCENT, wrap=620).pack(anchor="w")
        self.label(card, "Windows apps run inside isolated capsules. Your host stays clean unless you intentionally change storage.", 10, MUTED).pack(anchor="w", pady=(14, 0))
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", pady=(14, 0))
        self.button(row, "▣ Initialize / Repair", self.initialize, True).pack(side="left", padx=(0, 10))
        self.button(row, "Dashboard", self.open_dashboard).pack(side="left", padx=(0, 10))
        self.button(row, "Doctor", self.run_doctor).pack(side="left")

    def status_panel(self, parent) -> None:
        self.label(parent, "System Status", 18, TEXT, True).pack(anchor="w")
        self.badge(parent, "Leave no trace", "No changes to host system.", self.model["leave_no_trace"], status_color(self.model["storage_status"]))
        self.badge(parent, "Portable storage", "All data stays on portable storage.", self.model["portable_owned"], GOOD if self.model["portable_owned"] == "YES" else BAD)
        self.badge(parent, "Host write risk", "Windows apps cannot write to host system.", self.model["host_risk"], BAD if self.model["host_risk"] == "YES" else GOOD)
        note = tk.Frame(parent, bg=CARD_SOFT, padx=10, pady=10, highlightbackground=BORDER, highlightthickness=1)
        note.pack(fill="x", pady=(16, 0))
        self.label(note, "Green means safe. Red means stop and fix the storage setup before installing apps.", 9, MUTED, wrap=250).pack(anchor="w")

    def badge(self, parent, title: str, sub: str, value: str, color: str) -> None:
        box = tk.Frame(parent, bg=CARD, padx=10, pady=10, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="x", pady=(12, 0))
        top = tk.Frame(box, bg=CARD)
        top.pack(fill="x")
        self.label(top, title, 11, TEXT, True).pack(side="left", anchor="w")
        tk.Label(top, text=value, bg=color, fg="#ffffff" if color == BAD else "#111111", font=(FONT, 10, "bold"), width=8, relief="solid", bd=1).pack(side="right")
        self.label(box, sub, 9, MUTED, wrap=250).pack(anchor="w", pady=(5, 0))

    def taskbar(self, parent) -> None:
        bar = tk.Frame(parent, bg="#111111", height=46, highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Label(bar, text="☰ venvWin", bg=ACCENT, fg="#111111", font=(FONT, 12, "bold"), padx=16).pack(side="left", fill="y", padx=(8, 10), pady=6)
        tk.Label(bar, text=f"{PUBLIC_PRODUCT_NAME} Control Center", bg="#202020", fg=TEXT, font=(FONT, 10), padx=14, relief="solid", bd=1).pack(side="left", fill="y", pady=7)
        tk.Label(bar, text=f"Leave no trace: {self.model['leave_no_trace']}", bg="#111111", fg=MUTED, font=(FONT, 9)).pack(side="right", padx=12)

    def initialize(self) -> None:
        summary = write_first_run_files(self.home)
        messagebox.showinfo(f"{PUBLIC_PRODUCT_NAME} ready", f"Capsule storage initialized:\n{summary['capsule_store']}")

    def run_windows_app(self) -> None:
        if filedialog is None:
            messagebox.showwarning("Run Windows App", "File picker unavailable. Open a terminal and run: venvwin open /path/to/app.exe")
            return
        selected = filedialog.askopenfilename(title="Choose a Windows EXE or MSI", filetypes=[("Windows apps and installers", "*.exe *.msi"), ("All files", "*.*")])
        if not selected:
            return
        try:
            subprocess.Popen(["venvwin", "open", selected])
        except OSError:
            messagebox.showwarning("Run Windows App", f"Open a terminal and run:\nvenvwin open {selected}")

    def open_dashboard(self) -> None:
        try:
            subprocess.Popen(["xdg-open", self.model["dashboard_url"]])
            return
        except OSError:
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
