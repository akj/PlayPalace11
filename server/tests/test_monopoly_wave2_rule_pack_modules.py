"""Tests for Wave 2 Monopoly board rule-pack modules."""

import pytest

from server.games.monopoly.board_rules import (
    animal_crossing,
    barbie,
    disney_animation,
    disney_lightyear,
    disney_lion_king,
    disney_mickey_friends,
    disney_princesses,
    disney_villains,
    fortnite,
    harry_potter,
    jurassic_park,
    lord_of_the_rings,
    marvel_80_years,
    marvel_avengers,
    marvel_black_panther_wf,
    marvel_deadpool,
    marvel_spider_man,
    marvel_super_villains,
    star_wars_40th,
    star_wars_boba_fett,
    star_wars_complete_saga,
    star_wars_light_side,
    star_wars_mandalorian,
    star_wars_the_child,
    stranger_things,
)

WAVE2_MODULES = [
    (disney_princesses, "disney_princesses", "monopoly-b4644"),
    (disney_animation, "disney_animation", "monopoly-c2116"),
    (disney_lion_king, "disney_lion_king", "monopoly-e6707"),
    (disney_mickey_friends, "disney_mickey_friends", "monopoly-f5267"),
    (disney_villains, "disney_villains", "monopoly-f0091"),
    (disney_lightyear, "disney_lightyear", "monopoly-f8046"),
    (marvel_80_years, "marvel_80_years", "monopoly-e7866"),
    (marvel_avengers, "marvel_avengers", "monopoly-e6504"),
    (marvel_spider_man, "marvel_spider_man", "monopoly-f3968"),
    (marvel_black_panther_wf, "marvel_black_panther_wf", "monopoly-f5405"),
    (marvel_super_villains, "marvel_super_villains", "monopoly-f5270"),
    (marvel_deadpool, "marvel_deadpool", "monopoly-e2033"),
    (star_wars_40th, "star_wars_40th", "monopoly-c1990"),
    (star_wars_boba_fett, "star_wars_boba_fett", "monopoly-f5394"),
    (star_wars_light_side, "star_wars_light_side", "monopoly-f8383"),
    (star_wars_the_child, "star_wars_the_child", "monopoly-f2013"),
    (star_wars_mandalorian, "star_wars_mandalorian", "monopoly-f1276"),
    (star_wars_complete_saga, "star_wars_complete_saga", "monopoly-e8066"),
    (harry_potter, "harry_potter", "monopoly-f9422"),
    (fortnite, "fortnite", "monopoly-e6603"),
    (stranger_things, "stranger_things", "monopoly-c4550"),
    (jurassic_park, "jurassic_park", "monopoly-f1662"),
    (lord_of_the_rings, "lord_of_the_rings", "monopoly-f1663"),
    (animal_crossing, "animal_crossing", "monopoly-f1661"),
    (barbie, "barbie", "monopoly-g0038"),
]


@pytest.mark.parametrize(("module", "rule_pack_id", "anchor_id"), WAVE2_MODULES)
def test_wave2_stub_exposes_anchor_and_status(module, rule_pack_id: str, anchor_id: str):
    assert module.RULE_PACK_ID == rule_pack_id
    assert module.ANCHOR_EDITION_ID == anchor_id
    assert module.RULE_PACK_STATUS == "partial"
    assert isinstance(module.PASS_GO_CREDIT_OVERRIDE, int)
    assert "pass_go_credit_override" in module.CAPABILITY_IDS
    assert "startup_board_announcement" in module.CAPABILITY_IDS
