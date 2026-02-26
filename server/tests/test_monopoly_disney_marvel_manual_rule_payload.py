"""Coverage for Disney/Marvel-family manual rule payloads."""

from __future__ import annotations

import pytest

from server.games.monopoly.game import (
    CHANCE_CARD_IDS,
    COMMUNITY_CHEST_CARD_IDS,
    MonopolyGame,
    MonopolyOptions,
)
from server.games.monopoly.manual_rules.loader import load_manual_rule_set
from server.users.test_user import MockUser


DISNEY_MARVEL_FAMILY_BOARD_IDS = [
    "disney_princesses",
    "disney_animation",
    "disney_lion_king",
    "disney_mickey_friends",
    "disney_villains",
    "disney_lightyear",
    "disney_legacy",
    "disney_the_edition",
    "marvel_80_years",
    "marvel_avengers",
    "marvel_spider_man",
    "marvel_black_panther_wf",
    "marvel_super_villains",
    "marvel_deadpool",
    "marvel_avengers_legacy",
    "marvel_eternals",
    "marvel_falcon_winter_soldier",
    "marvel_flip",
]


def _start_game(board_id: str) -> MonopolyGame:
    game = MonopolyGame(
        options=MonopolyOptions(
            preset_id="classic_standard",
            board_id=board_id,
            board_rules_mode="auto",
        )
    )
    game.add_player("Host", MockUser("Host"))
    game.add_player("Guest", MockUser("Guest"))
    game.host = "Host"
    game.on_start()
    return game


@pytest.mark.parametrize("board_id", DISNEY_MARVEL_FAMILY_BOARD_IDS)
def test_disney_marvel_manual_rule_payload_has_full_card_and_space_baseline(board_id: str):
    rule_set = load_manual_rule_set(board_id)

    spaces = rule_set.board.get("spaces", [])
    chance_rows = rule_set.cards.get("chance", [])
    community_rows = rule_set.cards.get("community_chest", [])

    assert len(spaces) == 40
    assert [row["id"] for row in chance_rows] == CHANCE_CARD_IDS
    assert [row["id"] for row in community_rows] == COMMUNITY_CHEST_CARD_IDS


@pytest.mark.parametrize(
    ("board_id", "card_id", "expected_amount"),
    [
        ("disney_princesses", "bank_dividend_50", 90),
        ("disney_lightyear", "bank_dividend_50", 88),
        ("disney_lion_king", "income_tax_refund_20", 75),
        ("disney_villains", "bank_dividend_50", 68),
        ("disney_legacy", "bank_error_collect_200", 210),
        ("marvel_80_years", "bank_dividend_50", 92),
        ("marvel_avengers", "bank_error_collect_200", 220),
        ("marvel_black_panther_wf", "income_tax_refund_20", 70),
        ("marvel_avengers_legacy", "bank_error_collect_200", 215),
        ("marvel_eternals", "bank_dividend_50", 85),
    ],
)
def test_disney_marvel_manual_rule_payload_encodes_card_amount_overrides(
    board_id: str,
    card_id: str,
    expected_amount: int,
):
    rule_set = load_manual_rule_set(board_id)
    rows = rule_set.cards.get("chance", []) + rule_set.cards.get("community_chest", [])
    row = next(row for row in rows if row.get("id") == card_id)
    effect = row.get("effect", {})

    assert effect.get("amount") == expected_amount


def test_disney_marvel_manual_rule_payload_executes_manual_effect_for_remapped_card(monkeypatch):
    game = _start_game("disney_mickey_friends")
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))

    original = game._apply_manual_card_effect
    seen_effect_types: list[str] = []

    def _wrapped_apply(player, effect_spec, *, depth, dice_total):
        effect_type = effect_spec.get("type")
        if isinstance(effect_type, str):
            seen_effect_types.append(effect_type)
        return original(player, effect_spec, depth=depth, dice_total=dice_total)

    monkeypatch.setattr(game, "_apply_manual_card_effect", _wrapped_apply)

    game.execute_action(host, "roll_dice")

    assert "move_absolute" in seen_effect_types
    assert host.position == 0
    assert host.cash == 1700
