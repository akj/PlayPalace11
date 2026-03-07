"""Tests for Monopoly Junior ruleset profiles."""

from server.games.monopoly.junior_rules import get_junior_ruleset, is_junior_ruleset_preset


def test_junior_ruleset_anchors_are_fixed():
    modern = get_junior_ruleset("junior_modern")
    legacy = get_junior_ruleset("junior_legacy")
    assert modern.anchor_edition_id == "monopoly-f8562"
    assert legacy.anchor_edition_id == "monopoly-00441"


def test_junior_rulesets_define_core_fields():
    modern = get_junior_ruleset("junior_modern")
    legacy = get_junior_ruleset("junior_legacy")

    assert modern.starting_cash > 0
    assert legacy.starting_cash > 0
    assert modern.pass_go_cash > 0
    assert legacy.pass_go_cash > 0
    assert modern.game_end_mode in {"bankruptcy", "property_pool_exhausted", "timer"}
    assert legacy.game_end_mode in {"bankruptcy", "property_pool_exhausted", "timer"}


def test_is_junior_ruleset_preset_detects_known_ids():
    assert is_junior_ruleset_preset("junior_modern") is True
    assert is_junior_ruleset_preset("junior_legacy") is True
    assert is_junior_ruleset_preset("classic_standard") is False

