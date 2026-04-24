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
