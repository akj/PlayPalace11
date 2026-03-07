"""Tests for Monopoly manual rule loader."""

from __future__ import annotations

from server.games.monopoly.manual_rules.loader import load_manual_rule_set


def test_loader_reads_board_rule_json(tmp_path):
    board_file = tmp_path / "mario_kart.json"
    board_file.write_text(
        (
            '{"board_id":"mario_kart","anchor_edition_id":"monopoly-e1870",'
            '"board":{"spaces":[]},"economy":{"properties":{}},'
            '"cards":{"chance":[],"community_chest":[]},"mechanics":{},'
            '"win_condition":{"type":"bankruptcy"},'
            '"citations":[{"rule_path":"cards.chance","edition_id":"monopoly-e1870",'
            '"page_ref":"p.8","confidence":"high"}]}'
        ),
        encoding="utf-8",
    )

    rules = load_manual_rule_set("mario_kart", data_dir=tmp_path)

    assert rules.board_id == "mario_kart"
    assert rules.anchor_edition_id == "monopoly-e1870"
