"""Tests for Wave 3 board profile resolution."""

import pytest

from server.games.monopoly.board_profile import resolve_board_plan

WAVE3_BOARD_IDS = [
    "disney_star_wars_dark_side",
    "disney_legacy",
    "disney_the_edition",
    "lord_of_the_rings_trilogy",
    "star_wars_saga",
    "marvel_avengers_legacy",
    "star_wars_legacy",
    "star_wars_classic_edition",
    "star_wars_solo",
    "game_of_thrones",
    "deadpool_collectors",
    "toy_story",
    "black_panther",
    "stranger_things_collectors",
    "ghostbusters",
    "marvel_eternals",
    "transformers",
    "stranger_things_netflix",
    "fortnite_collectors",
    "star_wars_mandalorian_s2",
    "transformers_beast_wars",
    "marvel_falcon_winter_soldier",
    "fortnite_flip",
    "marvel_flip",
    "pokemon",
]


@pytest.mark.parametrize("board_id", WAVE3_BOARD_IDS)
def test_wave3_boards_resolve_to_classic_board_rules(board_id: str):
    plan = resolve_board_plan("classic_standard", board_id, "auto")
    assert plan.effective_preset_id == "classic_standard"
    assert plan.effective_mode == "board_rules"
    assert plan.rule_pack_status == "partial"
