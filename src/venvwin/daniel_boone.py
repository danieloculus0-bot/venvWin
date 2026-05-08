from __future__ import annotations

import random
import tkinter as tk

CELL = 24
COLS = 10
ROWS = 20
SIDE = 220
WIDTH = COLS * CELL + SIDE
HEIGHT = ROWS * CELL
TICK_START = 650

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

COLORS = ["#60a5fa", "#f59e0b", "#22c55e", "#a78bfa", "#ef4444", "#14b8a6", "#eab308"]
BLOAT_WORDS = ["BLOAT", "LAG", "SPY", "OEM", "UPDATE", "TOOLBAR", "DRIVER", "CLOUD", "PREFIX", "CRAP"]


def rotate(shape: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*shape[::-1])]


class DanielBooneTetris:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Daniel Boone: Bloat Stacker")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#0b1020", highlightthickness=0)
        self.canvas.pack()

        self.grid: list[list[str | None]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.running = True
        self.game_over = False
        self.flash = "Stack bloat. Clear lines. Rescue old PCs."
        self.piece: dict[str, object] = {}
        self.next_piece: dict[str, object] = self._new_piece()

        self._bind()
        self._spawn()
        self._draw()
        self.root.after(TICK_START, self._tick)

    def _bind(self) -> None:
        self.root.bind("<Left>", lambda _e: self._move(-1, 0))
        self.root.bind("<Right>", lambda _e: self._move(1, 0))
        self.root.bind("<Down>", lambda _e: self._soft_drop())
        self.root.bind("<Up>", lambda _e: self._rotate_piece())
        self.root.bind("<space>", lambda _e: self._hard_drop())
        self.root.bind("p", lambda _e: self._pause())
        self.root.bind("P", lambda _e: self._pause())
        self.root.bind("r", lambda _e: self._reset())
        self.root.bind("R", lambda _e: self._reset())
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

    def _new_piece(self) -> dict[str, object]:
        name = random.choice(list(SHAPES))
        return {
            "name": name,
            "shape": [row[:] for row in SHAPES[name]],
            "x": COLS // 2 - 2,
            "y": 0,
            "color": random.choice(COLORS),
            "word": random.choice(BLOAT_WORDS),
        }

    def _spawn(self) -> None:
        self.piece = self.next_piece
        self.piece["x"] = COLS // 2 - 2
        self.piece["y"] = 0
        self.next_piece = self._new_piece()
        if self._collides(self.piece["shape"], int(self.piece["x"]), int(self.piece["y"])):
            self.game_over = True
            self.running = False
            self.flash = "Bloat won. Press R to reboot the rescue."

    def _collides(self, shape: list[list[int]], px: int, py: int) -> bool:
        for y, row in enumerate(shape):
            for x, filled in enumerate(row):
                if not filled:
                    continue
                gx = px + x
                gy = py + y
                if gx < 0 or gx >= COLS or gy >= ROWS:
                    return True
                if gy >= 0 and self.grid[gy][gx] is not None:
                    return True
        return False

    def _move(self, dx: int, dy: int) -> bool:
        if not self.running or self.game_over:
            return False
        nx = int(self.piece["x"]) + dx
        ny = int(self.piece["y"]) + dy
        if not self._collides(self.piece["shape"], nx, ny):
            self.piece["x"] = nx
            self.piece["y"] = ny
            self._draw()
            return True
        return False

    def _soft_drop(self) -> None:
        if self._move(0, 1):
            self.score += 1
        else:
            self._lock()

    def _hard_drop(self) -> None:
        if not self.running or self.game_over:
            return
        dropped = 0
        while self._move(0, 1):
            dropped += 1
        self.score += dropped * 2
        self._lock()

    def _rotate_piece(self) -> None:
        if not self.running or self.game_over:
            return
        rotated = rotate(self.piece["shape"])
        px = int(self.piece["x"])
        py = int(self.piece["y"])
        for kick in (0, -1, 1, -2, 2):
            if not self._collides(rotated, px + kick, py):
                self.piece["shape"] = rotated
                self.piece["x"] = px + kick
                self._draw()
                return

    def _lock(self) -> None:
        shape = self.piece["shape"]
        px = int(self.piece["x"])
        py = int(self.piece["y"])
        color = str(self.piece["color"])
        for y, row in enumerate(shape):
            for x, filled in enumerate(row):
                if filled and 0 <= py + y < ROWS:
                    self.grid[py + y][px + x] = color
        self._clear_lines()
        self._spawn()
        self._draw()

    def _clear_lines(self) -> None:
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(new_grid)
        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(COLS)])
        self.grid = new_grid
        if cleared:
            self.lines += cleared
            self.level = 1 + self.lines // 8
            self.score += [0, 100, 300, 500, 800][cleared] * self.level
            self.flash = f"{cleared} line{'s' if cleared > 1 else ''} cleared. Host drive still clean."

    def _pause(self) -> None:
        if self.game_over:
            return
        self.running = not self.running
        self.flash = "Paused" if not self.running else "Back to rescuing old PCs"
        self._draw()

    def _reset(self) -> None:
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.running = True
        self.game_over = False
        self.flash = "Stack bloat. Clear lines. Rescue old PCs."
        self.next_piece = self._new_piece()
        self._spawn()
        self._draw()

    def _tick(self) -> None:
        if self.running and not self.game_over:
            if not self._move(0, 1):
                self._lock()
        delay = max(120, TICK_START - (self.level - 1) * 55)
        self.root.after(delay, self._tick)

    def _draw_cell(self, x: int, y: int, color: str, text: str = "") -> None:
        x1 = x * CELL
        y1 = y * CELL
        self.canvas.create_rectangle(x1 + 1, y1 + 1, x1 + CELL - 1, y1 + CELL - 1, fill=color, outline="#111827")
        if text:
            self.canvas.create_text(x1 + CELL / 2, y1 + CELL / 2, text=text[:3], fill="#0b1020", font=("Sans", 6, "bold"))

    def _draw(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, COLS * CELL, HEIGHT, fill="#111827", outline="#374151")
        for x in range(COLS + 1):
            self.canvas.create_line(x * CELL, 0, x * CELL, HEIGHT, fill="#1f2937")
        for y in range(ROWS + 1):
            self.canvas.create_line(0, y * CELL, COLS * CELL, y * CELL, fill="#1f2937")
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    self._draw_cell(x, y, color)
        if not self.game_over:
            shape = self.piece["shape"]
            px = int(self.piece["x"])
            py = int(self.piece["y"])
            for y, row in enumerate(shape):
                for x, filled in enumerate(row):
                    if filled:
                        self._draw_cell(px + x, py + y, str(self.piece["color"]), str(self.piece["word"]))
        sx = COLS * CELL + 20
        self.canvas.create_text(sx, 28, anchor="w", text="Daniel Boone", fill="#f9fafb", font=("Sans", 18, "bold"))
        self.canvas.create_text(sx, 54, anchor="w", text="Bloat Stacker", fill="#fde68a", font=("Sans", 14, "bold"))
        self.canvas.create_text(sx, 88, anchor="w", text=f"Score: {self.score}", fill="#d1d5db", font=("Sans", 11))
        self.canvas.create_text(sx, 112, anchor="w", text=f"Lines: {self.lines}", fill="#d1d5db", font=("Sans", 11))
        self.canvas.create_text(sx, 136, anchor="w", text=f"Level: {self.level}", fill="#d1d5db", font=("Sans", 11))
        self.canvas.create_text(sx, 174, anchor="w", text="Next", fill="#9ca3af", font=("Sans", 10, "bold"))
        self._draw_next(sx, 198)
        self.canvas.create_text(sx, 315, anchor="w", text="Controls", fill="#9ca3af", font=("Sans", 10, "bold"))
        controls = ["Left/Right: move", "Up: rotate", "Down: drop", "Space: slam", "P: pause", "R: reset", "Esc: quit"]
        for i, line in enumerate(controls):
            self.canvas.create_text(sx, 340 + i * 20, anchor="w", text=line, fill="#d1d5db", font=("Sans", 9))
        self.canvas.create_text(sx, HEIGHT - 42, anchor="w", text="One easter egg only.", fill="#60a5fa", font=("Sans", 9, "bold"))
        self.canvas.create_text(sx, HEIGHT - 22, anchor="w", text="No host-drive writes by default.", fill="#22c55e", font=("Sans", 9, "bold"))
        self.canvas.create_text(COLS * CELL / 2, HEIGHT - 16, text=self.flash, fill="#fde68a", font=("Sans", 9, "bold"))
        if self.game_over:
            self.canvas.create_rectangle(18, 190, COLS * CELL - 18, 300, fill="#030712", outline="#93c5fd")
            self.canvas.create_text(COLS * CELL / 2, 225, text="GAME OVER", fill="#f9fafb", font=("Sans", 20, "bold"))
            self.canvas.create_text(COLS * CELL / 2, 260, text="Press R to restart", fill="#9ca3af", font=("Sans", 12))
        elif not self.running:
            self.canvas.create_text(COLS * CELL / 2, 240, text="PAUSED", fill="#f9fafb", font=("Sans", 20, "bold"))

    def _draw_next(self, sx: int, sy: int) -> None:
        shape = self.next_piece["shape"]
        color = str(self.next_piece["color"])
        for y, row in enumerate(shape):
            for x, filled in enumerate(row):
                if filled:
                    x1 = sx + x * 20
                    y1 = sy + y * 20
                    self.canvas.create_rectangle(x1, y1, x1 + 18, y1 + 18, fill=color, outline="#111827")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    DanielBooneTetris().run()


if __name__ == "__main__":
    main()
