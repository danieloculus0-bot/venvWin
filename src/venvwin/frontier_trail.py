from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - headless test environments may not provide Tk
    tk = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]

WIDTH = 960
HEIGHT = 620
CANVAS_H = 430
GROUND_Y = 360
FONT = "Segoe UI"
BG = "#050505"
PANEL = "#151515"
PANEL_2 = "#222222"
BORDER = "#4a4a4a"
TEXT = "#f4f1ea"
MUTED = "#aaa39a"
ORANGE = "#ff8a00"
ORANGE_DARK = "#b65300"
GREEN = "#68b957"
RED = "#e04436"

PARTY_POOL = [
    ("Cletus", "trapper", "hunting", "steals small useful things"),
    ("Beth", "herbalist", "medicine", "gets accused when fear spreads"),
    ("Seymour", "blacksmith", "tools", "starts fights after whiskey"),
    ("Silas", "scout", "scouting", "wanders off at the worst times"),
    ("Amos", "preacher", "morale", "can turn superstition into panic"),
    ("Ruth", "cook", "food", "hides bad news until it festers"),
    ("Gideon", "old soldier", "powder", "settles arguments with a gun hand"),
    ("Mabel", "widow trader", "trade", "keeps private debts"),
]

LANDMARKS = [
    "Boonesborough Road",
    "Cold Creek Ford",
    "Dark Timber",
    "Trader's Hollow",
    "Cave Gap",
    "Winter Ridge",
    "New Homestead",
]

SCENARIOS = [
    {
        "title": "Tavern Trouble",
        "text": "Seymour breaks a chair over a stranger after a card game goes sour.",
        "skill": "morale",
        "choices": [
            ("Pay damages", -2, {"furs": -2, "morale": 1}, "You lose furs, but the party keeps moving."),
            ("Let the law handle it", 0, {"days": 1}, "The local sheriff wastes a day making a lesson out of him."),
            ("Drag him out yourself", 2, {"morale": -1}, "You get him out, but the camp mutters about your temper."),
        ],
        "fail": "Seymour is hanged at dawn for killing a man nobody liked enough to defend him.",
        "loss_skill": "tools",
    },
    {
        "title": "Witch Talk",
        "text": "A fever sweeps camp and Beth's herbs suddenly look suspicious to frightened fools.",
        "skill": "medicine",
        "choices": [
            ("Defend Beth", 2, {"morale": -1}, "You put yourself between Beth and the mob."),
            ("Leave before nightfall", 0, {"food": -2}, "You flee fast and leave supplies behind."),
            ("Let Amos speak", -1, {"morale": 1}, "Amos calms some people and terrifies others."),
        ],
        "fail": "Beth is burned as a witch while the camp watches the smoke and says nothing.",
        "loss_skill": "medicine",
    },
    {
        "title": "Missing Tobacco",
        "text": "Cletus swears innocence while chewing exactly like a guilty man.",
        "skill": "scouting",
        "choices": [
            ("Search his bedroll", 2, {"morale": -1}, "You find tobacco, a knife, and three furs he forgot stealing."),
            ("Ignore it", -1, {"furs": -2}, "Two pelts and your best knife vanish by morning."),
            ("Make him hunt double", 1, {"food": 2}, "Cletus grumbles, but comes back with meat."),
        ],
        "fail": "Cletus steals your chewing tobacco, two pelts, and the knife you actually liked.",
        "loss_skill": None,
    },
    {
        "title": "Village Trade",
        "text": "A nearby village offers corn, medicine, and a guide. They ask for furs and respect.",
        "skill": "trade",
        "choices": [
            ("Trade fairly", 2, {"furs": -2, "food": 4, "medicine": 1}, "The trade is clean and the guide points you toward dry ground."),
            ("Hold back furs", -2, {"food": 1}, "They notice. You receive little and leave under hard stares."),
            ("Ask for a guide", 1, {"furs": -1, "days": -1}, "A guide cuts a day from the trail."),
        ],
        "fail": "A raiding party hits the camp after dark. You lose furs and powder before you can form a line.",
        "loss_skill": None,
    },
    {
        "title": "River Fever",
        "text": "Bad creek water takes down half the camp by morning.",
        "skill": "medicine",
        "choices": [
            ("Spend medicine", 2, {"medicine": -1}, "The fever breaks after a miserable night."),
            ("Rest two days", 0, {"days": 2, "food": -2}, "The party recovers, but winter edges closer."),
            ("Push forward", -3, {"morale": -2}, "The sick stumble behind and hate you for it."),
        ],
        "fail": "One traveler dies before sunrise. Nobody says much while the grave is dug.",
        "loss_skill": "morale",
    },
    {
        "title": "Powder Thief",
        "text": "A horn of powder is missing and every face around the fire looks innocent as a church bell.",
        "skill": "scouting",
        "choices": [
            ("Track footprints", 2, {"powder": 1}, "You recover most of it beneath a rotten stump."),
            ("Accuse the loudest man", -1, {"morale": -1}, "The accusation poisons the camp."),
            ("Set a night watch", 1, {"morale": 1}, "Nobody sleeps well, but nothing else disappears."),
        ],
        "fail": "The thief slips away. Your powder supply is lighter and nobody trusts anybody.",
        "loss_skill": None,
    },
]


@dataclass
class Member:
    name: str
    role: str
    skill: str
    flaw: str
    luck: int
    alive: bool = True


@dataclass
class GameState:
    food: int = 28
    powder: int = 16
    furs: int = 6
    medicine: int = 4
    tools: int = 5
    morale: int = 7
    days: int = 0
    leg: int = 0
    score: int = 0
    party: list[Member] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.party:
            selected = random.sample(PARTY_POOL, 5)
            self.party = [Member(name, role, skill, flaw, random.randint(-1, 2)) for name, role, skill, flaw in selected]

    def alive_members(self) -> list[Member]:
        return [member for member in self.party if member.alive]

    def skill_bonus(self, skill: str) -> int:
        bonus = 0
        for member in self.alive_members():
            if member.skill == skill:
                bonus += 2 + member.luck
        if skill == "morale":
            bonus += max(-2, min(2, self.morale - 5))
        return bonus

    def add_log(self, text: str) -> None:
        self.log.insert(0, text)
        self.log = self.log[:7]

    def apply(self, effects: dict[str, int]) -> None:
        for key, delta in effects.items():
            current = getattr(self, key)
            setattr(self, key, max(0, current + delta))

    def consume_travel(self) -> None:
        self.days += random.randint(3, 6)
        self.food = max(0, self.food - max(2, len(self.alive_members())))
        if self.food == 0:
            self.morale = max(0, self.morale - 2)
            self.add_log("Food is gone. The camp gets quiet in the bad way.")

    def lose_member_by_skill(self, skill: str | None) -> str | None:
        candidates = [member for member in self.alive_members() if skill is None or member.skill == skill]
        if not candidates:
            candidates = self.alive_members()
        if len(candidates) <= 1:
            return None
        victim = random.choice(candidates)
        victim.alive = False
        self.morale = max(0, self.morale - 2)
        return victim.name

    def is_lost(self) -> bool:
        return len(self.alive_members()) == 0 or self.food == 0 and self.morale == 0

    def is_won(self) -> bool:
        return self.leg >= len(LANDMARKS) - 1 and not self.is_lost()


def roll_event(state: GameState, scenario: dict, choice_index: int) -> tuple[int, str, bool]:
    label, modifier, effects, success_text = scenario["choices"][choice_index]
    skill = scenario["skill"]
    roll = random.randint(1, 20)
    total = roll + modifier + state.skill_bonus(skill)
    if total >= 11:
        state.apply(effects)
        state.score += 50 + total
        result = f"Rolled {roll}. {success_text}"
        state.add_log(f"{scenario['title']}: {label}. {result}")
        return total, result, True

    state.apply({"morale": -1, "furs": -1})
    victim_name = None
    if roll <= 3 or total <= 5:
        victim_name = state.lose_member_by_skill(scenario.get("loss_skill"))
    result = f"Rolled {roll}. {scenario['fail']}"
    if victim_name:
        result += f" {victim_name} is gone from the party."
    state.add_log(f"{scenario['title']}: {label}. {result}")
    return total, result, False


class FrontierTrailApp:
    def __init__(self, root) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available. Install python3-tk to play Daniel Boone: Frontier Trail.")
        self.root = root
        self.root.title("Daniel Boone: Frontier Trail")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.minsize(WIDTH, HEIGHT)
        self.root.configure(bg=BG)
        self.state = GameState()
        self.mode = "title"
        self.keys: set[str] = set()
        self.player = {"x": 60.0, "y": 320.0, "vx": 0.0, "vy": 0.0, "w": 22, "h": 34, "ground": False}
        self.world_x = 0
        self.stage_goal = 880
        self.platforms: list[tuple[int, int, int, int]] = []
        self.hazards: list[tuple[int, int, int, int, str]] = []
        self.pickups: list[tuple[int, int, str, bool]] = []
        self.animals: list[dict] = []
        self.crosshair = {"x": 480, "y": 210}
        self.selected_scenario: dict | None = None
        self.roll_result = ""

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
            self.start_stage()
        elif self.mode == "stage_done" and key in {"space", "return"}:
            self.after_stage()
        elif self.mode == "hunt_done" and key in {"space", "return"}:
            self.finish_hunt()
        elif self.mode in {"won", "lost"} and key == "r":
            self.__init__(self.root)

    def key_up(self, event) -> None:
        self.keys.discard(event.keysym.lower())

    def mouse_move(self, event) -> None:
        self.crosshair["x"] = event.x
        self.crosshair["y"] = event.y

    def mouse_click(self, event) -> None:
        if self.mode == "hunt":
            self.fire_shot(event.x, event.y)

    def prepare_event(self) -> None:
        self.selected_scenario = random.choice(SCENARIOS)
        self.roll_result = ""

    def choose_event(self, idx: int) -> None:
        if self.selected_scenario is None:
            return
        _, result, _ = roll_event(self.state, self.selected_scenario, idx)
        self.roll_result = result
        self.mode = "event_done"

    def start_stage(self) -> None:
        self.mode = "stage"
        self.state.consume_travel()
        self.player.update({"x": 50.0, "y": 320.0, "vx": 0.0, "vy": 0.0})
        self.world_x = 0
        self.stage_goal = 980 + self.state.leg * 120
        self.platforms = [(0, GROUND_Y, self.stage_goal + 160, 40)]
        self.hazards = []
        self.pickups = []
        rng = random.Random(1000 + self.state.leg)
        for i in range(5 + self.state.leg):
            x = 220 + i * 145 + rng.randint(-30, 30)
            kind = rng.choice(["pit", "snake", "log", "wolf", "rock"])
            if kind == "pit":
                self.hazards.append((x, GROUND_Y - 2, 58, 44, "pit"))
            else:
                self.hazards.append((x, GROUND_Y - 26, 36, 26, kind))
            if rng.random() < 0.65:
                self.pickups.append((x + rng.randint(40, 88), GROUND_Y - rng.randint(55, 105), rng.choice(["food", "powder", "furs", "medicine"]), False))
        for i in range(2 + self.state.leg // 2):
            px = 300 + i * 220 + rng.randint(-40, 40)
            py = GROUND_Y - rng.randint(80, 140)
            self.platforms.append((px, py, 120, 12))

    def after_stage(self) -> None:
        if self.state.is_lost():
            self.mode = "lost"
            return
        if self.state.leg >= len(LANDMARKS) - 1:
            self.mode = "won"
            return
        if self.state.food < 10 or self.state.leg in {1, 4}:
            self.start_hunt()
        else:
            self.mode = "event"
            self.prepare_event()

    def start_hunt(self) -> None:
        self.mode = "hunt"
        self.animals = []
        rng = random.Random(time.time_ns())
        for _ in range(5):
            animal = rng.choice(["rabbit", "turkey", "deer", "bear"])
            size = {"rabbit": 18, "turkey": 22, "deer": 32, "bear": 44}[animal]
            food = {"rabbit": 2, "turkey": 3, "deer": 6, "bear": 8}[animal]
            self.animals.append({
                "kind": animal,
                "x": rng.randint(40, WIDTH - 80),
                "y": rng.randint(80, CANVAS_H - 80),
                "vx": rng.choice([-1, 1]) * rng.uniform(1.2, 3.0),
                "size": size,
                "food": food,
                "alive": True,
            })
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
                    self.state.add_log("The bear dropped, but not before clawing a man badly enough to sour the firelight.")
                return

    def finish_hunt(self) -> None:
        carried = min(12, self.hunt_food)
        self.state.food += carried
        self.state.add_log(f"Hunt finished. Brought back {carried} food. Left the rest to rot because arms are not wagons.")
        self.mode = "event"
        self.prepare_event()

    def update_stage(self) -> None:
        speed = 3.4
        if "left" in self.keys or "a" in self.keys:
            self.player["vx"] = -speed
        elif "right" in self.keys or "d" in self.keys:
            self.player["vx"] = speed
        else:
            self.player["vx"] = 0
        if ("space" in self.keys or "up" in self.keys or "w" in self.keys) and self.player["ground"]:
            self.player["vy"] = -10.5
            self.player["ground"] = False
        self.player["vy"] += 0.55
        self.player["x"] += self.player["vx"]
        self.player["y"] += self.player["vy"]
        self.player["ground"] = False
        px, py, pw, ph = self.player["x"], self.player["y"], self.player["w"], self.player["h"]
        for x, y, w, h in self.platforms:
            if px + pw > x and px < x + w and py + ph >= y and py + ph <= y + 18 and self.player["vy"] >= 0:
                self.player["y"] = y - ph
                self.player["vy"] = 0
                self.player["ground"] = True
        if self.player["y"] > CANVAS_H:
            self.hit_hazard("pit")
        for x, y, w, h, kind in self.hazards:
            if px + pw > x and px < x + w and py + ph > y and py < y + h:
                self.hit_hazard(kind)
                break
        for i, (x, y, kind, taken) in enumerate(self.pickups):
            if not taken and abs(px + pw / 2 - x) < 24 and abs(py + ph / 2 - y) < 28:
                self.pickups[i] = (x, y, kind, True)
                self.state.apply({kind: 1})
                self.state.score += 15
        self.player["x"] = max(0, min(self.player["x"], self.stage_goal))
        self.world_x = max(0, int(self.player["x"] - 210))
        if self.player["x"] >= self.stage_goal - 30:
            self.state.leg += 1
            self.state.score += 100
            self.mode = "stage_done"

    def hit_hazard(self, kind: str) -> None:
        self.state.apply({"morale": -1, "medicine": -1 if kind in {"snake", "wolf", "bear", "rock"} else 0})
        if random.random() < 0.22:
            victim = self.state.lose_member_by_skill(None)
            if victim:
                self.state.add_log(f"{victim} was lost to the {kind}. The trail does not care who was useful.")
        else:
            self.state.add_log(f"A {kind} cost medicine and nerve, but the party kept moving.")
        self.player.update({"x": max(40.0, self.player["x"] - 90), "y": 280.0, "vx": 0.0, "vy": 0.0})
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
        self.canvas.create_text(WIDTH // 2, 200, text="Oregon Trail decisions. Pitfall-style travel. Atari hunting. Tiny d20 doom.", fill=MUTED, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 262, text="Press SPACE to leave the settlement", fill=TEXT, font=(FONT, 17, "bold"))
        self.canvas.create_text(WIDTH // 2, 310, text="One rough party. Seven landmarks. Reach the homestead before winter eats your luck.", fill=MUTED, font=(FONT, 12))
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
        self.canvas.create_text(WIDTH // 2, CANVAS_H - 62, text="Press 1, 2, or 3. Higher rolls live longer.", fill=MUTED, font=(FONT, 12))
        self.write_panel("Recent trail notes:\n" + "\n".join(self.state.log or ["The settlement is behind you. That was the easy part."]))

    def draw_event_done(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        self.canvas.create_rectangle(70, 96, WIDTH - 70, 310, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(100, 125, text="The dice hit the dirt.", fill=ORANGE, anchor="w", font=(FONT, 22, "bold"))
        self.canvas.create_text(100, 170, text=self.roll_result, fill=TEXT, anchor="nw", width=WIDTH - 200, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 350, text="Press SPACE for the next trail run.", fill=TEXT, font=(FONT, 16, "bold"))
        self.write_panel(self.party_text())

    def draw_stage(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        ox = self.world_x
        self.canvas.create_rectangle(0, 44, WIDTH, CANVAS_H, fill="#090909", outline="")
        self.canvas.create_line(0, GROUND_Y + 42, WIDTH, GROUND_Y + 42, fill="#2e2e2e", width=3)
        for x, y, w, h in self.platforms:
            sx = x - ox
            if -100 <= sx <= WIDTH + 100:
                self.canvas.create_rectangle(sx, y, sx + w, y + h, fill="#3a332a", outline="#6b5c45")
        for x, y, w, h, kind in self.hazards:
            sx = x - ox
            if -80 <= sx <= WIDTH + 80:
                color = RED if kind in {"snake", "wolf", "rock"} else "#070707"
                self.canvas.create_rectangle(sx, y, sx + w, y + h, fill=color, outline="#555555")
                self.canvas.create_text(sx + w / 2, y - 8, text=kind, fill=MUTED, font=(FONT, 8))
        for x, y, kind, taken in self.pickups:
            if taken:
                continue
            sx = x - ox
            self.canvas.create_oval(sx - 9, y - 9, sx + 9, y + 9, fill=ORANGE, outline="#ffb45b")
            self.canvas.create_text(sx, y - 18, text=kind, fill=MUTED, font=(FONT, 8))
        px = self.player["x"] - ox
        py = self.player["y"]
        self.canvas.create_rectangle(px, py, px + self.player["w"], py + self.player["h"], fill="#d8d8d8", outline="#111111")
        self.canvas.create_rectangle(px + 7, py - 12, px + 18, py, fill="#c7a37a", outline="#111111")
        goal_x = self.stage_goal - ox
        self.canvas.create_rectangle(goal_x, GROUND_Y - 70, goal_x + 34, GROUND_Y, fill=GREEN, outline="#d8f6d0")
        self.canvas.create_text(18, CANVAS_H - 20, text="Move: A/D or arrows. Jump: SPACE/W/UP. Collect supplies. Avoid frontier nonsense.", fill=MUTED, anchor="w", font=(FONT, 10))
        self.write_panel("Trail notes:\n" + "\n".join(self.state.log or ["Move right. Try not to make the obituary interesting."]))

    def draw_stage_done(self) -> None:
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
        self.canvas.create_line(x - 12, y, x + 12, y, fill=TEXT)
        self.canvas.create_line(x, y - 12, x, y + 12, fill=TEXT)
        remaining = max(0, 35 - int(time.time() - self.hunt_start))
        self.canvas.create_text(WIDTH - 20, 62, text=f"{remaining}s", fill=TEXT, anchor="e", font=(FONT, 13, "bold"))
        self.write_panel("Click animals to hunt. Food carry limit is 12. Missed shots still burn powder because physics is rude.")

    def draw_hunt_done(self) -> None:
        self.canvas.delete("all")
        self.draw_header()
        carried = min(12, self.hunt_food)
        self.canvas.create_rectangle(110, 110, WIDTH - 110, 300, fill="#121212", outline=BORDER, width=2)
        self.canvas.create_text(WIDTH // 2, 150, text="Hunt Complete", fill=ORANGE, font=(FONT, 24, "bold"))
        self.canvas.create_text(WIDTH // 2, 205, text=f"You can carry {carried} food back to camp.", fill=TEXT, font=(FONT, 14))
        self.canvas.create_text(WIDTH // 2, 260, text="Press SPACE to return to the trail.", fill=TEXT, font=(FONT, 16, "bold"))
        self.write_panel("The woods get quiet after gunfire. Sometimes that is mercy. Sometimes it is bad news.")

    def draw_end(self, won: bool) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, CANVAS_H, fill=BG, outline="")
        self.canvas.create_rectangle(100, 80, WIDTH - 100, 330, fill="#121212", outline=BORDER, width=2)
        title = "NEW HOMESTEAD REACHED" if won else "THE TRAIL TOOK THE REST"
        color = GREEN if won else RED
        self.canvas.create_text(WIDTH // 2, 130, text=title, fill=color, font=(FONT, 26, "bold"))
        ending = "You arrive with enough breath left to call it victory." if won else "Somewhere behind you, the frontier closed over the tracks."
        self.canvas.create_text(WIDTH // 2, 185, text=ending, fill=TEXT, font=(FONT, 14))
        self.canvas.create_text(WIDTH // 2, 245, text=f"Score {self.state.score}   Days {self.state.days}   Survivors {len(self.state.alive_members())}", fill=MUTED, font=(FONT, 13))
        self.canvas.create_text(WIDTH // 2, 295, text="Press R to run it again.", fill=TEXT, font=(FONT, 16, "bold"))
        self.write_panel(self.party_text())

    def party_text(self) -> str:
        lines = ["Party:"]
        for member in self.state.party:
            state = "alive" if member.alive else "gone"
            lines.append(f"- {member.name}, {member.role}: {state}; +{member.skill}; flaw: {member.flaw}")
        lines.append("\nTrail notes:")
        lines.extend(self.state.log or ["No news yet. Which is suspicious."])
        return "\n".join(lines)

    def write_panel(self, value: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.configure(state="disabled")

    def tick(self) -> None:
        if self.mode == "title":
            self.draw_title()
        elif self.mode == "event":
            if self.selected_scenario is None:
                self.prepare_event()
            self.draw_event()
        elif self.mode == "event_done":
            self.draw_event_done()
        elif self.mode == "stage":
            self.update_stage()
            self.draw_stage()
        elif self.mode == "stage_done":
            self.draw_stage_done()
        elif self.mode == "hunt":
            self.update_hunt()
            self.draw_hunt()
        elif self.mode == "hunt_done":
            self.draw_hunt_done()
        elif self.mode == "won":
            self.draw_end(True)
        elif self.mode == "lost":
            self.draw_end(False)
        self.root.after(33, self.tick)


def main(argv: list[str] | None = None) -> int:
    if tk is None:
        print("Daniel Boone: Frontier Trail requires Tkinter. Install python3-tk.", file=sys.stderr)
        return 1
    root = tk.Tk()
    FrontierTrailApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
