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
