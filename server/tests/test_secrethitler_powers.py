"""Tests for Secret Hitler executive powers."""

import random

import pytest

from server.games.secrethitler.game import SecretHitler, Phase
from server.games.secrethitler.cards import Policy, Role, Power, Party
from server.core.users.test_user import MockUser


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"player{i + 1}"
        name = f"P{i + 1}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name))
    return g


def _run_to_power(g: SecretHitler, enacted_fascist: int) -> None:
    """Run a full acknowledge → nominate → vote-ja → discard-fascist → enact-fascist sequence.

    Sets fascist_policies to enacted_fascist-1 beforehand so the one enactment
    brings the track to slot `enacted_fascist`.
    """
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.fascist_policies = enacted_fascist - 1
    pres = g._player_at_seat(g.current_president_seat)
    chan = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{chan.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    g.president_drawn_policies = [Policy.FASCIST, Policy.FASCIST, Policy.LIBERAL]
    g._action_discard_policy(pres, "discard_2")
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(chancellor, "enact_0")


def _spoken(g: SecretHitler, player) -> list[str]:
    u = g.get_user(player)
    return u.get_spoken_messages() if u else []


def test_investigate_loyalty_reveals_party_to_president_only():
    random.seed(101)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=1)
    assert g.phase == Phase.POWER_RESOLUTION
    assert g.pending_power == Power.INVESTIGATE
    pres = g._player_at_seat(g.current_president_seat)
    target = next(
        p for p in g.players
        if p is not pres and p.is_alive and not p.has_been_investigated
    )
    before = len(_spoken(g, pres))
    g._action_investigate(pres, f"investigate_{target.seat}")
    after_msgs = _spoken(g, pres)[before:]
    liberal_line = f"{target.name} is a Liberal."
    fascist_line = f"{target.name} is a Fascist."
    assert any(liberal_line in m or fascist_line in m for m in after_msgs), (
        f"President should see loyalty reveal; got {after_msgs!r}"
    )
    # No other player sees the loyalty reveal line for the target.
    for p in g.players:
        if p is pres:
            continue
        msgs = _spoken(g, p)
        assert not any(liberal_line in m or fascist_line in m for m in msgs), (
            f"{p.name} should not see the investigate reveal; got {msgs!r}"
        )
    assert target.has_been_investigated is True
    assert g.phase == Phase.NOMINATION


def test_investigate_loyalty_cannot_repeat_target():
    random.seed(102)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=1)
    pres = g._player_at_seat(g.current_president_seat)
    target = next(
        p for p in g.players
        if p is not pres and p.is_alive and not p.has_been_investigated
    )
    target.has_been_investigated = True
    other = next(
        p for p in g.players
        if p is not pres and p is not target and p.is_alive
    )
    g._action_investigate(pres, f"investigate_{target.seat}")
    assert g.phase == Phase.POWER_RESOLUTION
    g._action_investigate(pres, f"investigate_{other.seat}")
    assert other.has_been_investigated is True
    assert g.phase == Phase.NOMINATION


def test_investigate_loyalty_hitler_shows_as_fascist():
    random.seed(103)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=1)
    pres = g._player_at_seat(g.current_president_seat)
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    if hitler is pres:
        other = next(p for p in g.players if p is not pres)
        other.role, pres.role = pres.role, other.role
        hitler = other
    before = len(_spoken(g, pres))
    g._action_investigate(pres, f"investigate_{hitler.seat}")
    after_msgs = _spoken(g, pres)[before:]
    fascist_line = f"{hitler.name} is a Fascist."
    assert any(fascist_line in m for m in after_msgs), (
        f"Hitler should render as Fascist; got {after_msgs!r}"
    )


def test_policy_peek_reveals_top_three_only_to_president():
    random.seed(111)
    g = _make_game(5)
    _run_to_power(g, enacted_fascist=3)
    assert g.pending_power == Power.POLICY_PEEK
    pres = g._player_at_seat(g.current_president_seat)
    # Override the top of the deck so we know what the president should see.
    g.deck[:3] = [Policy.FASCIST, Policy.LIBERAL, Policy.LIBERAL]
    # _announce_power_start for POLICY_PEEK already delivered the peek to the president
    # (the implementation below emits the peek eagerly). Invoke re-emission test by
    # sending a fresh peek immediately before ack:
    before = len(_spoken(g, pres))
    g._action_acknowledge_peek(pres, "acknowledge_peek")
    # Deck unchanged.
    assert g.deck[:3] == [Policy.FASCIST, Policy.LIBERAL, Policy.LIBERAL]
    # President must have received a peek line before the ack transitioned us away.
    # Easiest check: whole spoken history contains the peek text (emitted on power start).
    full = _spoken(g, pres)
    peek_prefix = "Top three policies:"
    assert any(peek_prefix in m for m in full), (
        f"President should see peek contents in history; got {full!r}"
    )
    for p in g.players:
        if p is pres:
            continue
        msgs = _spoken(g, p)
        assert not any(peek_prefix in m for m in msgs), (
            f"{p.name} should not see the peek; got {msgs!r}"
        )
    assert g.phase == Phase.NOMINATION


def test_execution_kills_target_and_advances_to_nomination():
    random.seed(100)  # seed 121 hits Hitler-elected; 100 avoids it
    g = _make_game(7)
    _run_to_power(g, enacted_fascist=4)
    assert g.pending_power == Power.EXECUTION
    pres = g._player_at_seat(g.current_president_seat)
    target = next(
        p for p in g.players
        if p is not pres and p.is_alive and p.role == Role.LIBERAL
    )
    g._action_execute(pres, f"execute_{target.seat}")
    assert target.is_alive is False
    assert g.phase == Phase.NOMINATION


def test_execution_of_hitler_liberals_win():
    random.seed(122)
    g = _make_game(7)
    _run_to_power(g, enacted_fascist=4)
    pres = g._player_at_seat(g.current_president_seat)
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    if hitler is pres:
        other = next(p for p in g.players if p is not pres)
        other.role, pres.role = pres.role, other.role
        hitler = other
    g._action_execute(pres, f"execute_{hitler.seat}")
    assert hitler.is_alive is False
    assert g.phase == Phase.GAME_OVER
    assert g.winner == Party.LIBERAL
    assert g.win_reason == "sh-liberals-win-execution"


def test_executed_player_cannot_vote_or_nominate():
    random.seed(123)
    g = _make_game(7)
    _run_to_power(g, enacted_fascist=4)
    pres = g._player_at_seat(g.current_president_seat)
    target = next(
        p for p in g.players
        if p is not pres and p.is_alive and p.role == Role.LIBERAL
    )
    g._action_execute(pres, f"execute_{target.seat}")
    assert target.seat not in g._eligible_chancellor_seats()
    pres2 = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p.is_alive and p is not pres2)
    g._action_nominate(pres2, f"nominate_{nominee.seat}")
    g._action_call_vote(pres2, "call_vote")
    alive = [p for p in g.players if p.is_alive]
    for p in alive:
        g._action_vote_ja(p, "vote_ja")
    assert g.phase != Phase.VOTING


def test_special_election_sets_override():
    random.seed(131)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=3)
    assert g.pending_power == Power.SPECIAL_ELECTION
    pres = g._player_at_seat(g.current_president_seat)
    target = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_choose_president(pres, f"choose_president_{target.seat}")
    assert g.phase == Phase.NOMINATION
    assert g.current_president_seat == target.seat


def test_special_election_rotation_resumes_from_original():
    random.seed(100)  # seed 132 had eligible-chancellor conflicts; 100 avoids it
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=3)
    original_pres_seat = g.current_president_seat
    pres = g._player_at_seat(original_pres_seat)
    target = next(
        p for p in g.players
        if p.is_alive and p.seat != (original_pres_seat + 1) % 9 and p is not pres
    )
    g._action_choose_president(pres, f"choose_president_{target.seat}")
    electee = g._player_at_seat(g.current_president_seat)
    # Pick an eligible chancellor, not just any alive player
    eligible = g._eligible_chancellor_seats()
    nominee = g._player_at_seat(eligible[0])
    g._action_nominate(electee, f"nominate_{nominee.seat}")
    g._action_call_vote(electee, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_nein(p, "vote_nein")
    alive_seats = sorted(p.seat for p in g.players if p.is_alive)
    idx = alive_seats.index(original_pres_seat)
    expected_next = alive_seats[(idx + 1) % len(alive_seats)]
    assert g.current_president_seat == expected_next


def _run_to_chan_legislation_with_fascist_policies(g: SecretHitler, f_count: int) -> None:
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.fascist_policies = f_count
    pres = g._player_at_seat(g.current_president_seat)
    chan = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{chan.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    g.president_drawn_policies = [Policy.FASCIST, Policy.FASCIST, Policy.FASCIST]
    g._action_discard_policy(pres, "discard_2")


def test_veto_locked_before_5_fascist():
    random.seed(141)
    g = _make_game(5)
    _run_to_chan_legislation_with_fascist_policies(g, 4)
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_propose_veto(chancellor, "propose_veto")
    assert g.veto_proposed is False


def test_veto_unlocked_at_5_fascist():
    random.seed(142)
    g = _make_game(5)
    _run_to_chan_legislation_with_fascist_policies(g, 5)
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_propose_veto(chancellor, "propose_veto")
    assert g.veto_proposed is True


def test_veto_accept_discards_and_advances_tracker():
    random.seed(143)
    g = _make_game(5)
    _run_to_chan_legislation_with_fascist_policies(g, 5)
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_propose_veto(chancellor, "propose_veto")
    pres = g._player_at_seat(g.current_president_seat)
    discard_before = len(g.discard)
    g._action_veto_accept(pres, "veto_accept")
    assert g.veto_proposed is False
    assert g.chancellor_received_policies is None
    assert len(g.discard) == discard_before + 2
    assert g.election_tracker == 1
    assert g.phase == Phase.NOMINATION


def test_veto_reject_reopens_chancellor_menu_no_reveto():
    random.seed(106)  # seed 144 hits Hitler-elected; 106 avoids it
    g = _make_game(5)
    _run_to_chan_legislation_with_fascist_policies(g, 5)
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_propose_veto(chancellor, "propose_veto")
    pres = g._player_at_seat(g.current_president_seat)
    g._action_veto_reject(pres, "veto_reject")
    assert g.veto_proposed is False
    g._action_propose_veto(chancellor, "propose_veto")
    assert g.veto_proposed is False
    g._action_enact_policy(chancellor, "enact_0")
    assert g.phase in (Phase.POWER_RESOLUTION, Phase.NOMINATION, Phase.GAME_OVER)
