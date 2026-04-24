"""Secret Hitler game implementation."""

from dataclasses import dataclass, field
from enum import Enum
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState
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

    def _on_phase_transition(self) -> None:
        """Reset the on-turn player's menu focus to position 1.

        Called after every `self.phase = ...` assignment. Without this,
        persistent items like `view_tracks` shift position as phase-specific
        actions appear and disappear, stranding focus at the bottom.
        """
        target_seat: int | None = None
        if self.phase == Phase.NOMINATION:
            target_seat = self.current_president_seat
        elif self.phase == Phase.PRES_LEGISLATION:
            target_seat = self.current_president_seat
        elif self.phase == Phase.CHAN_LEGISLATION:
            target_seat = self.current_chancellor_seat
        elif self.phase == Phase.POWER_RESOLUTION:
            target_seat = self.current_president_seat
        if target_seat is None:
            return
        try:
            player = self._player_at_seat(target_seat)
        except KeyError:
            return
        self.rebuild_player_menu(player, position=1)

    def _begin_nomination(self) -> None:
        self.phase = Phase.NOMINATION
        self.current_president_seat = self._next_president_seat()
        self.current_chancellor_seat = None
        self.nominee_chancellor_seat = None
        self.votes = {}
        self.vote_call_deadline_tick = None
        pres = self._player_at_seat(self.current_president_seat)
        self.broadcast_l("sh-president-is", player=pres.name)
        self._on_phase_transition()

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
        self._on_phase_transition()
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
        self._on_phase_transition()
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
                    self._on_phase_transition()
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

    # ------------------------------------------------------------------
    # Task 17 — Veto
    # ------------------------------------------------------------------

    def _action_propose_veto(self, player, action_id: str) -> None:
        if self.phase != Phase.CHAN_LEGISLATION:
            return
        if self.fascist_policies < 5:
            return
        if self.veto_blocked_this_turn:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_chancellor_seat:
            return
        self.veto_proposed = True
        self.broadcast_l("sh-chancellor-proposes-veto")

    def _action_veto_accept(self, player, action_id: str) -> None:
        if self.phase != Phase.CHAN_LEGISLATION or not self.veto_proposed:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        for p in self.chancellor_received_policies or []:
            self.discard.append(p)
        self.chancellor_received_policies = None
        self.veto_proposed = False
        self.broadcast_l("sh-president-accepts-veto")
        self.election_tracker += 1
        self.broadcast_l("sh-tracker-advances", count=self.election_tracker)
        if self.election_tracker >= 3:
            self._chaos_enact()
            return
        self._begin_nomination()

    def _action_veto_reject(self, player, action_id: str) -> None:
        if self.phase != Phase.CHAN_LEGISLATION or not self.veto_proposed:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        if player.seat != self.current_president_seat:
            return
        self.veto_proposed = False
        self.veto_blocked_this_turn = True
        self.broadcast_l("sh-president-rejects-veto")

    # ------------------------------------------------------------------
    # Task 22 — Action sets, keybinds, standard menu items
    # ------------------------------------------------------------------

    def _host_locale(self) -> str:
        """Return the host's locale, falling back to 'en'."""
        if hasattr(self, "host_username") and self.host_username:
            player = self.get_player_by_name(self.host_username)
            if player:
                user = self.get_user(player)
                if user:
                    return user.locale
        return "en"

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()
        locale = self._host_locale()

        self.define_keybind(
            "v",
            Localization.get(locale, "sh-vote-ja"),
            ["vote_ja", "vote_nein"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "n",
            Localization.get(locale, "sh-nominate"),
            [f"nominate_{i}" for i in range(10)],
            state=KeybindState.ACTIVE,
            requires_focus=True,
        )
        self.define_keybind(
            "r",
            Localization.get(locale, "sh-view-my-role"),
            ["view_my_role"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "s",
            Localization.get(locale, "sh-view-tracks"),
            ["check_scores"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+s",
            Localization.get(locale, "sh-view-government"),
            ["check_scores_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # -- is_playing helper -------------------------------------------------

    def _is_playing(self) -> bool:
        return self.status == "playing" and self.phase != Phase.GAME_OVER

    # -- Acknowledge role ---------------------------------------------------

    def _is_acknowledge_role_hidden(self, player: Player) -> Visibility:
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if self.phase != Phase.ROLE_REVEAL:
            return Visibility.HIDDEN
        if player.seat in self.role_ack_seats:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_acknowledge_role_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.ROLE_REVEAL:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat in self.role_ack_seats:
            return "action-not-available"
        return None

    # -- Nominate family ---------------------------------------------------

    def _is_nominate_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.phase != Phase.NOMINATION:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        eligible = self._eligible_chancellor_seats()
        if seat not in eligible:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_nominate_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.phase != Phase.NOMINATION:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        eligible = self._eligible_chancellor_seats()
        if seat not in eligible:
            return "action-not-available"
        return None

    def _get_nominate_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-nominate", player="?")
        try:
            target = self._player_at_seat(seat)
        except KeyError:
            return Localization.get(locale, "sh-nominate", player="?")
        return Localization.get(locale, "sh-nominate", player=target.name)

    # -- Call vote / cancel nomination -------------------------------------

    def _is_call_vote_hidden(self, player: Player) -> Visibility:
        if self.phase != Phase.NOMINATION:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if self.nominee_chancellor_seat is None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_call_vote_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.NOMINATION:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if self.nominee_chancellor_seat is None:
            return "action-not-available"
        return None

    def _is_cancel_nomination_hidden(self, player: Player) -> Visibility:
        return self._is_call_vote_hidden(player)

    def _is_cancel_nomination_enabled(self, player: Player) -> str | None:
        return self._is_call_vote_enabled(player)

    # -- Vote ja / nein ----------------------------------------------------

    def _is_vote_hidden(self, player: Player) -> Visibility:
        if self.phase != Phase.VOTING:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if not player.is_alive:
            return Visibility.HIDDEN
        if player.seat in self.votes:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_vote_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.VOTING:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if not player.is_alive:
            return "action-not-available"
        if player.seat in self.votes:
            return "action-not-available"
        return None

    # -- Discard policy family (president) ---------------------------------

    def _is_discard_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.phase != Phase.PRES_LEGISLATION:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        if idx < 0 or idx >= len(self.president_drawn_policies or []):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_discard_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.phase != Phase.PRES_LEGISLATION:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        if idx < 0 or idx >= len(self.president_drawn_policies or []):
            return "action-not-available"
        return None

    def _get_discard_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-discard-policy", policy="?")
        policies = self.president_drawn_policies or []
        if idx < 0 or idx >= len(policies):
            return Localization.get(locale, "sh-discard-policy", policy="?")
        policy_key = "sh-policy-liberal" if policies[idx] == Policy.LIBERAL else "sh-policy-fascist"
        policy_name = Localization.get(locale, policy_key)
        return Localization.get(locale, "sh-discard-policy", policy=policy_name)

    # -- Enact policy family (chancellor) ----------------------------------

    def _is_enact_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.phase != Phase.CHAN_LEGISLATION:
            return Visibility.HIDDEN
        if self.veto_proposed:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_chancellor_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        if idx < 0 or idx >= len(self.chancellor_received_policies or []):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_enact_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.phase != Phase.CHAN_LEGISLATION:
            return "action-not-available"
        if self.veto_proposed:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_chancellor_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        if idx < 0 or idx >= len(self.chancellor_received_policies or []):
            return "action-not-available"
        return None

    def _get_enact_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            idx = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-enact-policy", policy="?")
        policies = self.chancellor_received_policies or []
        if idx < 0 or idx >= len(policies):
            return Localization.get(locale, "sh-enact-policy", policy="?")
        policy_key = "sh-policy-liberal" if policies[idx] == Policy.LIBERAL else "sh-policy-fascist"
        policy_name = Localization.get(locale, policy_key)
        return Localization.get(locale, "sh-enact-policy", policy=policy_name)

    # -- Propose veto ------------------------------------------------------

    def _is_propose_veto_hidden(self, player: Player) -> Visibility:
        if self.phase != Phase.CHAN_LEGISLATION:
            return Visibility.HIDDEN
        if self.fascist_policies < 5:
            return Visibility.HIDDEN
        if self.veto_proposed:
            return Visibility.HIDDEN
        if self.veto_blocked_this_turn:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_chancellor_seat:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_propose_veto_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.CHAN_LEGISLATION:
            return "action-not-available"
        if self.fascist_policies < 5:
            return "action-not-available"
        if self.veto_proposed:
            return "action-not-available"
        if self.veto_blocked_this_turn:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_chancellor_seat:
            return "action-not-available"
        return None

    # -- Veto accept / reject (president) ----------------------------------

    def _is_veto_response_hidden(self, player: Player) -> Visibility:
        if self.phase != Phase.CHAN_LEGISLATION:
            return Visibility.HIDDEN
        if not self.veto_proposed:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_veto_response_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.CHAN_LEGISLATION:
            return "action-not-available"
        if not self.veto_proposed:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        return None

    # -- Investigate family ------------------------------------------------

    def _is_investigate_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.INVESTIGATE:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        target_seats = {p.seat for p in self._investigate_targets()}
        if seat not in target_seats:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_investigate_enabled(
        self, player: Player, action_id: str | None = None
    ) -> str | None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.INVESTIGATE:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        target_seats = {p.seat for p in self._investigate_targets()}
        if seat not in target_seats:
            return "action-not-available"
        return None

    def _get_investigate_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-investigate-target", player="?")
        try:
            target = self._player_at_seat(seat)
        except KeyError:
            return Localization.get(locale, "sh-investigate-target", player="?")
        return Localization.get(locale, "sh-investigate-target", player=target.name)

    def _investigate_targets(self) -> list[SecretHitlerPlayer]:
        pres_seat = self.current_president_seat
        return [
            p for p in self.players
            if isinstance(p, SecretHitlerPlayer)
            and p.is_alive
            and not p.has_been_investigated
            and p.seat != pres_seat
        ]

    # -- Choose president family (special election) ------------------------

    def _is_choose_president_hidden(
        self, player: Player, action_id: str | None = None
    ) -> Visibility:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.SPECIAL_ELECTION:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        target_seats = {p.seat for p in self._special_election_targets()}
        if seat not in target_seats:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_choose_president_enabled(
        self, player: Player, action_id: str | None = None
    ) -> str | None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.SPECIAL_ELECTION:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        target_seats = {p.seat for p in self._special_election_targets()}
        if seat not in target_seats:
            return "action-not-available"
        return None

    def _get_choose_president_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-choose-president-target", player="?")
        try:
            target = self._player_at_seat(seat)
        except KeyError:
            return Localization.get(locale, "sh-choose-president-target", player="?")
        return Localization.get(locale, "sh-choose-president-target", player=target.name)

    def _special_election_targets(self) -> list[SecretHitlerPlayer]:
        pres_seat = self.current_president_seat
        return [
            p for p in self.players
            if isinstance(p, SecretHitlerPlayer) and p.is_alive and p.seat != pres_seat
        ]

    # -- Execute family ----------------------------------------------------

    def _is_execute_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.EXECUTION:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        if action_id is None:
            return Visibility.VISIBLE
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Visibility.HIDDEN
        target_seats = {p.seat for p in self._execution_targets()}
        if seat not in target_seats:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_execute_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.EXECUTION:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        if action_id is None:
            return None
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return "action-not-available"
        target_seats = {p.seat for p in self._execution_targets()}
        if seat not in target_seats:
            return "action-not-available"
        return None

    def _get_execute_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        try:
            seat = int(action_id.rsplit("_", 1)[-1])
        except ValueError:
            return Localization.get(locale, "sh-execute-target", player="?")
        try:
            target = self._player_at_seat(seat)
        except KeyError:
            return Localization.get(locale, "sh-execute-target", player="?")
        return Localization.get(locale, "sh-execute-target", player=target.name)

    def _execution_targets(self) -> list[SecretHitlerPlayer]:
        pres_seat = self.current_president_seat
        return [
            p for p in self.players
            if isinstance(p, SecretHitlerPlayer) and p.is_alive and p.seat != pres_seat
        ]

    # -- Acknowledge peek --------------------------------------------------

    def _is_acknowledge_peek_hidden(self, player: Player) -> Visibility:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.POLICY_PEEK:
            return Visibility.HIDDEN
        if not isinstance(player, SecretHitlerPlayer):
            return Visibility.HIDDEN
        if player.seat != self.current_president_seat:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_acknowledge_peek_enabled(self, player: Player) -> str | None:
        if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.POLICY_PEEK:
            return "action-not-available"
        if not isinstance(player, SecretHitlerPlayer):
            return "action-not-available"
        if player.seat != self.current_president_seat:
            return "action-not-available"
        return None

    # ------------------------------------------------------------------
    # create_turn_action_set
    # ------------------------------------------------------------------

    def create_turn_action_set(self, player: SecretHitlerPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        # Acknowledge role
        action_set.add(Action(
            id="acknowledge_role",
            label=Localization.get(locale, "sh-acknowledge-role"),
            handler="_action_acknowledge_role",
            is_enabled="_is_acknowledge_role_enabled",
            is_hidden="_is_acknowledge_role_hidden",
        ))

        # Nominate 0..9
        for i in range(10):
            action_set.add(Action(
                id=f"nominate_{i}",
                label=Localization.get(locale, "sh-nominate", player="?"),
                handler="_action_nominate",
                is_enabled="_is_nominate_enabled",
                is_hidden="_is_nominate_hidden",
                get_label="_get_nominate_label",
                show_in_actions_menu=False,
            ))

        # Call vote / cancel nomination
        action_set.add(Action(
            id="call_vote",
            label=Localization.get(locale, "sh-call-vote"),
            handler="_action_call_vote",
            is_enabled="_is_call_vote_enabled",
            is_hidden="_is_call_vote_hidden",
        ))
        action_set.add(Action(
            id="cancel_nomination",
            label=Localization.get(locale, "sh-cancel-nomination"),
            handler="_action_cancel_nomination",
            is_enabled="_is_cancel_nomination_enabled",
            is_hidden="_is_cancel_nomination_hidden",
        ))

        # Vote ja / nein
        action_set.add(Action(
            id="vote_ja",
            label=Localization.get(locale, "sh-vote-ja"),
            handler="_action_vote_ja",
            is_enabled="_is_vote_enabled",
            is_hidden="_is_vote_hidden",
        ))
        action_set.add(Action(
            id="vote_nein",
            label=Localization.get(locale, "sh-vote-nein"),
            handler="_action_vote_nein",
            is_enabled="_is_vote_enabled",
            is_hidden="_is_vote_hidden",
        ))

        # Discard policy 0..2 (president legislation)
        for i in range(3):
            action_set.add(Action(
                id=f"discard_{i}",
                label=Localization.get(locale, "sh-discard-policy", policy="?"),
                handler="_action_discard_policy",
                is_enabled="_is_discard_enabled",
                is_hidden="_is_discard_hidden",
                get_label="_get_discard_label",
                show_in_actions_menu=False,
            ))

        # Enact policy 0..1 (chancellor legislation)
        for i in range(2):
            action_set.add(Action(
                id=f"enact_{i}",
                label=Localization.get(locale, "sh-enact-policy", policy="?"),
                handler="_action_enact_policy",
                is_enabled="_is_enact_enabled",
                is_hidden="_is_enact_hidden",
                get_label="_get_enact_label",
                show_in_actions_menu=False,
            ))

        # Propose veto
        action_set.add(Action(
            id="propose_veto",
            label=Localization.get(locale, "sh-propose-veto"),
            handler="_action_propose_veto",
            is_enabled="_is_propose_veto_enabled",
            is_hidden="_is_propose_veto_hidden",
        ))

        # Veto accept / reject (president)
        action_set.add(Action(
            id="veto_accept",
            label=Localization.get(locale, "sh-veto-accept"),
            handler="_action_veto_accept",
            is_enabled="_is_veto_response_enabled",
            is_hidden="_is_veto_response_hidden",
        ))
        action_set.add(Action(
            id="veto_reject",
            label=Localization.get(locale, "sh-veto-reject"),
            handler="_action_veto_reject",
            is_enabled="_is_veto_response_enabled",
            is_hidden="_is_veto_response_hidden",
        ))

        # Investigate 0..9
        for i in range(10):
            action_set.add(Action(
                id=f"investigate_{i}",
                label=Localization.get(locale, "sh-investigate-target", player="?"),
                handler="_action_investigate",
                is_enabled="_is_investigate_enabled",
                is_hidden="_is_investigate_hidden",
                get_label="_get_investigate_label",
                show_in_actions_menu=False,
            ))

        # Choose president 0..9 (special election)
        for i in range(10):
            action_set.add(Action(
                id=f"choose_president_{i}",
                label=Localization.get(locale, "sh-choose-president-target", player="?"),
                handler="_action_choose_president",
                is_enabled="_is_choose_president_enabled",
                is_hidden="_is_choose_president_hidden",
                get_label="_get_choose_president_label",
                show_in_actions_menu=False,
            ))

        # Execute 0..9
        for i in range(10):
            action_set.add(Action(
                id=f"execute_{i}",
                label=Localization.get(locale, "sh-execute-target", player="?"),
                handler="_action_execute",
                is_enabled="_is_execute_enabled",
                is_hidden="_is_execute_hidden",
                get_label="_get_execute_label",
                show_in_actions_menu=False,
            ))

        # Acknowledge peek
        action_set.add(Action(
            id="acknowledge_peek",
            label=Localization.get(locale, "sh-acknowledge-peek"),
            handler="_action_acknowledge_peek",
            is_enabled="_is_acknowledge_peek_enabled",
            is_hidden="_is_acknowledge_peek_hidden",
        ))

        return action_set

    # ------------------------------------------------------------------
    # Standard action set — persistent info actions
    # ------------------------------------------------------------------

    def _is_sh_info_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        return None

    def _is_sh_info_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE

    def _is_view_my_role_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_view_my_role_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def create_standard_action_set(self, player: Player) -> ActionSet:
        """Create the standard action set, adding Secret Hitler persistent info actions."""
        action_set = super().create_standard_action_set(player)

        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(Action(
            id="view_tracks",
            label=Localization.get(locale, "sh-view-tracks"),
            handler="_action_view_tracks",
            is_enabled="_is_sh_info_enabled",
            is_hidden="_is_sh_info_hidden",
            show_in_actions_menu=True,
            include_spectators=True,
        ))
        action_set.add(Action(
            id="view_government",
            label=Localization.get(locale, "sh-view-government"),
            handler="_action_view_government",
            is_enabled="_is_sh_info_enabled",
            is_hidden="_is_sh_info_hidden",
            show_in_actions_menu=True,
            include_spectators=True,
        ))
        action_set.add(Action(
            id="view_players",
            label=Localization.get(locale, "sh-view-players"),
            handler="_action_view_players",
            is_enabled="_is_sh_info_enabled",
            is_hidden="_is_sh_info_hidden",
            show_in_actions_menu=True,
            include_spectators=True,
        ))
        action_set.add(Action(
            id="view_my_role",
            label=Localization.get(locale, "sh-view-my-role"),
            handler="_action_view_my_role",
            is_enabled="_is_view_my_role_enabled",
            is_hidden="_is_view_my_role_hidden",
            show_in_actions_menu=True,
        ))
        action_set.add(Action(
            id="view_election_tracker",
            label=Localization.get(locale, "sh-view-election-tracker"),
            handler="_action_view_election_tracker",
            is_enabled="_is_sh_info_enabled",
            is_hidden="_is_sh_info_hidden",
            show_in_actions_menu=True,
            include_spectators=True,
        ))

        return action_set

    # ------------------------------------------------------------------
    # _action_check_scores / _action_check_scores_detailed overrides
    # ------------------------------------------------------------------

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        """Brief status: liberal and fascist track counts."""
        user = self.get_user(player)
        if user:
            user.speak_l(
                "sh-view-tracks-content",
                "table",
                liberal=self.liberal_policies,
                fascist=self.fascist_policies,
            )

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        return None

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        """Detailed status: tracks + current government + election tracker."""
        user = self.get_user(player)
        if not user:
            return
        pres_name = "—"
        if self.current_president_seat is not None:
            try:
                pres_name = self._player_at_seat(self.current_president_seat).name
            except KeyError:
                pass
        chan_name = "—"
        if self.current_chancellor_seat is not None:
            try:
                chan_name = self._player_at_seat(self.current_chancellor_seat).name
            except KeyError:
                pass
        lastpres = "—"
        if self.last_elected_president_seat is not None:
            try:
                lastpres = self._player_at_seat(self.last_elected_president_seat).name
            except KeyError:
                pass
        lastchan = "—"
        if self.last_elected_chancellor_seat is not None:
            try:
                lastchan = self._player_at_seat(self.last_elected_chancellor_seat).name
            except KeyError:
                pass
        lines = [
            Localization.get(
                user.locale,
                "sh-view-tracks-content",
                liberal=self.liberal_policies,
                fascist=self.fascist_policies,
            ),
            Localization.get(
                user.locale,
                "sh-view-government-content",
                president=pres_name,
                chancellor=chan_name,
                lastpres=lastpres,
                lastchan=lastchan,
            ),
            Localization.get(
                user.locale,
                "sh-tracker-advances",
                count=self.election_tracker,
            ),
        ]
        self.status_box(player, lines)

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    # ------------------------------------------------------------------
    # Persistent view handlers
    # ------------------------------------------------------------------

    def _action_view_tracks(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(
                "sh-view-tracks-content",
                "table",
                liberal=self.liberal_policies,
                fascist=self.fascist_policies,
            )

    def _action_view_government(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        pres_name = "—"
        if self.current_president_seat is not None:
            try:
                pres_name = self._player_at_seat(self.current_president_seat).name
            except KeyError:
                pass
        chan_name = "—"
        if self.current_chancellor_seat is not None:
            try:
                chan_name = self._player_at_seat(self.current_chancellor_seat).name
            except KeyError:
                pass
        lastpres = "—"
        if self.last_elected_president_seat is not None:
            try:
                lastpres = self._player_at_seat(self.last_elected_president_seat).name
            except KeyError:
                pass
        lastchan = "—"
        if self.last_elected_chancellor_seat is not None:
            try:
                lastchan = self._player_at_seat(self.last_elected_chancellor_seat).name
            except KeyError:
                pass
        user.speak_l(
            "sh-view-government-content",
            "table",
            president=pres_name,
            chancellor=chan_name,
            lastpres=lastpres,
            lastchan=lastchan,
        )

    def _action_view_players(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.players if not p.is_spectator]
        parts = []
        for p in active:
            if isinstance(p, SecretHitlerPlayer):
                status = "alive" if p.is_alive else "dead"
                parts.append(f"{p.name} ({status})")
            else:
                parts.append(p.name)
        user.speak(", ".join(parts) if parts else "—", buffer="table")

    def _action_view_my_role(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if not isinstance(player, SecretHitlerPlayer):
            return
        key = {
            Role.LIBERAL: "sh-you-are-liberal",
            Role.FASCIST: "sh-you-are-fascist",
            Role.HITLER: "sh-you-are-hitler",
        }.get(player.role, "sh-you-are-liberal")
        user.speak_l(key, "table")

    def _action_view_election_tracker(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l("sh-tracker-advances", "table", count=self.election_tracker)
