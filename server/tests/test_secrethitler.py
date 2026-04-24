"""Tests for Secret Hitler game."""

import pytest
from server.games.registry import GameRegistry


def test_game_registered():
    """Secret Hitler must be registered under type 'secrethitler'."""
    cls = GameRegistry.get("secrethitler")
    assert cls is not None
    assert cls.get_type() == "secrethitler"
    assert cls.get_name() == "Secret Hitler"


def test_player_count_bounds():
    cls = GameRegistry.get("secrethitler")
    assert cls.get_min_players() == 5
    assert cls.get_max_players() == 10
