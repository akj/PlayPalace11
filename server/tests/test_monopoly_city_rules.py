"""Tests for Monopoly City normalized rules data."""

from server.games.monopoly.city_rules import (
    CITY_RULESET,
    CITY_SPACE_DEFINITIONS,
)


def test_city_ruleset_is_anchor_backed():
    assert CITY_RULESET.anchor_edition_id == "monopoly-1790"


def test_city_spaces_loaded_for_runtime_resolution():
    assert len(CITY_SPACE_DEFINITIONS) > 0
    assert any(space["kind"] == "planning_permission" for space in CITY_SPACE_DEFINITIONS)
