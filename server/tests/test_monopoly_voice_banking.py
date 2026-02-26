"""Integration tests for Monopoly voice banking preset behavior."""

from server.games.monopoly.game import MonopolyGame, MonopolyOptions
from server.users.test_user import MockUser


def _create_two_player_game(options: MonopolyOptions | None = None) -> MonopolyGame:
    game = MonopolyGame(options=options or MonopolyOptions())
    host_user = MockUser("Host")
    guest_user = MockUser("Guest")
    game.add_player("Host", host_user)
    game.add_player("Guest", guest_user)
    game.host = "Host"
    return game


def _start_two_player_game(options: MonopolyOptions | None = None) -> MonopolyGame:
    game = _create_two_player_game(options)
    game.on_start()
    return game


def test_voice_banking_on_start_initializes_profile_and_accounts():
    game = _start_two_player_game(MonopolyOptions(preset_id="voice_banking"))
    assert game.voice_banking_profile is not None
    assert game.voice_banking_profile.anchor_edition_id == "monopoly-e4816"
    assert game.banking_state is not None
    assert game._bank_balance(game.players[0]) > 0
