"""Tests for Monopoly board deck provider resolution."""

from server.games.monopoly.deck_provider import resolve_deck_provider


def test_resolve_deck_provider_uses_classic_by_default():
    provider = resolve_deck_provider("mario_kart", deck_mode="classic")

    assert provider.board_id == "mario_kart"
    assert provider.mode == "classic"


def test_resolve_deck_provider_supports_board_specific_mode():
    provider = resolve_deck_provider("star_wars_mandalorian", deck_mode="board_specific")

    assert provider.board_id == "star_wars_mandalorian"
    assert provider.mode == "board_specific"


def test_resolve_deck_provider_falls_back_for_unknown_mode():
    provider = resolve_deck_provider("mario_kart", deck_mode="unexpected")

    assert provider.mode == "classic"
