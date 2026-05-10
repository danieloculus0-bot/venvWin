from __future__ import annotations

import importlib.util
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

_LEGACY_PATH = Path(__file__).resolve().parents[1] / "frontier_trail.py"
_SPEC = importlib.util.spec_from_file_location("venvwin._frontier_trail_legacy", _LEGACY_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover
    raise ImportError(f"Could not load legacy Frontier Trail module at {_LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_legacy)

Member = _legacy.Member
GameState = _legacy.GameState
roll_event = _legacy.roll_event
PARTY_POOL = _legacy.PARTY_POOL
LANDMARKS = _legacy.LANDMARKS
SCENARIOS = _legacy.SCENARIOS

try:
    import tkinter as tk
except Exception:  # pragma: no cover - headless CI may not have Tk
    tk = None  # type: ignore[assignment]

WIDTH = 960
HEIGHT = 620
CANVAS_H = 430
GROUND_Y = 354
FONT = "Segoe UI"
BG = "#050505"
PANEL = "#151515"
PANEL_2 = "#222222"
BORDER = "#4a4a4a"
TEXT = "#f4f1ea"
MUTED = "#aaa39a"
ORANGE = "#ff8a00"
GREEN = "#68b957"
RED = "#e04436"


@dataclass
class Room:
    kind: str
    pit: tuple[int, int] | None = None
    rope_x: int | None = None
    ladder: bool = False
    pickups: list[tuple[int, int, str, bool]] = field(default_factory=list)
    hazards: list[dict] = field(default_factory=list)


class FrontierTrailApp:
    """Pitfall-style rewrite that shadows the older side-scroll module while keeping its model API."""

    def __init__(self, root) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available. Install python3-tk to play Frontier Trail.")
        self.root = root
        self.root.title("Daniel Boone: Frontier Trail")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.minsize(WIDTH, HEIGHT)
        self.root.configure(bg=BG)
        self.state = GameState()
        self.mode = "title"
        self.keys: set[str] = set()
        self.player = {"x": 76.0, "y": 308.0, "vx": 0.0, "vy": 0.0, "w": 20, "h": 34, "ground": False}
        self.room_index = 0
        self.rooms: list[Room] = []
        self.swing = 0
        self.selected_scenario: dict | None = None
        self.roll_result = ""
        self.crosshair = {"x": 480, "y": 210}
        self.animals: list[dict] = []
        self.hunt_food = 0
        self.hunt_shots = 8
        self.hunt_start = 0.0
        self.canvas = tk.Canvas(root, width=WIDTH, height=CANVAS_H, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="x")
        self.info = tk.Frame(root, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.info.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.text = tk.Text(self.info, height=7, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 10), wrap="word")
        self.text.pack(fill="both", expand=True, padx=10, pady=8)
        self.text.configure(state="disabled")
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<Button-1>", self.mouse_click)
        root.bind("<Motion>", self.mouse_move)
        self.tick()

    def key_down(self, event) -> None:
        key = event.keysym.lower()
        self.keys.add(key)
        if self.mode == "title" and key in {"space", "return"}:
            self.mode = "event"
            self.prepare_event()
        elif self.mode == "event" and key in {"1", "2", "3"}:
            self.choose_event(int(key) - 1)
        elif self.mode == "event_done" and key in {"space", "return"}:
            self.start_trail()
        elif self.mode == "trail_done" and key in {"space", "return"}:
            self.after_trail()
        elif self.mode == "hunt_done" and key in {"space", "return"}:
            self.finish_hunt()
        elif self.mode in {"won", "lost"} and key == "r":
            self.reset_game()

    def key_up(self, event) -> None:
        self.keys.discard(event.keysym.lower())

    def mouse_move(self, event) -> None:
        self.crosshair.update({"x": event.x, "y": event.y})

    def mouse_click(self, event) -> None:
        if self.mode == "hunt":
            self.fire_shot(event.x, event.y)

    def reset_game(self) -> None:
        self.state = GameState()
        self.mode = "title"
        self.player.update({"x": 76.0, "y": 308.0, "vx": 0.0, "vy": 0.0})
        self.room_index = 0
        self.rooms = []
        self.selected_scenario = None
        self.roll_result = ""

    def prepare_event(self) -> None:
        self.selected_scenario = random.choice(SCENARIOS)
        self.roll_result = ""

    def choose_event(self, idx: int) -> None:
        if self.selected_scenario is None:
            return
        _, result, _ = roll_event(self.state, self.selected_scenario, idx)
        self.roll_result = result
        self.mode = "event_done"

    def make_room(self, rng: random.Random, index: int) -> Room:
        kind = rng.choice(["pit", "snake", "log", "rope", "ladder", "plain"])
        if index == 0:
            kind = "plain"
        if index >= 5:
            kind = "camp"
        room = Room(kind=kind)
        if kind in {"pit", "rope"}:
            room.pit = (350, 510)
        if kind == "rope":
            room.rope_x = 420
        if kind == "ladder":
            room.ladder = True
            room.pickups.append((455, 290, rng.choice(["furs", "medicine", "powder"]), False))
        if kind in {"snake", "log", "plain"}:
            room.hazards.append({"kind": rng.choice(["snake", "log", "wolf"]), "x": 520.0, "y": GROUND_Y - 26.0, "vx": rng.choice([-1.6, 1.6]), "w": 38, "h": 24})
        if kind == "camp":
            room.pickups.append((820, GROUND_Y - 45, "food", False))
        if rng.random() < 0.75 and kind != "camp":
            room.pickups.append((rng.randint(180, 790), GROUND_Y - rng.randint(50, 110), rng.choice(["food", "powder", "furs", "medicine"]), False))
        return room

    def start_trail(self) -> None:
        self.mode = "trail"
        self.state.consume_travel()
        self.player.update({"x": 76.0, "y": 308.0, "vx": 0.0, "vy": 0.0})
        self.room_index = 0
        rng = random.Random(4200 + self.state.leg * 97 + self.state.days)
        self.rooms = [self.make_room(rng, i) for i in range(6)]

    def after_trail(self) -> None:
        if self.state.is_lost():
            self.mode = "lost"
        elif self.state.leg >= len(LANDMARKS) - 1:
            self.mode = "won"
        elif self.state.food < 10 or self.state.leg in {1, 4}:
            self.start_hunt()
        else:
            self.mode = "event"
            self.prepare_event()

    def start_hunt(self) -> None:
        self.mode = "hunt"
        self.animals = []
        rng = random.Random(time.time_ns())
        for _ in range(6):
            kind = rng.choice(["rabbit", "turkey", "deer", "bear"])
            size = {"rabbit": 16, "turkey": 21, "deer": 31, "bear": 43}[kind]
            food = {"rabbit": 2, "turkey": 3, "deer": 6, "bear": 8}[kind]
            self.animals.append({"kind": kind, "x": rng.randint(50, WIDTH - 80), "y": rng.randint(80, CANVAS_H - 90), "vx": rng.choice([-1, 1]) * rng.uniform(1.3, 3.2), "size": size, "food": food, "alive": True})
        self.hunt_start = time.time()
        self.hunt_food = 0
        self.hunt_shots = 8

    def fire_shot(self, x: int, y: int) -> None:
        if self.hunt_shots <= 0 or self.state.powder <= 0:
            return
        self.hunt_shots -= 1
        self.state.powder = max(0, self.state.powder - 1)
        for animal in self.animals:
            if not animal["alive"]:
                continue
            dx = x - animal["x"]
            dy = y - animal["y"]
            if dx * dx + dy * dy <= animal["size"] * animal["size"]:
                animal["alive"] = False
                self.hunt_food += animal["food"]
                self.state.score += animal["food"] * 10
                if animal["kind"] == "bear" and random.random() < 0.25:
                    self.state.morale = max(0, self.state.morale - 1)
                    self.state.add_log("The bear dropped, but not before chewing up morale like a bastard.")
                return

    def finish_hunt(self) -> None:
        carried = min(12, self.hunt_food)
        self.state.food += carried
        self.state.add_log(f"Hunt finished. Brought back {carried} food. The rest stayed in the woods because arms are not wagons.")
        self.mode = "event"
        self.prepare_event()

    def current_room(self) -> Room:
        return self.rooms[min(self.room_index, len(self.rooms) - 1)]

    def ground_at(self, x: float) -> bool:
        pit = self.current_room().pit
        return not pit or not (pit[0] <= x <= pit[1])

    def update_trail(self) -> None:
        room = self.current_room()
        speed = 3.8
        self.player["vx"] = 0.0
        if "left" in self.keys or "a" in self.keys:
            self.player["vx"] = -speed
        if "right" in self.keys or "d" in self.keys:
            self.player["vx"] = speed
        if room.rope_x and abs(self.player["x"] - room.rope_x) < 42 and ("space" in self.keys or "up" in self.keys or "w" in self.keys):
            self.swing = 32
        if self.swing > 0:
            self.swing -= 1
            self.player["vx"] = 7.6
            self.player["vy"] = -0.25 if self.swing > 14 else 0.9
        elif ("space" in self.keys or "up" in self.keys or "w" in self.keys) and self.player["ground"]:
            self.player["vy"] = -10.2
            self.player["ground"] = False
        self.player["vy"] += 0.58
        self.player["x"] += self.player["vx"]
        self.player["y"] += self.player["vy"]
        self.player["ground"] = False
        center_x = self.player["x"] + self.player["w"] / 2
        if self.ground_at(center_x) and self.player["y"] + self.player["h"] >= GROUND_Y:
            self.player["y"] = GROUND_Y - self.player["h"]
            self.player["vy"] = 0
            self.player["ground"] = True
        if self.player["y"] > CANVAS_H:
            self.hit_hazard("pit")
        for hazard in room.hazards:
            hazard["x"] += hazard["vx"]
            if hazard["x"] < 130 or hazard["x"] > 820:
                hazard["vx"] *= -1
            if self.collides(hazard):
                self.hit_hazard(hazard["kind"])
                break
        for i, (x, y, kind, taken) in enumerate(room.pickups):
            if not taken and abs(center_x - x) < 25 and abs((self.player["y"] + 16) - y) < 34:
                room.pickups[i] = (x, y, kind, True)
                self.state.apply({kind: 1})
                self.state.score += 15
        if room.ladder and 430 < self.player["x"] < 500 and ("down" in self.keys or "s" in self.keys):
            self.state.apply({"furs": 1, "tools": -1})
            self.state.add_log("You took the cave ladder. Found a fur cache, lost a tool, and heard something breathing.")
            self.room_index += 1
            self.player.update({"x": 76.0, "y": GROUND_Y - self.player["h"], "vx": 0.0, "vy": 0.0})
        self.player["x"] = max(12, min(self.player["x"], WIDTH - 30))
        if self.player["x"] >= WIDTH - 42:
            if self.room_index >= len(self.rooms) - 1:
                self.state.leg += 1
                self.state.score += 100
                self.mode = "trail_done"
            else:
                self.room_index += 1
                self.player.update({"x": 30.0, "y": GROUND_Y - self.player["h"], "vx": 0.0, "vy": 0.0})
        elif self.player["x"] <= 18 and self.room_index > 0:
            self.room_index -= 1
            self.player.update({"x": WIDTH - 65.0, "y": GROUND_Y - self.player["h"], "vx": 0.0, "vy": 0.0})

    def collides(self, hazard: dict) -> bool:
        return self.player["x"] + self.player["w"] > hazard["x"] and self.player["x"] < hazard["x"] + hazard["w"] and self.player["y"] + self.player["h"] > hazard["y"] and self.player["y"] < hazard["y"] + hazard["h"]

    def hit_hazard(self, kind: str) -> None:
        self.state.apply({"morale": -1, "medicine": -1 if kind in {"snake", "wolf", "bear", "pit"} else 0})
        if random.random() < 0.18:
            victim = self.state.lose_member_by_skill(None)
            if victim:
                self.state.add_log(f"{victim} was lost to the {kind}. The trace kept moving, rude son of a bitch that it is.")
        else:
            self.state.add_log(f"A {kind} cost medicine and nerve, but the party kept crawling west.")
        self.player.update({"x": max(50.0, self.player["x"] - 120), "y": 250.0, "vx": 0.0, "vy": 0.0})
        self.swing = 0
        if self.state.is_lost():
            self.mode = "lost"

    def update_hunt(self) -> None:
        for animal in self.animals:
            if not animal["alive"]:
                continue
            animal["x"] += animal["vx"]
            if animal["x"] < 20 or animal["x"] > WIDTH - 20:
                animal["vx"] *= -1
        if time.time() - self.hunt_start > 35 or self.hunt_shots <= 0:
            self.mode = "hunt_done"

    def draw_header(self) -> None:
        self.canvas.create_rectangle(0, 0, WIDTH, 44, fill="#111111", outline=BORDER)
        loc = LANDMARKS[min(self.state.leg, len(LANDMARKS) - 1)]
        self.canvas.create_text(16, 22, text=f"Daniel Boone: Frontier Trail  |  {loc}", fill=TEXT, anchor="w", font=(FONT, 14, "bold"))
        stats = f"Food {self.state.food}  Powder {self.state.powder}  Furs {self.state.furs}  Med {self.state.medicine}  Tools {self.state.tools}  Morale {self.state.morale}  Day {self.state.days}"
        self.canvas.create_text(WIDTH - 16, 22, text=stats, fill=MUTED, anchor="e", font=(FONT, 10))

    def draw_title(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, CANVAS_H, fill=BG, outline="")
        self.canvas.create_rectangle(90, 54, WIDTH - 90, CANVAS_H - 38, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(WIDTH // 2, 105, text="DANIEL BOONE", fill=TEXT, font=(FONT, 34, "bold"))
        self.canvas.create_text(WIDTH // 2, 150, text="FRONTIER TRAIL", fill=ORANGE, font=(FONT, 32, "bold"))
        self.canvas.create_text(WIDTH // 2, 200, text="Oregon Trail choices. Pitfall rooms. Atari hunting. Tiny d20 doom.", fill=MUTED, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 262, text="Press SPACE to leave the settlement", fill=TEXT, font=(FONT, 17, "bold"))
        self.write_panel("Party:\n" + "\n".join(f"- {m.name}, {m.role}: +{m.skill}; flaw: {m.flaw}" for m in self.state.party))

    def draw_event(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        sc = self.selected_scenario
        if sc is None:
            return
        self.canvas.create_rectangle(80, 70, WIDTH - 80, CANVAS_H - 36, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(110, 100, text=sc["title"], fill=ORANGE, anchor="w", font=(FONT, 24, "bold"))
        self.canvas.create_text(110, 140, text=sc["text"], fill=TEXT, anchor="nw", font=(FONT, 13), width=WIDTH - 220)
        y = 205
        for i, (label, modifier, _effects, _success) in enumerate(sc["choices"], start=1):
            self.canvas.create_rectangle(120, y, WIDTH - 120, y + 48, fill=PANEL_2, outline=BORDER)
            sign = "+" if modifier >= 0 else ""
            self.canvas.create_text(140, y + 24, text=f"{i}. {label}   d20 {sign}{modifier}", fill=TEXT, anchor="w", font=(FONT, 13, "bold"))
            y += 62
        self.canvas.create_text(WIDTH // 2, CANVAS_H - 62, text="Press 1, 2, or 3.", fill=MUTED, font=(FONT, 12))
        self.write_panel("Recent trail notes:\n" + "\n".join(self.state.log or ["The settlement is behind you. That was the easy part."]))

    def draw_event_done(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        self.canvas.create_rectangle(70, 96, WIDTH - 70, 310, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(100, 125, text="The dice hit the dirt.", fill=ORANGE, anchor="w", font=(FONT, 22, "bold"))
        self.canvas.create_text(100, 170, text=self.roll_result, fill=TEXT, anchor="nw", width=WIDTH - 200, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 350, text="Press SPACE for the next Pitfall trail run.", fill=TEXT, font=(FONT, 16, "bold"))
        self.write_panel(self.party_text())

    def draw_trail(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        room = self.current_room()
        self.canvas.create_rectangle(0, 44, WIDTH, CANVAS_H, fill="#080808", outline="")
        self.canvas.create_text(18, 62, text=f"ROOM {self.room_index + 1}/6  {room.kind.upper()}", fill=ORANGE, anchor="w", font=(FONT, 12, "bold"))
        self.canvas.create_rectangle(0, GROUND_Y, WIDTH, GROUND_Y + 42, fill="#2c241b", outline="#5a4d3d")
        if room.pit:
            x1, x2 = room.pit
            self.canvas.create_rectangle(x1, GROUND_Y - 2, x2, GROUND_Y + 44, fill="#020202", outline="#555555")
            self.canvas.create_text((x1 + x2) // 2, GROUND_Y + 22, text="PIT", fill="#555555", font=(FONT, 9, "bold"))
        if room.rope_x:
            sway = (16 - self.swing) if self.swing else 0
            self.canvas.create_line(room.rope_x, 58, room.rope_x + sway, 238, fill="#b07b3c", width=4)
            self.canvas.create_oval(room.rope_x - 7 + sway, 232, room.rope_x + 7 + sway, 246, fill=ORANGE, outline="")
        if room.ladder:
            self.canvas.create_line(470, GROUND_Y, 470, GROUND_Y - 115, fill="#8a6a45", width=4)
            self.canvas.create_line(500, GROUND_Y, 500, GROUND_Y - 115, fill="#8a6a45", width=4)
            for y in range(GROUND_Y - 105, GROUND_Y, 18):
                self.canvas.create_line(468, y, 502, y, fill="#8a6a45", width=3)
            self.canvas.create_text(485, GROUND_Y - 128, text="DOWN = CAVE", fill=MUTED, font=(FONT, 9))
        for hazard in room.hazards:
            color = RED if hazard["kind"] in {"snake", "wolf"} else "#7d6048"
            self.canvas.create_rectangle(hazard["x"], hazard["y"], hazard["x"] + hazard["w"], hazard["y"] + hazard["h"], fill=color, outline="#151515")
            self.canvas.create_text(hazard["x"] + hazard["w"] / 2, hazard["y"] - 8, text=hazard["kind"], fill=MUTED, font=(FONT, 8))
        for x, y, kind, taken in room.pickups:
            if not taken:
                self.canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill=ORANGE, outline="#ffb45b")
                self.canvas.create_text(x, y - 18, text=kind, fill=MUTED, font=(FONT, 8))
        px = self.player["x"]
        py = self.player["y"]
        self.canvas.create_rectangle(px, py, px + self.player["w"], py + self.player["h"], fill="#dedbd2", outline="#111111")
        self.canvas.create_rectangle(px + 6, py - 12, px + 17, py, fill="#c6a077", outline="#111111")
        self.canvas.create_text(18, CANVAS_H - 20, text="A/D move. SPACE jump/swing. DOWN cave ladder. Right edge changes rooms.", fill=MUTED, anchor="w", font=(FONT, 10))
        self.write_panel("Trail notes:\n" + "\n".join(self.state.log or ["Pitfall mode: cross the room, dodge the bullshit, keep moving."]))

    def draw_trail_done(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        reached = LANDMARKS[min(self.state.leg, len(LANDMARKS) - 1)]
        self.canvas.create_rectangle(100, 100, WIDTH - 100, 315, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(WIDTH // 2, 145, text=f"Reached {reached}", fill=ORANGE, font=(FONT, 24, "bold"))
        self.canvas.create_text(WIDTH // 2, 210, text="The party limps in, counts supplies, and pretends morale is a plan.", fill=TEXT, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 275, text="Press SPACE to continue.", fill=TEXT, font=(FONT, 16, "bold"))
        self.write_panel(self.party_text())

    def draw_hunt(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        self.canvas.create_rectangle(0, 44, WIDTH, CANVAS_H, fill="#0b0b0b", outline="")
        self.canvas.create_text(20, 62, text=f"HUNTING  Powder {self.state.powder}  Shots {self.hunt_shots}  Food hit {self.hunt_food}", fill=ORANGE, anchor="w", font=(FONT, 13, "bold"))
        for animal in self.animals:
            if not animal["alive"]:
                continue
            size = animal["size"]
            color = {"rabbit": "#d8d8d8", "turkey": "#b98542", "deer": "#9b6a3c", "bear": "#4b3621"}[animal["kind"]]
            self.canvas.create_oval(animal["x"] - size, animal["y"] - size / 2, animal["x"] + size, animal["y"] + size / 2, fill=color, outline="#111111")
            self.canvas.create_text(animal["x"], animal["y"] - size, text=animal["kind"], fill=MUTED, font=(FONT, 8))
        x, y = self.crosshair["x"], self.crosshair["y"]
        self.canvas.create_line(x - 14, y, x + 14, y, fill=ORANGE)
        self.canvas.create_line(x, y - 14, x, y + 14, fill=ORANGE)
        self.write_panel("Click animals to hunt. Intentionally stupid-simple Atari arcade, not a deer sim.")

    def draw_hunt_done(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        self.canvas.create_rectangle(100, 100, WIDTH - 100, 315, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(WIDTH // 2, 150, text="Hunt complete", fill=ORANGE, font=(FONT, 24, "bold"))
        self.canvas.create_text(WIDTH // 2, 205, text=f"Food hit: {self.hunt_food}. Carry limit: 12.", fill=TEXT, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 275, text="Press SPACE to pack the meat and move on.", fill=TEXT, font=(FONT, 15, "bold"))
        self.write_panel("The woods are quieter now. Probably judging you.")

    def draw_end(self, won: bool) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, CANVAS_H, fill=BG, outline="")
        title = "HOMESTEAD REACHED" if won else "THE TRACE TOOK YOU"
        color = GREEN if won else RED
        self.canvas.create_rectangle(90, 76, WIDTH - 90, CANVAS_H - 50, fill="#121212", outline=color, width=2)
        self.canvas.create_text(WIDTH // 2, 130, text=title, fill=color, font=(FONT, 30, "bold"))
        self.canvas.create_text(WIDTH // 2, 190, text=f"Score {self.state.score}  Days {self.state.days}  Survivors {len(self.state.alive_members())}", fill=TEXT, font=(FONT, 14))
        self.canvas.create_text(WIDTH // 2, 270, text="Press R to restart.", fill=ORANGE, font=(FONT, 16, "bold"))
        self.write_panel(self.party_text())

    def party_text(self) -> str:
        lines = ["Party status:"]
        for member in self.state.party:
            status = "alive" if member.alive else "gone"
            lines.append(f"- {member.name}, {member.role}: {status}; flaw: {member.flaw}")
        lines.append("\nLog:")
        lines.extend(self.state.log or ["Nothing terrible has happened in the last five seconds. Suspicious."])
        return "\n".join(lines)

    def write_panel(self, content: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")

    def tick(self) -> None:
        if self.mode == "trail":
            self.update_trail()
        elif self.mode == "hunt":
            self.update_hunt()
        draw = {
            "title": self.draw_title,
            "event": self.draw_event,
            "event_done": self.draw_event_done,
            "trail": self.draw_trail,
            "trail_done": self.draw_trail_done,
            "hunt": self.draw_hunt,
            "hunt_done": self.draw_hunt_done,
            "won": lambda: self.draw_end(True),
            "lost": lambda: self.draw_end(False),
        }.get(self.mode, self.draw_title)
        draw()
        self.root.after(33, self.tick)


def launch_cli() -> int:
    if tk is None:
        print("Tkinter is not available. Install python3-tk to play Daniel Boone: Frontier Trail.", file=sys.stderr)
        return 1
    root = tk.Tk()
    FrontierTrailApp(root)
    root.mainloop()
    return 0


def main() -> None:
    raise SystemExit(launch_cli())


__all__ = ["Member", "GameState", "roll_event", "FrontierTrailApp", "launch_cli", "main"]

if __name__ == "__main__":
    main()
