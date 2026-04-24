"""Player and Options dataclasses for Secret Hitler."""

from dataclasses import dataclass

from ..base import Player, GameOptions
from ...game_utils.options import IntOption, option_field
from .cards import Role


@dataclass
class SecretHitlerPlayer(Player):
    """Player state for Secret Hitler."""

    seat: int = 0
    role: Role = Role.LIBERAL
    is_alive: bool = True
    has_been_investigated: bool = False
    connected: bool = True


@dataclass
class SecretHitlerOptions(GameOptions):
    """Lobby options for Secret Hitler."""

    president_vote_timeout_seconds: int = option_field(
        IntOption(
            default=180,
            min_val=30,
            max_val=600,
            value_key="seconds",
            label="sh-set-vote-timeout",
            prompt="sh-enter-vote-timeout",
            change_msg="sh-option-changed-vote-timeout",
            description="sh-desc-vote-timeout",
        )
    )
    bot_think_seconds: int = option_field(
        IntOption(
            default=2,
            min_val=0,
            max_val=10,
            value_key="seconds",
            label="sh-set-bot-think",
            prompt="sh-enter-bot-think",
            change_msg="sh-option-changed-bot-think",
            description="sh-desc-bot-think",
        )
    )
