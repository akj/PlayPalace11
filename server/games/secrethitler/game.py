"""Secret Hitler game implementation."""

from dataclasses import dataclass, field
from enum import Enum
import random

from ..base import Game
from ..registry import register_game
from .cards import (
    Policy,
    Party,
    Power,
    Role,
    ROLE_COUNTS,
    build_policy_deck,
)
from .player import SecretHitlerPlayer, SecretHitlerOptions


class Phase(str, Enum):
    LOBBY = "lobby"
    ROLE_REVEAL = "role_reveal"
    NOMINATION = "nomination"
    VOTING = "voting"
    PRES_LEGISLATION = "pres_legislation"
    CHAN_LEGISLATION = "chan_legislation"
    POWER_RESOLUTION = "power_resolution"
    GAME_OVER = "game_over"


@dataclass
@register_game
class SecretHitler(Game):
    """Secret Hitler — social-deduction legislative game, 5–10 players."""

    players: list[SecretHitlerPlayer] = field(default_factory=list)
    options: SecretHitlerOptions = field(default_factory=SecretHitlerOptions)

    # Phase
    phase: Phase = Phase.LOBBY

    # Deck
    deck: list[Policy] = field(default_factory=list)
    discard: list[Policy] = field(default_factory=list)

    # Track counts
    liberal_policies: int = 0
    fascist_policies: int = 0
    election_tracker: int = 0

    # Rotation
    president_seat: int = 0
    special_election_override: int | None = None
    current_president_seat: int | None = None
    current_chancellor_seat: int | None = None
    last_elected_president_seat: int | None = None
    last_elected_chancellor_seat: int | None = None

    # Nomination / voting
    nominee_chancellor_seat: int | None = None
    votes: dict[int, bool] = field(default_factory=dict)
    vote_call_deadline_tick: int | None = None
    role_ack_seats: set[int] = field(default_factory=set)

    # Legislation
    president_drawn_policies: list[Policy] | None = None
    chancellor_received_policies: list[Policy] | None = None
    veto_proposed: bool = False

    # Power resolution
    pending_power: Power = Power.NONE
    power_target_seat: int | None = None
    policy_peek_cards: list[Policy] | None = None

    # Flow control
    paused_for_reconnect: bool = False
    tick: int = 0
    game_over: bool = False
    winner: Party | None = None
    win_reason: str | None = None

    @classmethod
    def get_name(cls) -> str:
        return "Secret Hitler"

    @classmethod
    def get_type(cls) -> str:
        return "secrethitler"

    @classmethod
    def get_category(cls) -> str:
        return "category-social-deduction"

    @classmethod
    def get_min_players(cls) -> int:
        return 5

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> SecretHitlerPlayer:
        return SecretHitlerPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self):
        errors = super().prestart_validate()
        n = len([p for p in self.players if not p.is_spectator])
        if n < 5 or n > 10:
            errors.append("sh-error-need-5-players")
        return errors

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1

        active = [p for p in self.players if not p.is_spectator]
        n = len(active)
        if n < 5 or n > 10:
            return

        for i, p in enumerate(active):
            p.seat = i
            p.is_alive = True
            p.has_been_investigated = False
            p.connected = True

        libs, fascists, _hitler = ROLE_COUNTS[n]
        role_pool = (
            [Role.LIBERAL] * libs
            + [Role.FASCIST] * fascists
            + [Role.HITLER]
        )
        random.shuffle(role_pool)
        for p, role in zip(active, role_pool):
            p.role = role

        self.deck = build_policy_deck()
        random.shuffle(self.deck)
        self.discard = []

        self.liberal_policies = 0
        self.fascist_policies = 0
        self.election_tracker = 0
        self.president_seat = 0
        self.special_election_override = None
        self.current_president_seat = None
        self.current_chancellor_seat = None
        self.last_elected_president_seat = None
        self.last_elected_chancellor_seat = None

        self.nominee_chancellor_seat = None
        self.votes = {}
        self.vote_call_deadline_tick = None
        self.president_drawn_policies = None
        self.chancellor_received_policies = None
        self.veto_proposed = False
        self.pending_power = Power.NONE
        self.power_target_seat = None
        self.policy_peek_cards = None

        self.paused_for_reconnect = False
        self.game_over = False
        self.winner = None
        self.win_reason = None
        self.role_ack_seats = set()

        self.phase = Phase.ROLE_REVEAL
        self._deliver_role_reveals()

    def _deliver_role_reveals(self) -> None:
        """Send each player a personal message about their role and, if applicable, teammates."""
        active = [p for p in self.players if not p.is_spectator]
        n = len(active)
        fascists = [p for p in active if p.role == Role.FASCIST]
        hitler = next(p for p in active if p.role == Role.HITLER)

        for p in active:
            user = self.get_user(p)
            if not user:
                continue
            if p.role == Role.LIBERAL:
                user.speak_l("sh-you-are-liberal", "table")
            elif p.role == Role.FASCIST:
                teammate_names = ", ".join(f.name for f in fascists if f is not p)
                user.speak_l("sh-you-are-fascist", "table")
                user.speak_l(
                    "sh-fascist-teammates",
                    "table",
                    names=teammate_names,
                    hitler=hitler.name,
                )
            elif p.role == Role.HITLER:
                user.speak_l("sh-you-are-hitler", "table")
                if n <= 6:
                    teammate_names = ", ".join(f.name for f in fascists)
                    user.speak_l(
                        "sh-hitler-knows-teammates",
                        "table",
                        names=teammate_names,
                    )
