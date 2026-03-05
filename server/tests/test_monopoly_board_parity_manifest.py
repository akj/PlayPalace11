"""Tests for Monopoly special-board parity manifest scaffolding."""

from server.games.monopoly.board_parity import (
    get_board_parity_profile,
    get_parity_board_ids,
)
from server.games.monopoly.board_profile import DEFAULT_BOARD_ID, get_available_board_ids


def test_parity_manifest_contains_all_special_boards():
    expected_special_boards = {
        board_id for board_id in get_available_board_ids() if board_id != DEFAULT_BOARD_ID
    }
    ids = set(get_parity_board_ids())

    assert expected_special_boards.issubset(ids)


def test_parity_manifest_has_anchor_and_fidelity_fields():
    profile = get_board_parity_profile("mario_kart")

    assert profile is not None
    assert profile.anchor_edition_id.startswith("monopoly-")
    assert profile.canonical_manual_edition_id == profile.anchor_edition_id
    assert profile.fidelity_status in {"partial", "partial_plus", "manual_core", "near_full"}


def test_parity_manifest_exposes_hardware_capability_subset():
    profile = get_board_parity_profile("junior_super_mario")

    assert profile is not None
    assert "junior_powerup_sound_ready" in profile.capability_ids
    assert "junior_powerup_sound_ready" in profile.hardware_capability_ids


def test_parity_manifest_exposes_star_wars_audio_hardware_capability_subset():
    profile = get_board_parity_profile("star_wars_mandalorian")

    assert profile is not None
    assert "audio_theme_event" in profile.capability_ids
    assert "audio_theme_event" in profile.hardware_capability_ids


def test_parity_manifest_exposes_mario_question_block_hardware_capability_subset():
    profile = get_board_parity_profile("mario_celebration")

    assert profile is not None
    assert "question_block_sound_unit" in profile.capability_ids
    assert "question_block_sound_unit" in profile.hardware_capability_ids
