"""Contract tests for finalized Marvel native-card literal slot handling."""

from __future__ import annotations

import pytest

from server.games.monopoly.manual_rules.loader import load_manual_rule_set


@pytest.mark.parametrize("board_id", ("marvel_avengers_legacy", "marvel_flip"))
def test_remaining_marvel_native_slots_no_longer_use_not_observed_status(board_id: str):
    rule_set = load_manual_rule_set(board_id)
    unresolved = [
        card
        for deck_id in ("chance", "community_chest")
        for card in rule_set.cards.get(deck_id, [])
        if card.get("text_status") == "not_observed_in_available_manual_sources"
    ]

    assert unresolved == []
