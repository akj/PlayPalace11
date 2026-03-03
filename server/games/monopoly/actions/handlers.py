"""Handler helpers for Monopoly turn actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...base import Player
from ..voice_commands import parse_voice_command

if TYPE_CHECKING:
    from ..game import MonopolyGame


def action_banking_balance(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Announce current electronic bank balance to the requesting player."""
    _ = action_id
    if not game._is_electronic_banking_preset():
        return
    mono_player = player  # type: ignore[assignment]
    user = game.get_user(player)
    if user:
        user.speak_l(
            "monopoly-banking-balance-report",
            player=mono_player.name,
            cash=game._bank_balance(mono_player),
        )


def action_banking_transfer(game: MonopolyGame, player: Player, option: str, action_id: str) -> None:
    """Execute one manual bank transfer between players."""
    _ = action_id
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return
    mono_player = player  # type: ignore[assignment]
    if option not in game._options_for_banking_transfer(player):
        return
    parsed = game._parse_banking_transfer_option(option)
    if not parsed:
        return

    target_id, amount = parsed
    target = game.get_player_by_id(target_id)
    if not target or target.bankrupt:
        return

    transferred = game._transfer_between_players(
        mono_player,
        target,
        amount,
        "manual_transfer",
    )
    if transferred == amount:
        game.broadcast_l(
            "monopoly-banking-transfer-success",
            from_player=mono_player.name,
            to_player=target.name,
            amount=transferred,
        )
    else:
        game.broadcast_l(
            "monopoly-banking-transfer-failed",
            player=mono_player.name,
            reason="insufficient_funds",
        )

    game._sync_cash_scores()
    game.rebuild_all_menus()


def action_banking_ledger(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Announce recent banking ledger events to the requesting player."""
    _ = action_id
    user = game.get_user(player)
    if not user:
        return
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return

    entries: list[str] = []
    for tx in game.banking_state.ledger[-5:]:
        if tx.status == "success":
            entries.append(
                f"{tx.tx_id} {tx.kind} {tx.from_id}->{tx.to_id} {tx.amount} ({tx.reason})"
            )
        else:
            entries.append(
                f"{tx.tx_id} {tx.kind} failed ({tx.failure_reason or 'unknown'})"
            )

    if not entries:
        user.speak_l("monopoly-banking-ledger-empty")
        return
    user.speak_l("monopoly-banking-ledger-report", entries=" | ".join(entries))


def action_voice_command(game: MonopolyGame, player: Player, text: str, action_id: str) -> None:
    """Parse and execute one voice-style command in voice banking preset."""
    if game.active_preset_id != "voice_banking":
        return
    mono_player = player  # type: ignore[assignment]
    parsed = parse_voice_command(text)

    user = game.get_user(player)
    if parsed.error:
        game.voice_last_response_by_player_id[mono_player.id] = parsed.error
        if user:
            user.speak_l("monopoly-voice-command-error", reason=parsed.error)
        return

    if parsed.intent == "check_balance":
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        if user:
            user.speak_l(
                "monopoly-banking-balance-report",
                player=mono_player.name,
                cash=game._bank_balance(mono_player),
            )
        return

    if parsed.intent == "show_recent_ledger":
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        action_banking_ledger(game, player, action_id)
        return

    if parsed.intent == "repeat_last_bank_result":
        previous = game.voice_last_response_by_player_id.get(mono_player.id, "none")
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        if user:
            user.speak_l("monopoly-voice-command-repeat", response=previous)
        return

    if parsed.intent == "transfer_amount_to_player":
        target = None
        wanted_name = parsed.target_name.strip().lower()
        for turn_player in game.turn_players:
            if turn_player.id == mono_player.id or turn_player.bankrupt:
                continue
            if turn_player.name.lower() == wanted_name:
                target = turn_player
                break

        if target is None:
            game.voice_last_response_by_player_id[mono_player.id] = "invalid_target"
            if user:
                user.speak_l("monopoly-voice-command-error", reason="invalid_target")
            return

        game.voice_pending_transfer_by_player_id[mono_player.id] = (target.id, parsed.amount)
        game.voice_last_response_by_player_id[mono_player.id] = "transfer_pending_confirm"
        if user:
            user.speak_l(
                "monopoly-voice-transfer-staged",
                amount=parsed.amount,
                target=target.name,
            )
        return

    if parsed.intent == "confirm_transfer":
        pending = game.voice_pending_transfer_by_player_id.get(mono_player.id)
        if not pending:
            game.voice_last_response_by_player_id[mono_player.id] = "no_pending_transfer"
            if user:
                user.speak_l("monopoly-voice-command-error", reason="no_pending_transfer")
            return

        target_id, amount = pending
        target = game.get_player_by_id(target_id)
        if not target or target.bankrupt:
            game.voice_pending_transfer_by_player_id.pop(mono_player.id, None)
            game.voice_last_response_by_player_id[mono_player.id] = "invalid_target"
            if user:
                user.speak_l("monopoly-voice-command-error", reason="invalid_target")
            return

        transferred = game._transfer_between_players(
            mono_player,
            target,
            amount,
            "voice_transfer",
        )
        game.voice_pending_transfer_by_player_id.pop(mono_player.id, None)
        if transferred == amount:
            game.voice_last_response_by_player_id[mono_player.id] = "transfer_confirmed"
            game.broadcast_l(
                "monopoly-banking-transfer-success",
                from_player=mono_player.name,
                to_player=target.name,
                amount=transferred,
            )
            game._sync_cash_scores()
            game.rebuild_all_menus()
        else:
            game.voice_last_response_by_player_id[mono_player.id] = "insufficient_funds"
            if user:
                user.speak_l("monopoly-voice-command-error", reason="insufficient_funds")
        return

    game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
    if user:
        user.speak_l("monopoly-voice-command-accepted", intent=parsed.intent)
