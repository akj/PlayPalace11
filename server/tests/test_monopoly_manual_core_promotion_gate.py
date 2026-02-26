"""Tests for manual-core promotion gating helpers."""

from server.games.monopoly.board_parity import can_promote_manual_core
from server.games.monopoly.manual_rules.models import ManualRuleSet


def test_manual_core_gate_returns_false_when_validation_fails(monkeypatch):
    rule_set = ManualRuleSet.from_dict(
        {
            "board_id": "star_wars_40th",
            "anchor_edition_id": "monopoly-e1870",
            "board": {"spaces": []},
            "economy": {"properties": {}},
            "cards": {"chance": [], "community_chest": []},
            "mechanics": {},
            "win_condition": {"type": "bankruptcy"},
            "citations": [
                {
                    "rule_path": "board.spaces",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.2",
                    "confidence": "high",
                }
            ],
        }
    )
    monkeypatch.setattr(
        "server.games.monopoly.board_parity.load_manual_rule_set",
        lambda board_id: rule_set,
    )
    monkeypatch.setattr(
        "server.games.monopoly.board_parity.validate_manual_rule_set",
        lambda rs: ["cards.chance missing citation"],
    )

    assert can_promote_manual_core("star_wars_40th") is False


def test_manual_core_gate_returns_true_for_valid_rule_set(monkeypatch):
    rule_set = ManualRuleSet.from_dict(
        {
            "board_id": "mario_kart",
            "anchor_edition_id": "monopoly-e1870",
            "board": {"spaces": []},
            "economy": {"properties": {}},
            "cards": {"chance": [], "community_chest": []},
            "mechanics": {},
            "win_condition": {"type": "bankruptcy"},
            "citations": [
                {
                    "rule_path": "board.spaces",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.2",
                    "confidence": "high",
                },
                {
                    "rule_path": "economy.properties",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.4",
                    "confidence": "high",
                },
                {
                    "rule_path": "cards.chance",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.7",
                    "confidence": "high",
                },
                {
                    "rule_path": "cards.community_chest",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.8",
                    "confidence": "high",
                },
                {
                    "rule_path": "win_condition",
                    "edition_id": "monopoly-e1870",
                    "page_ref": "p.11",
                    "confidence": "high",
                },
            ],
        }
    )

    monkeypatch.setattr(
        "server.games.monopoly.board_parity.load_manual_rule_set",
        lambda board_id: rule_set,
    )

    assert can_promote_manual_core("mario_kart") is True
