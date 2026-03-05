"""Tests for Monopoly manual rule dataclass models."""

import pytest

from server.games.monopoly.manual_rules.models import ManualRuleSet


def test_manual_rule_set_requires_citations():
    payload = {
        "board_id": "mario_kart",
        "anchor_edition_id": "monopoly-e1870",
        "board": {"spaces": []},
        "economy": {"properties": {}},
        "cards": {"chance": [], "community_chest": []},
        "mechanics": {},
        "win_condition": {"type": "bankruptcy"},
        "citations": [],
    }

    with pytest.raises(ValueError, match="citations must be non-empty"):
        ManualRuleSet.from_dict(payload)


def test_manual_rule_set_from_dict_parses_citations():
    payload = {
        "board_id": "mario_kart",
        "anchor_edition_id": "monopoly-e1870",
        "board": {"spaces": []},
        "economy": {"properties": {}},
        "cards": {"chance": [], "community_chest": []},
        "mechanics": {},
        "win_condition": {"type": "bankruptcy"},
        "citations": [
            {
                "rule_path": "cards.chance",
                "edition_id": "monopoly-e1870",
                "page_ref": "p.8",
                "confidence": "high",
            }
        ],
    }

    rules = ManualRuleSet.from_dict(payload)

    assert rules.board_id == "mario_kart"
    assert rules.citations[0].rule_path == "cards.chance"
