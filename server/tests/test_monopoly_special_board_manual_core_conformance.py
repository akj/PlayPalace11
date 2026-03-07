"""Conformance tests for all special-board parity promotion targets."""

import pytest

from server.games.monopoly.board_parity import get_board_parity_profile
from server.games.monopoly.board_profile import BOARD_PROFILES, DEFAULT_BOARD_ID


ALL_SPECIAL_BOARD_IDS = sorted(
    board_id for board_id in BOARD_PROFILES if board_id != DEFAULT_BOARD_ID
)


@pytest.mark.parametrize("board_id", ALL_SPECIAL_BOARD_IDS)
def test_special_board_reaches_manual_core(board_id: str):
    profile = get_board_parity_profile(board_id)

    assert profile is not None
    assert profile.fidelity_status == "manual_core"
