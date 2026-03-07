"""Tests for Wave 2 Monopoly board rules registry coverage."""

import pytest

from server.games.monopoly.board_rules_registry import get_rule_pack, supports_capability

WAVE2_RULE_PACK_IDS = [
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


@pytest.mark.parametrize("rule_pack_id", WAVE2_RULE_PACK_IDS)
def test_wave2_rule_pack_registered(rule_pack_id: str):
    pack = get_rule_pack(rule_pack_id)
    assert pack is not None
    assert pack.status == "partial"
    assert supports_capability(rule_pack_id, "pass_go_credit_override") is True
