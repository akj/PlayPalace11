"""Minimal bot for Secret Hitler. Plays legally; does not strategize."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.bot_helper import BotHelper
from .cards import Policy, Role, Power

if TYPE_CHECKING:
    from .game import SecretHitler
    from .player import SecretHitlerPlayer


class SecretHitlerBot(BotHelper):
    """Legal-only bot for Secret Hitler."""

    @classmethod
    def bot_think(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str | None:
        # Local import to avoid circular dependency.
        from .game import Phase

        if player.bot_think_ticks > 0:
            player.bot_think_ticks -= 1
            return None

        phase = game.phase

        if phase == Phase.ROLE_REVEAL:
            if player.seat not in game.role_ack_seats:
                return "acknowledge_role"
            return None

        if phase == Phase.NOMINATION:
            if player.seat != game.current_president_seat:
                return None
            if game.nominee_chancellor_seat is None:
                eligible = game._eligible_chancellor_seats()
                if not eligible:
                    return None
                seat = random.choice(eligible)
                return f"nominate_{seat}"
            return "call_vote"

        if phase == Phase.VOTING:
            if not player.is_alive:
                return None
            if player.seat in game.votes:
                return None
            return cls._pick_vote(game, player)

        if phase == Phase.PRES_LEGISLATION:
            if player.seat != game.current_president_seat:
                return None
            return cls._pick_discard(game, player)

        if phase == Phase.CHAN_LEGISLATION:
            if game.veto_proposed:
                # President decides veto accept/reject.
                if player.seat == game.current_president_seat:
                    # Liberal pres → accept; fascist pres → reject (wants to enact).
                    if player.role == Role.LIBERAL:
                        return "veto_accept"
                    return "veto_reject"
                return None
            if player.seat != game.current_chancellor_seat:
                return None
            return cls._pick_enact_or_veto(game, player)

        if phase == Phase.POWER_RESOLUTION:
            if player.seat != game.current_president_seat:
                return None
            return cls._pick_power(game, player)

        return None

    @classmethod
    def _pick_vote(cls, game: "SecretHitler", player: "SecretHitlerPlayer") -> str:
        from .player import SecretHitlerPlayer as _P

        chancellor = next(
            p for p in game.players
            if isinstance(p, _P) and p.seat == game.nominee_chancellor_seat
        )
        if player.role == Role.HITLER:
            return "vote_ja"
        if player.role == Role.FASCIST:
            pres = next(
                p for p in game.players
                if isinstance(p, _P) and p.seat == game.current_president_seat
            )
            if pres.role in (Role.FASCIST, Role.HITLER) or chancellor.role in (
                Role.FASCIST, Role.HITLER
            ):
                return "vote_ja"
            return "vote_ja" if random.random() < 0.5 else "vote_nein"
        return "vote_ja" if random.random() < 0.6 else "vote_nein"

    @classmethod
    def _pick_discard(cls, game: "SecretHitler", player: "SecretHitlerPlayer") -> str:
        want = Policy.LIBERAL if player.role == Role.LIBERAL else Policy.FASCIST
        cards = game.president_drawn_policies or []
        unwanted = Policy.FASCIST if want == Policy.LIBERAL else Policy.LIBERAL
        candidates = [i for i, c in enumerate(cards) if c == unwanted]
        if candidates:
            return f"discard_{random.choice(candidates)}"
        if not cards:
            return "discard_0"
        return f"discard_{random.randint(0, len(cards) - 1)}"

    @classmethod
    def _pick_enact_or_veto(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str:
        cards = game.chancellor_received_policies or []
        # Consider veto when available and both cards are undesirable.
        if game.fascist_policies >= 5 and not game.veto_blocked_this_turn:
            want = Policy.LIBERAL if player.role == Role.LIBERAL else Policy.FASCIST
            if all(c != want for c in cards):
                return "propose_veto"
        want = Policy.LIBERAL if player.role == Role.LIBERAL else Policy.FASCIST
        candidates = [i for i, c in enumerate(cards) if c == want]
        if candidates:
            return f"enact_{random.choice(candidates)}"
        if not cards:
            return "enact_0"
        return f"enact_{random.randint(0, len(cards) - 1)}"

    @classmethod
    def _pick_power(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str | None:
        power = game.pending_power
        alive_others = [
            p.seat for p in game.players
            if isinstance(p, type(player)) and p.is_alive and p.seat != player.seat
        ]
        if power == Power.INVESTIGATE:
            eligible = [
                p.seat for p in game.players
                if isinstance(p, type(player))
                and p.is_alive
                and p.seat != player.seat
                and not p.has_been_investigated
            ]
            if not eligible:
                return None
            return f"investigate_{random.choice(eligible)}"
        if power == Power.SPECIAL_ELECTION:
            if not alive_others:
                return None
            return f"choose_president_{random.choice(alive_others)}"
        if power == Power.POLICY_PEEK:
            return "acknowledge_peek"
        if power == Power.EXECUTION:
            if not alive_others:
                return None
            return f"execute_{random.choice(alive_others)}"
        return None
