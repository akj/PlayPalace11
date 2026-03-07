"""Tests for deterministic Monopoly City engine behavior."""

from server.games.monopoly.city_engine import CityEngine
from server.games.monopoly.city_profile import DEFAULT_CITY_PROFILE


def test_city_engine_initializes_turn_state():
    engine = CityEngine(DEFAULT_CITY_PROFILE)
    engine.on_turn_start("p1", 0)
    assert engine.current_turn_player_id == "p1"


def test_city_engine_reports_winner_when_threshold_reached():
    engine = CityEngine(DEFAULT_CITY_PROFILE)
    engine.record_progress("p1", DEFAULT_CITY_PROFILE.win_threshold)
    winner = engine.evaluate_winner(("p1", "p2"))
    assert winner == "p1"
