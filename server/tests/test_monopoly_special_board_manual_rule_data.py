"""Validation coverage for non-Mario special board manual rule artifacts."""

import pytest

from server.games.monopoly.board_profile import BOARD_PROFILES, DEFAULT_BOARD_ID
from server.games.monopoly.manual_rules.loader import load_manual_rule_set
from server.games.monopoly.manual_rules.validator import validate_manual_rule_set


MARIO_BOARD_IDS = {
    "mario_collectors",
    "mario_kart",
    "mario_celebration",
    "mario_movie",
    "junior_super_mario",
}

ALL_SPECIAL_NON_MARIO_BOARD_IDS = sorted(
    board_id
    for board_id in BOARD_PROFILES
    if board_id != DEFAULT_BOARD_ID and board_id not in MARIO_BOARD_IDS
)


@pytest.mark.parametrize("board_id", ALL_SPECIAL_NON_MARIO_BOARD_IDS)
def test_special_board_manual_rule_data_validates(board_id: str):
    rule_set = load_manual_rule_set(board_id)

    assert rule_set.board_id == board_id
    assert validate_manual_rule_set(rule_set) == []
