"""Option helpers for Monopoly turn actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...base import Player

if TYPE_CHECKING:
    from ..game import MonopolyGame


def encode_banking_transfer_option(game: MonopolyGame, target: Player, amount: int) -> str:
    """Encode one banking transfer option for menu selection."""
    _ = game
    return f"Transfer {amount} to {target.name} ## target={target.id};amount={amount}"


def parse_banking_transfer_option(game: MonopolyGame, option: str) -> tuple[str, int] | None:
    """Parse one banking transfer option from menu input."""
    _ = game
    if "##" not in option:
        return None
    _, raw_meta = option.split("##", 1)
    meta: dict[str, str] = {}
    for part in raw_meta.strip().split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        meta[key.strip()] = value.strip()

    target_id = meta.get("target", "")
    if not target_id:
        return None
    try:
        amount = int(meta.get("amount", "0"))
    except ValueError:
        return None
    if amount <= 0:
        return None
    return target_id, amount


def options_for_banking_transfer(game: MonopolyGame, player: Player) -> list[str]:
    """Menu options for player-to-player transfers in electronic mode."""
    mono_player = player  # type: ignore[assignment]
    if (
        not game._is_electronic_banking_preset()
        or game.banking_state is None
        or game.banking_profile is None
        or not game.banking_profile.allow_manual_transfers
    ):
        return []

    balance = game._current_liquid_balance(mono_player)
    if balance <= 0:
        return []

    base_amounts = [10, 20, 50, 100, 200, 500]
    options: list[str] = []
    for target in game.turn_players:
        if target.id == mono_player.id or target.bankrupt:
            continue
        target_amounts = sorted(
            {
                amount
                for amount in [*base_amounts, balance]
                if amount > 0 and amount <= balance
            }
        )
        for amount in target_amounts:
            options.append(encode_banking_transfer_option(game, target, amount))
    return options
