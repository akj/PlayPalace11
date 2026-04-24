"""Executive power resolution for Secret Hitler.

Each resolver mutates the game state and returns the primary side-effect
the caller needs (e.g., whether execution ended the game). The phase
machine in game.py is responsible for what comes next.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .cards import Role

if TYPE_CHECKING:
    from .game import SecretHitler
    from .player import SecretHitlerPlayer


def resolve_investigate(
    game: "SecretHitler",
    president: "SecretHitlerPlayer",
    target: "SecretHitlerPlayer",
) -> None:
    """Reveal target's party affiliation privately to the president."""
    target.has_been_investigated = True
    party = target.role.party  # Hitler.party == Party.FASCIST
    user = game.get_user(president)
    if user:
        user.speak_l(
            "sh-you-see-party",
            "table",
            player=target.name,
            party=party.value,
        )


def resolve_policy_peek(game: "SecretHitler", president: "SecretHitlerPlayer") -> None:
    """Deliver the top-three deck contents privately to the president."""
    game._ensure_deck_has(3)
    top3 = list(game.deck[:3])
    game.policy_peek_cards = top3
    user = game.get_user(president)
    if user:
        user.speak_l(
            "sh-you-peek",
            "table",
            p1=top3[0].value,
            p2=top3[1].value,
            p3=top3[2].value,
        )


def resolve_execution(
    game: "SecretHitler",
    president: "SecretHitlerPlayer",
    target: "SecretHitlerPlayer",
) -> bool:
    """Execute target. Returns True if this ends the game (Hitler was killed)."""
    target.is_alive = False
    game.broadcast_l("sh-player-executed", player=target.name)
    if target.role == Role.HITLER:
        return True
    return False
