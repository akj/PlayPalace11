"""Tests for Wave 2 board profile resolution."""

import pytest

from server.games.monopoly.board_profile import resolve_board_plan

WAVE2_BOARD_IDS = [
    "disney_princesses",
    "disney_animation",
    "disney_lion_king",
    "disney_mickey_friends",
    "disney_villains",
    "disney_lightyear",
    "marvel_80_years",
    "marvel_avengers",
    "marvel_spider_man",
    "marvel_black_panther_wf",
    "marvel_super_villains",
    "marvel_deadpool",
    "star_wars_40th",
    "star_wars_boba_fett",
    "star_wars_light_side",
    "star_wars_the_child",
    "star_wars_mandalorian",
    "star_wars_complete_saga",
    "harry_potter",
    "fortnite",
    "stranger_things",
    "jurassic_park",
    "lord_of_the_rings",
    "animal_crossing",
    "barbie",
]


@pytest.mark.parametrize("board_id", WAVE2_BOARD_IDS)
def test_wave2_boards_resolve_to_classic_board_rules(board_id: str):
    plan = resolve_board_plan("classic_standard", board_id, "auto")
    assert plan.effective_preset_id == "classic_standard"
    assert plan.effective_mode == "board_rules"
    assert plan.rule_pack_status == "partial"
