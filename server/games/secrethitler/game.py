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
    FASCIST_TRACK_POWERS,
    build_policy_deck,
    track_bucket_for,
)
from .player import SecretHitlerPlayer, SecretHitlerOptions
from . import powers


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
    veto_blocked_this_turn: bool = False
    _first_nomination: bool = True
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
        self.veto_blocked_this_turn = False
        self._first_nomination = True
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

    # ------------------------------------------------------------------
    # Task 7 — Role acknowledgement → NOMINATION
    # ------------------------------------------------------------------

    def _action_acknowledge_role(self, player, action_id: str) -> None:
        """Record that `player` has acknowledged their role."""
        if self.phase != Phase.ROLE_REVEAL:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        self.role_ack_seats.add(player.seat)
        active = [p for p in self.players if not p.is_spectator]
        if all(p.seat in self.role_ack_seats for p in active):
            self._begin_nomination()

    def _begin_nomination(self) -> None:
        self.phase = Phase.NOMINATION
        self.current_president_seat = self._next_president_seat()
        self.current_chancellor_seat = None
        self.nominee_chancellor_seat = None
        self.votes = {}
        self.vote_call_deadline_tick = None
        pres = self._player_at_seat(self.current_president_seat)
        self.broadcast_l("sh-president-is", player=pres.name)

    def _next_president_seat(self) -> int:
        """Compute the next president seat, consuming special-election override if set."""
        if self.special_election_override is not None:
            seat = self.special_election_override
            self.special_election_override = None
            # Intentionally do NOT update president_seat so rotation resumes from the
            # original seat after the special election. (See Task 16.)
            return seat
        active_alive = sorted(
            p.seat for p in self.players if not p.is_spectator and p.is_alive
        )
        if not active_alive:
            return 0
        if self._first_nomination:
            self._first_nomination = False
            self.president_seat = active_alive[0]
            return self.president_seat
        for seat in active_alive:
            if seat > self.president_seat:
                self.president_seat = seat
                return seat
        self.president_seat = active_alive[0]
        return self.president_seat

    def _player_at_seat(self, seat: int) -> SecretHitlerPlayer:
        for p in self.players:
            if isinstance(p, SecretHitlerPlayer) and p.seat == seat and not p.is_spectator:
                return p
        raise KeyError(f"No player at seat {seat}")

    # ------------------------------------------------------------------
    # Task 8 — Nomination and chancellor eligibility
    # ------------------------------------------------------------------

    def _alive_count(self) -> int:
        return sum(1 for p in self.players if not p.is_spectator and p.is_alive)

    def _eligible_chancellor_seats(self) -> list[int]:
        alive = [
            p.seat
            for p in self.players
            if not p.is_spectator
            and p.is_alive
            and p.seat != self.current_president_seat
        ]
        if self.last_elected_chancellor_seat in alive:
            alive.remove(self.last_elected_chancellor_seat)
        if self._alive_count() > 5 and self.last_elected_president_seat in alive:
            alive.remove(self.last_elected_president_seat)
        return sorted(alive)

    def _action_nominate(self, player, action_id: str) -> None:
        if self.phase != Phase.NOMINATION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        try:
            target_seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        if target_seat not in self._eligible_chancellor_seats():
            return
        self.nominee_chancellor_seat = target_seat
        chancellor = self._player_at_seat(target_seat)
        self.broadcast_l(
            "sh-president-nominates",
            president=player.name,
            chancellor=chancellor.name,
        )
        self.broadcast_l("sh-president-can-call-vote")
        self.vote_call_deadline_tick = self.tick + (
            self.options.president_vote_timeout_seconds * 20
        )

    def _action_cancel_nomination(self, player, action_id: str) -> None:
        if self.phase != Phase.NOMINATION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        self.nominee_chancellor_seat = None

    # ------------------------------------------------------------------
    # Task 9 — Call vote, tally, tracker advance, chaos
    # ------------------------------------------------------------------

    def _action_call_vote(self, player, action_id: str) -> None:
        if self.phase != Phase.NOMINATION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        if self.nominee_chancellor_seat is None:
            return
        self.vote_call_deadline_tick = None
        self.phase = Phase.VOTING
        self.votes = {}
        self.broadcast_l("sh-voting-open")

    def _action_vote_ja(self, player, action_id: str) -> None:
        self._record_vote(player, True)

    def _action_vote_nein(self, player, action_id: str) -> None:
        self._record_vote(player, False)

    def _record_vote(self, player, ja: bool) -> None:
        if self.phase != Phase.VOTING:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if not player.is_alive:
            return
        if player.seat in self.votes:
            return
        self.votes[player.seat] = ja
        user = self.get_user(player)
        if user:
            user.speak_l("sh-you-voted-ja" if ja else "sh-you-voted-nein", "table")
        if self._all_alive_voted():
            self._tally_vote()

    def _all_alive_voted(self) -> bool:
        alive_seats = {p.seat for p in self.players if not p.is_spectator and p.is_alive}
        return alive_seats <= set(self.votes.keys())

    def _tally_vote(self) -> None:
        for seat, ja in sorted(self.votes.items()):
            voter = self._player_at_seat(seat)
            self.broadcast_l(
                "sh-vote-roll-call",
                player=voter.name,
                vote="ja" if ja else "nein",
            )
        passed = sum(1 for v in self.votes.values() if v) > len(self.votes) / 2
        self.broadcast_l("sh-vote-result", passed="true" if passed else "false")
        if passed:
            self._on_vote_passed()
        else:
            self._on_vote_failed()

    def _on_vote_passed(self) -> None:
        self.veto_blocked_this_turn = False
        chancellor = self._player_at_seat(self.nominee_chancellor_seat)
        if self.fascist_policies >= 3 and chancellor.role == Role.HITLER:
            self._end_game(Party.FASCIST, "sh-fascists-win-hitler-elected")
            return
        self.last_elected_president_seat = self.current_president_seat
        self.last_elected_chancellor_seat = self.nominee_chancellor_seat
        self.current_chancellor_seat = self.nominee_chancellor_seat
        self.election_tracker = 0
        self._ensure_deck_has(3)
        self.president_drawn_policies = [self.deck.pop(0) for _ in range(3)]
        self.phase = Phase.PRES_LEGISLATION
        self.broadcast_l("sh-president-draws")
        pres = self._player_at_seat(self.current_president_seat)
        self._send_policies_private(pres, self.president_drawn_policies, "sh-your-policies")

    def _on_vote_failed(self) -> None:
        self.election_tracker += 1
        self.broadcast_l("sh-tracker-advances", count=self.election_tracker)
        if self.election_tracker >= 3:
            self._chaos_enact()
            return
        self._begin_nomination()

    def _ensure_deck_has(self, n: int) -> None:
        if len(self.deck) < n:
            self.deck = self.deck + self.discard
            random.shuffle(self.deck)
            self.discard = []

    def _send_policies_private(self, player, policies, key: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        args = {f"p{i + 1}": p.value for i, p in enumerate(policies)}
        user.speak_l(key, "table", **args)

    def _end_game(self, winner, reason_key: str) -> None:
        self.phase = Phase.GAME_OVER
        self.game_over = True
        self.winner = winner
        self.win_reason = reason_key
        self.broadcast_l(reason_key)
        lines = ", ".join(
            f"{p.name} ({p.role.value})"
            for p in self.players
            if not p.is_spectator
        )
        self.broadcast_l("sh-final-roles", lines=lines)

    def _chaos_enact(self) -> None:
        self._ensure_deck_has(1)
        top = self.deck.pop(0)
        self.broadcast_l("sh-chaos-top-policy")
        if top == Policy.LIBERAL:
            self.liberal_policies += 1
        else:
            self.fascist_policies += 1
        self.broadcast_l(
            "sh-chancellor-enacts",
            policy=top.value,
            liberal=self.liberal_policies,
            fascist=self.fascist_policies,
        )
        self.election_tracker = 0
        self.last_elected_president_seat = None
        self.last_elected_chancellor_seat = None
        if self._check_track_win():
            return
        self._begin_nomination()

    def _check_track_win(self) -> bool:
        if self.liberal_policies >= 5:
            self._end_game(Party.LIBERAL, "sh-liberals-win-policies")
            return True
        if self.fascist_policies >= 6:
            self._end_game(Party.FASCIST, "sh-fascists-win-policies")
            return True
        return False

    # ------------------------------------------------------------------
    # Task 10 — Vote auto-call on timeout
    # ------------------------------------------------------------------

    def on_tick(self) -> None:
        super().on_tick()
        if self.paused_for_reconnect:
            return
        self.tick += 1
        if (
            self.phase == Phase.NOMINATION
            and self.nominee_chancellor_seat is not None
            and self.vote_call_deadline_tick is not None
            and self.tick >= self.vote_call_deadline_tick
        ):
            pres = self._player_at_seat(self.current_president_seat)
            self._action_call_vote(pres, "call_vote")

    # ------------------------------------------------------------------
    # Task 11 — President discards → chancellor receives
    # ------------------------------------------------------------------

    def _action_discard_policy(self, player, action_id: str) -> None:
        if self.phase != Phase.PRES_LEGISLATION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        if idx < 0 or idx >= len(self.president_drawn_policies or []):
            return
        drawn = list(self.president_drawn_policies or [])
        discarded = drawn.pop(idx)
        self.discard.append(discarded)
        self.broadcast_l("sh-president-discards")
        self.chancellor_received_policies = drawn
        self.president_drawn_policies = None
        self.phase = Phase.CHAN_LEGISLATION
        chancellor = self._player_at_seat(self.current_chancellor_seat)
        self.broadcast_l("sh-chancellor-receives")
        self._send_policies_private(
            chancellor, self.chancellor_received_policies, "sh-your-policies-chancellor"
        )

    # ------------------------------------------------------------------
    # Task 12 — Chancellor enacts: track + win + power dispatch
    # ------------------------------------------------------------------

    def _action_enact_policy(self, player, action_id: str) -> None:
        if self.phase != Phase.CHAN_LEGISLATION:
            return
        if self.veto_proposed:
            return  # president must resolve veto first
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_chancellor_seat:
            return
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        if idx < 0 or idx >= len(self.chancellor_received_policies or []):
            return
        received = list(self.chancellor_received_policies or [])
        enacted = received.pop(idx)
        for leftover in received:
            self.discard.append(leftover)
        self.chancellor_received_policies = None
        if enacted == Policy.LIBERAL:
            self.liberal_policies += 1
        else:
            self.fascist_policies += 1
        self.broadcast_l(
            "sh-chancellor-enacts",
            policy=enacted.value,
            liberal=self.liberal_policies,
            fascist=self.fascist_policies,
        )
        self._ensure_deck_has(3)
        if self._check_track_win():
            return
        if enacted == Policy.FASCIST:
            bucket = track_bucket_for(self._active_player_count())
            slot = self.fascist_policies  # 1..5
            if 1 <= slot <= 5:
                power = FASCIST_TRACK_POWERS[bucket][slot - 1]
                if power != Power.NONE:
                    self.phase = Phase.POWER_RESOLUTION
                    self.pending_power = power
                    self.power_target_seat = None
                    self._announce_power_start(power)
                    return
        self._begin_nomination()

    def _active_player_count(self) -> int:
        return sum(1 for p in self.players if not p.is_spectator)

    def _announce_power_start(self, power: Power) -> None:
        key = {
            Power.INVESTIGATE: "sh-power-investigate",
            Power.SPECIAL_ELECTION: "sh-power-special-election",
            Power.POLICY_PEEK: "sh-power-policy-peek",
            Power.EXECUTION: "sh-power-execution",
        }[power]
        self.broadcast_l(key)
        if power == Power.POLICY_PEEK:
            pres = self._player_at_seat(self.current_president_seat)
            powers.resolve_policy_peek(self, pres)

    # ------------------------------------------------------------------
    # Task 13 — Investigate loyalty
    # ------------------------------------------------------------------

    def _action_investigate(self, player, action_id: str) -> None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.INVESTIGATE:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        try:
            target_seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        target = next(
            (
                p for p in self.players
                if isinstance(p, SecretHitlerPlayer)
                and p.seat == target_seat
                and p.is_alive
                and not p.has_been_investigated
                and p is not player
            ),
            None,
        )
        if target is None:
            return
        powers.resolve_investigate(self, player, target)
        self.pending_power = Power.NONE
        self.power_target_seat = None
        self._begin_nomination()

    # ------------------------------------------------------------------
    # Task 14 — Policy peek acknowledge
    # ------------------------------------------------------------------

    def _action_acknowledge_peek(self, player, action_id: str) -> None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.POLICY_PEEK:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        self.policy_peek_cards = None
        self.pending_power = Power.NONE
        self.power_target_seat = None
        self._begin_nomination()

    # ------------------------------------------------------------------
    # Task 15 — Execution
    # ------------------------------------------------------------------

    def _action_execute(self, player, action_id: str) -> None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.EXECUTION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        try:
            target_seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        target = next(
            (
                p for p in self.players
                if isinstance(p, SecretHitlerPlayer)
                and p.seat == target_seat
                and p.is_alive
                and p is not player
            ),
            None,
        )
        if target is None:
            return
        ended = powers.resolve_execution(self, player, target)
        self.pending_power = Power.NONE
        self.power_target_seat = None
        if ended:
            self._end_game(Party.LIBERAL, "sh-liberals-win-execution")
            return
        self._begin_nomination()

    # ------------------------------------------------------------------
    # Task 16 — Special election
    # ------------------------------------------------------------------

    def _action_choose_president(self, player, action_id: str) -> None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.SPECIAL_ELECTION:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        try:
            target_seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return
        target = next(
            (
                p for p in self.players
                if isinstance(p, SecretHitlerPlayer)
                and p.seat == target_seat
                and p.is_alive
                and p is not player
            ),
            None,
        )
        if target is None:
            return
        powers.resolve_special_election(self, player, target)
        self.pending_power = Power.NONE
        self.power_target_seat = None
        self._begin_nomination()
