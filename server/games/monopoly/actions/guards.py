"""Guard helpers for Monopoly turn actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ....game_utils.actions import Visibility
from ...base import Player

if TYPE_CHECKING:
    from ..game import MonopolyGame


def is_banking_balance_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable bank balance checks only for electronic banking preset."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return "monopoly-action-disabled-for-preset"
    return None


def is_banking_balance_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show bank balance action only in electronic banking mode."""
    return game.turn_action_visibility(
        player,
        extra_condition=game._is_electronic_banking_preset(),
    )


def is_banking_transfer_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable manual transfer only when options are available."""
    error = is_banking_balance_enabled(game, player)
    if error:
        return error
    if not game._options_for_banking_transfer(player):
        return "monopoly-not-enough-cash"
    return None


def is_banking_transfer_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show transfer action only when electronic transfer options exist."""
    return game.turn_action_visibility(
        player,
        extra_condition=game._is_electronic_banking_preset()
        and bool(game._options_for_banking_transfer(player)),
    )


def is_banking_ledger_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable ledger announcements in electronic banking mode."""
    return is_banking_balance_enabled(game, player)


def is_banking_ledger_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show ledger action only in electronic banking mode."""
    return game.turn_action_visibility(
        player,
        extra_condition=game._is_electronic_banking_preset(),
    )


def is_voice_command_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable voice command entry only for voice banking preset."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game.active_preset_id != "voice_banking":
        return "monopoly-action-disabled-for-preset"
    return None


def is_voice_command_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show voice command entry only during voice banking games."""
    return game.turn_action_visibility(
        player,
        extra_condition=game.active_preset_id == "voice_banking",
    )
