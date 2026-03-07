"""Tests for Monopoly cheaters profile resolver."""

from server.games.monopoly.cheaters_profile import (
    DEFAULT_CHEATERS_PROFILE,
    resolve_cheaters_profile,
)


def test_resolve_cheaters_profile_uses_anchor_defaults():
    profile = resolve_cheaters_profile("cheaters")
    assert profile.preset_id == "cheaters"
    assert profile.anchor_edition_id == "monopoly-e4888"
    assert profile.source_policy == "anchor-first"
    assert "early_end_turn" in profile.enabled_rules


def test_resolve_cheaters_profile_falls_back_to_default():
    profile = resolve_cheaters_profile("unknown")
    assert profile == DEFAULT_CHEATERS_PROFILE
