"""Validation tests for Mario manual rule data artifacts."""

import pytest

from server.games.monopoly.manual_rules.loader import load_manual_rule_set
from server.games.monopoly.manual_rules.validator import validate_manual_rule_set


@pytest.mark.parametrize(
    "board_id",
    [
        "mario_collectors",
        "mario_kart",
        "mario_celebration",
        "mario_movie",
        "junior_super_mario",
    ],
)
def test_mario_manual_rule_data_exists_and_validates(board_id: str):
    rule_set = load_manual_rule_set(board_id)

    assert rule_set.board_id == board_id
    assert validate_manual_rule_set(rule_set) == []
