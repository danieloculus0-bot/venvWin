from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass

WIDTH = 860
HEIGHT = 560
TICK_MS = 16
BALL_SIZE = 12
PADDLE_H = 16

BRICK_LABELS = [
    "BLOAT",
    "SPYWARE",
    "FORCED UPDATE",
    "PREFIX HELL",
    "OLD DRIVER",
    "LAG",
    "TOOLBAR",
    "OEM CRAP",
    "CLOUD TAX",
    "32-BIT GHOST",
]

POWERUPS = ["WIDE", "SLOW", "LNT", "MULTI"]


@dataclass
class Ball:
    x: float
    y: float
    dx: float
    dy: float
    size: int = BALL_SIZE


@dataclass
class Drop:
    item: int
    kind: str
    dy: float = 2.0


class DanielBooneGame:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Daniel Boone: Bloat Breaker")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#0b1020", highlightthickness=0)
        self.canvas.pack()

        self.level = 1
        self.score = 0
        self.lives = 3
        self.rescue = 0
        self.running = True
        self.paddle_w = 128
        self.paddle_x = WIDTH // 2 - self.paddle_w // 2
        self.balls: list[Ball] = []
        self.bricks: list[int] = []
        self.drops: list[Drop] = []
        self.flash = ""
        self.flash_ticks = 0

        self._bind()
        self._reset_level()
        self.root.after(TICK_MS, self._tick)

    def _bind(self) -> None:
        self.root.bind("<Left>", lambda _e: self._move(-42))
        self.root.bind("<Right>", lambda _e: self._move(42))
        self.root.bind("a", lambda _e: self._move(-42))
        self.root.bind("A", lambda _e: self._move(-42))
        self.root.bind("d", lambda _e: self._move(42))
        self.root.bind("D", lambda _e: self._move(42))
        self.root.bind("<space>", lambda _e: self._pause())
        self.root.bind("r", lambda _e: self._new_game())
        self.root.bind("R", lambda _e: self._new_game())
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

    def _new_game(self) -> None:
        self.level = 1
        self.score = 0
        self.lives = 3
        self.rescue = 0
        self.running = True
        self.paddle_w = 128
        self._reset_level()

    def _reset_level(self) -> None:
        self.canvas.delete("all")
        self.bricks.clear()
        self.drops.clear()
        speed = 4.0 + min(self.level * 0.35, 2.2)
        self.balls = [Ball(WIDTH / 2, HEIGHT - 92, random.choice([-speed, speed]), -speed)]
        self.paddle_x = WIDTH // 2 - self.paddle_w // 2
        self._make_bricks()
        self._draw()
        self._say(f"Level {self.level}: rescue the old hardware")

    def _make_bricks(self) -> None:
        rows = min(4 + self.level, 8)
        cols = 8
        brick_w = 94
        brick_h = 24
        start_x = 31
        start_y = 88
        for row in range(rows):
            for col in range(cols):
                x1 = start_x + col * (brick_w + 8)
                y1 = start_y + row * (brick_h + 8)
                x2 = x1 + brick_w
                y2 = y1 + brick_h
                hp = 1 + (1 if self.level >= 3 and row < 2 and random.random() < 0.35 else 0)
                fill = "#374151" if hp == 1 else "#4b5563"
                brick = self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#93c5fd", tags=("brick", f"hp:{hp}"))
                self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=random.choice(BRICK_LABELS),
                    fill="#f9fafb",
                    font=("Sans", 7, "bold"),
                    tags=("brick-label", f"label-{brick}"),
                )
                self.bricks.append(brick)

    def _move(self, amount: int) -> None:
        self.paddle_x = max(12, min(WIDTH - self.paddle_w - 12, self.paddle_x + amount))
        self._draw()

    def _pause(self) -> None:
        self.running = not self.running
        self._say("Paused" if not self.running else "Back to work")

    def _say(self, text: str) -> None:
        self.flash = text
        self.flash_ticks = 120

    def _draw(self) -> None:
        self.canvas.delete("hud", "paddle", "ball", "drop", "message")
        self._draw_background()
        self.canvas.create_text(WIDTH // 2, 22, text="Daniel Boone: Bloat Breaker", fill="#f9fafb", font=("Sans", 20, "bold"), tags="hud")
        self.canvas.create_text(WIDTH // 2, 47, text="One easter egg. Zero host-drive bullshit. Smash bloat and rescue old PCs.", fill="#9ca3af", font=("Sans", 10), tags="hud")
        self.canvas.create_text(76, 24, text=f"Score {self.score}", fill="#d1d5db", font=("Sans", 11, "bold"), tags="hud")
        self.canvas.create_text(76, 47, text=f"Lives {self.lives}", fill="#d1d5db", font=("Sans", 10), tags="hud")
        self.canvas.create_text(WIDTH - 78, 24, text=f"Level {self.level}", fill="#d1d5db", font=("Sans", 11, "bold"), tags="hud")
        self.canvas.create_text(WIDTH - 94, 47, text=f"Rescue {self.rescue}%", fill="#d1d5db", font=("Sans", 10), tags="hud")
        self._draw_rescue_bar()
        if self.flash_ticks > 0:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 28, text=self.flash, fill="#fde68a", font=("Sans", 11, "bold"), tags="message")
        else:
            self.canvas.create_text(WIDTH // 2, HEIGHT - 28, text="Arrows/A-D move. Space pauses. R resets. Esc quits.", fill="#6b7280", font=("Sans", 9), tags="message")

        py = HEIGHT - 68
        self.canvas.create_rectangle(self.paddle_x, py, self.paddle_x + self.paddle_w, py + PADDLE_H, fill="#f59e0b", outline="#fde68a", tags="paddle")
        self.canvas.create_text(self.paddle_x + self.paddle_w / 2, py - 13, text="DANIEL BOONE", fill="#fde68a", font=("Sans", 8, "bold"), tags="paddle")
        for ball in self.balls:
            self.canvas.create_oval(ball.x, ball.y, ball.x + ball.size, ball.y + ball.size, fill="#60a5fa", outline="#bfdbfe", tags="ball")
        for drop in self.drops:
            x1, y1, x2, y2 = self.canvas.coords(drop.item)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=drop.kind, fill="#111827", font=("Sans", 7, "bold"), tags="drop")

    def _draw_background(self) -> None:
        self.canvas.delete("bg")
        for i in range(0, WIDTH, 40):
            shade = "#101827" if (i // 40) % 2 else "#0f172a"
            self.canvas.create_rectangle(i, 64, i + 40, HEIGHT, fill=shade, outline="", tags="bg")

    def _draw_rescue_bar(self) -> None:
        x1, y1, x2, y2 = 250, 62, WIDTH - 250, 72
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#374151", fill="#111827", tags="hud")
        fill_w = (x2 - x1) * max(0, min(self.rescue, 100)) / 100
        self.canvas.create_rectangle(x1, y1, x1 + fill_w, y2, outline="", fill="#22c55e", tags="hud")

    def _tick(self) -> None:
        if self.flash_ticks > 0:
            self.flash_ticks -= 1
        if self.running:
            self._move_balls()
            self._move_drops()
        self._draw()
        self.root.after(TICK_MS, self._tick)

    def _move_balls(self) -> None:
        py = HEIGHT - 68
        still_alive: list[Ball] = []
        for ball in self.balls:
            ball.x += ball.dx
            ball.y += ball.dy
            if ball.x <= 0 or ball.x >= WIDTH - ball.size:
                ball.dx *= -1
            if ball.y <= 64:
                ball.dy = abs(ball.dy)
            if py - ball.size <= ball.y <= py + PADDLE_H and self.paddle_x <= ball.x <= self.paddle_x + self.paddle_w:
                hit = (ball.x - self.paddle_x) / self.paddle_w - 0.5
                ball.dx = hit * (7.0 + self.level * 0.2)
                ball.dy = -abs(ball.dy)
            self._hit_bricks(ball)
            if ball.y <= HEIGHT:
                still_alive.append(ball)
        self.balls = still_alive
        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self._game_over("Bloat won. Press R and rescue that old PC again.")
            else:
                speed = 4.0 + min(self.level * 0.35, 2.2)
                self.balls = [Ball(WIDTH / 2, HEIGHT - 92, random.choice([-speed, speed]), -speed)]
                self._say("Ball lost. Daniel reloads.")
        if not self.bricks and self.lives > 0:
            self.level += 1
            self.rescue = min(100, self.rescue + 20)
            self.paddle_w = max(96, self.paddle_w - 4)
            if self.rescue >= 100:
                self._game_over("All bloat destroyed. Old hardware lives again. Hell yeah.")
            else:
                self._reset_level()

    def _hit_bricks(self, ball: Ball) -> None:
        for brick in list(self.bricks):
            coords = self.canvas.coords(brick)
            if not coords:
                continue
            x1, y1, x2, y2 = coords
            if x1 <= ball.x <= x2 and y1 <= ball.y <= y2:
                tags = self.canvas.gettags(brick)
                hp = 1
                for tag in tags:
                    if tag.startswith("hp:"):
                        hp = int(tag.split(":", 1)[1])
                        break
                if hp > 1:
                    self.canvas.itemconfig(brick, fill="#6b7280", tags=("brick", f"hp:{hp - 1}"))
                else:
                    self.canvas.delete(brick)
                    self.canvas.delete(f"label-{brick}")
                    self.bricks.remove(brick)
                    self.score += 10 * self.level
                    if random.random() < 0.12:
                        self._spawn_powerup((x1 + x2) / 2, (y1 + y2) / 2)
                ball.dy *= -1
                return

    def _spawn_powerup(self, x: float, y: float) -> None:
        kind = random.choice(POWERUPS)
        item = self.canvas.create_rectangle(x - 18, y - 10, x + 18, y + 10, fill="#a7f3d0", outline="#34d399")
        self.drops.append(Drop(item=item, kind=kind, dy=2.2 + self.level * 0.15))

    def _move_drops(self) -> None:
        py = HEIGHT - 68
        for drop in list(self.drops):
            self.canvas.move(drop.item, 0, drop.dy)
            coords = self.canvas.coords(drop.item)
            if not coords:
                self.drops.remove(drop)
                continue
            x1, y1, x2, y2 = coords
            if y2 > HEIGHT:
                self.canvas.delete(drop.item)
                self.drops.remove(drop)
                continue
            if py <= y2 <= py + PADDLE_H + 8 and self.paddle_x <= (x1 + x2) / 2 <= self.paddle_x + self.paddle_w:
                self._apply_powerup(drop.kind)
                self.canvas.delete(drop.item)
                self.drops.remove(drop)

    def _apply_powerup(self, kind: str) -> None:
        if kind == "WIDE":
            self.paddle_w = min(190, self.paddle_w + 28)
            self._say("WIDE paddle: more Daniel per pixel")
        elif kind == "SLOW":
            for ball in self.balls:
                ball.dx *= 0.82
                ball.dy *= 0.82
            self._say("SLOW: bloat gets less twitchy")
        elif kind == "LNT":
            self.score += 75
            self.rescue = min(100, self.rescue + 5)
            self._say("LNT: host drive untouched")
        elif kind == "MULTI":
            if self.balls:
                b = self.balls[0]
                self.balls.append(Ball(b.x, b.y, -b.dx or 4.0, b.dy, b.size))
            self._say("MULTI: compatibility layer engaged")

    def _game_over(self, message: str) -> None:
        self.running = False
        self.canvas.create_rectangle(90, 200, WIDTH - 90, 330, fill="#030712", outline="#93c5fd", tags="message")
        self.canvas.create_text(WIDTH // 2, 235, text=message, fill="#f9fafb", font=("Sans", 15, "bold"), tags="message")
        self.canvas.create_text(WIDTH // 2, 270, text=f"Final score: {self.score}", fill="#d1d5db", font=("Sans", 12), tags="message")
        self.canvas.create_text(WIDTH // 2, 300, text="Press R to restart or Esc to quit", fill="#9ca3af", font=("Sans", 11), tags="message")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    DanielBooneGame().run()


if __name__ == "__main__":
    main()
