"""Tests for Secret Hitler game."""

import pytest
from server.games.registry import GameRegistry
from server.games.secrethitler.cards import (
    Policy,
    Role,
    Party,
    Power,
    ROLE_COUNTS,
    FASCIST_TRACK_POWERS,
    build_policy_deck,
)


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


def test_role_counts_by_player_count():
    assert ROLE_COUNTS[5] == (3, 1, 1)
    assert ROLE_COUNTS[6] == (4, 1, 1)
    assert ROLE_COUNTS[7] == (4, 2, 1)
    assert ROLE_COUNTS[8] == (5, 2, 1)
    assert ROLE_COUNTS[9] == (5, 3, 1)
    assert ROLE_COUNTS[10] == (6, 3, 1)


def test_fascist_track_powers_5_6():
    track = FASCIST_TRACK_POWERS["5-6"]
    assert track == (
        Power.NONE,
        Power.NONE,
        Power.POLICY_PEEK,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_fascist_track_powers_7_8():
    track = FASCIST_TRACK_POWERS["7-8"]
    assert track == (
        Power.NONE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_fascist_track_powers_9_10():
    track = FASCIST_TRACK_POWERS["9-10"]
    assert track == (
        Power.INVESTIGATE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_policy_deck_composition():
    deck = build_policy_deck()
    assert len(deck) == 17
    assert deck.count(Policy.LIBERAL) == 6
    assert deck.count(Policy.FASCIST) == 11


def test_party_of_role():
    assert Role.LIBERAL.party is Party.LIBERAL
    assert Role.FASCIST.party is Party.FASCIST
    assert Role.HITLER.party is Party.FASCIST


from server.games.secrethitler.player import (
    SecretHitlerPlayer,
    SecretHitlerOptions,
)
from server.games.secrethitler.game import SecretHitler


def test_player_defaults():
    p = SecretHitlerPlayer(id="x", name="Alice")
    assert p.seat == 0
    assert p.role == Role.LIBERAL
    assert p.is_alive is True
    assert p.has_been_investigated is False
    assert p.connected is True


def test_options_defaults():
    o = SecretHitlerOptions()
    assert o.president_vote_timeout_seconds == 180
    assert o.bot_think_seconds == 2


def test_game_creates_typed_players_and_options():
    g = SecretHitler()
    p = g.create_player("player1", "Alice")
    assert isinstance(p, SecretHitlerPlayer)
    assert isinstance(g.options, SecretHitlerOptions)


from pathlib import Path


def test_locale_file_exists_and_has_game_name_key():
    locale_path = Path(__file__).parent.parent / "locales" / "en" / "secrethitler.ftl"
    assert locale_path.exists(), f"Missing locale file: {locale_path}"
    text = locale_path.read_text(encoding="utf-8")
    assert "game-name-secrethitler = Secret Hitler" in text
    for key in (
        "sh-you-are-liberal",
        "sh-you-are-fascist",
        "sh-you-are-hitler",
        "sh-fascist-teammates",
    ):
        assert key in text, f"Missing key {key} in locale file"
