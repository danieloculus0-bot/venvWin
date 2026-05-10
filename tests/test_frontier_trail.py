from __future__ import annotations

import random

from venvwin.frontier_trail import GameState, Member, roll_event


def test_game_state_starts_with_supplies_and_party() -> None:
    state = GameState()

    assert state.food > 0
    assert state.powder > 0
    assert state.furs >= 0
    assert len(state.party) == 5
    assert len(state.alive_members()) == 5


def test_skill_bonus_uses_living_party_members() -> None:
    state = GameState(
        party=[
            Member("Beth", "herbalist", "medicine", "accused easily", luck=2),
            Member("Cletus", "trapper", "hunting", "steals", luck=0, alive=False),
        ]
    )

    assert state.skill_bonus("medicine") == 4
    assert state.skill_bonus("hunting") == 0


def test_roll_event_success_applies_choice_effects(monkeypatch) -> None:
    monkeypatch.setattr(random, "randint", lambda _low, _high: 20)
    state = GameState(party=[Member("Mabel", "trader", "trade", "debts", luck=0)])
    scenario = {
        "title": "Trade Test",
        "text": "A trader waits.",
        "skill": "trade",
        "choices": [("Trade fairly", 0, {"furs": -2, "food": 4}, "Clean trade.")],
        "fail": "The deal turns sour.",
        "loss_skill": None,
    }

    total, result, success = roll_event(state, scenario, 0)

    assert success is True
    assert total >= 11
    assert "Clean trade" in result
    assert state.furs == 4
    assert state.food == 32


def test_travel_consumes_food_and_advances_days() -> None:
    state = GameState(party=[Member("Silas", "scout", "scouting", "wanders", luck=0)])
    before_food = state.food

    state.consume_travel()

    assert state.days >= 3
    assert state.food < before_food
