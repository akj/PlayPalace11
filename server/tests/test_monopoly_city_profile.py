"""Tests for Monopoly City profile resolver."""

from server.games.monopoly.city_profile import (
    DEFAULT_CITY_PROFILE,
    resolve_city_profile,
)


def test_resolve_city_profile_uses_city_anchor_defaults():
    profile = resolve_city_profile("city")
    assert profile.preset_id == "city"
    assert profile.anchor_edition_id == "monopoly-1790"
    assert profile.source_policy == "anchor-first"
    assert profile.win_rule_key != ""


def test_resolve_city_profile_falls_back_to_default():
    assert resolve_city_profile("unknown") == DEFAULT_CITY_PROFILE
