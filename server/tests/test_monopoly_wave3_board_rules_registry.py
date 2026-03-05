"""Tests for Wave 3 Monopoly board rules registry coverage."""

import pytest

from server.games.monopoly.board_rules_registry import get_rule_pack, supports_capability

WAVE3_RULE_PACK_IDS = [
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


@pytest.mark.parametrize("rule_pack_id", WAVE3_RULE_PACK_IDS)
def test_wave3_rule_pack_registered(rule_pack_id: str):
    pack = get_rule_pack(rule_pack_id)
    assert pack is not None
    assert pack.status == "partial"
    assert supports_capability(rule_pack_id, "pass_go_credit_override") is True
