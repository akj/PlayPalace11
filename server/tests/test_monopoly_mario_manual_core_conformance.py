"""Conformance tests for Mario board manual-core parity promotion."""

import pytest

from server.games.monopoly.board_parity import get_board_parity_profile


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
def test_mario_board_reaches_manual_core(board_id: str):
    profile = get_board_parity_profile(board_id)

    assert profile is not None
    assert profile.fidelity_status == "manual_core"
