"""Save/load roundtrip tests at every phase boundary."""

import random

import pytest

from server.games.secrethitler.game import SecretHitler, Phase
from server.games.secrethitler.cards import Policy, Power
from server.core.users.test_user import MockUser


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"p{i}"
        name = f"P{i}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name))
    return g


def _roundtrip(g: SecretHitler) -> SecretHitler:
    blob = g.to_json()
    clone = SecretHitler.from_json(blob)
    for p in clone.players:
        clone.attach_user(p.id, MockUser(p.name))
    clone.rebuild_runtime_state()
    return clone


def _assert_identical_state(a: SecretHitler, b: SecretHitler) -> None:
    assert a.to_json() == b.to_json()


def test_roundtrip_at_role_reveal():
    random.seed(301)
    g = _make_game(5)
    g.on_start()
    assert g.phase == Phase.ROLE_REVEAL
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    for p in clone.players:
        clone._action_acknowledge_role(p, "acknowledge_role")
    assert clone.phase == Phase.NOMINATION


def test_roundtrip_mid_nomination():
    random.seed(302)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    assert g.phase == Phase.NOMINATION
    assert g.nominee_chancellor_seat == nominee.seat
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    clone._action_call_vote(clone_pres, "call_vote")
    assert clone.phase == Phase.VOTING


def test_roundtrip_mid_voting():
    random.seed(303)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    g._action_call_vote(pres, "call_vote")
    alive = [p for p in g.players if p.is_alive][:2]
    for p in alive:
        g._action_vote_ja(p, "vote_ja")
    assert g.phase == Phase.VOTING
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    remaining = [
        p for p in clone.players
        if p.is_alive and p.id not in {a.id for a in alive}
    ]
    for p in remaining:
        clone._action_vote_ja(p, "vote_ja")
    assert clone.phase == Phase.PRES_LEGISLATION


def test_roundtrip_mid_pres_legislation():
    random.seed(304)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    assert g.phase == Phase.PRES_LEGISLATION
    assert len(g.president_drawn_policies) == 3
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    clone._action_discard_policy(clone_pres, "discard_0")
    assert clone.phase == Phase.CHAN_LEGISLATION
    assert len(clone.chancellor_received_policies) == 2


def test_roundtrip_mid_chan_legislation():
    random.seed(305)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    g._action_discard_policy(pres, "discard_0")
    assert g.phase == Phase.CHAN_LEGISLATION
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    assert clone.veto_proposed is False
    clone_chan = clone._player_at_seat(clone.current_chancellor_seat)
    clone._action_enact_policy(clone_chan, "enact_0")
    assert clone.phase in (Phase.NOMINATION, Phase.POWER_RESOLUTION, Phase.GAME_OVER)


def test_roundtrip_mid_power_resolution():
    random.seed(306)
    g = _make_game(9)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.fascist_policies = 0  # slot 1 triggers INVESTIGATE at 9p
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
    assert g.phase == Phase.POWER_RESOLUTION
    assert g.pending_power == Power.INVESTIGATE
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    assert clone.pending_power == Power.INVESTIGATE
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    target = next(
        p for p in clone.players
        if p is not clone_pres and p.is_alive and not p.has_been_investigated
    )
    clone._action_investigate(clone_pres, f"investigate_{target.seat}")
    assert clone.pending_power == Power.NONE


def test_roundtrip_mid_special_election():
    """Special-election rotation state must survive restore."""
    random.seed(307)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    # 7p: slot 3 triggers SPECIAL_ELECTION. Set fascist_policies=2 so the enact
    # brings it to 3 and triggers the power.
    g.fascist_policies = 2
    pres = g._player_at_seat(g.current_president_seat)
    chan = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{chan.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    g.president_drawn_policies = [Policy.FASCIST, Policy.FASCIST, Policy.LIBERAL]
    g._action_discard_policy(pres, "discard_2")
    clone_chan = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(clone_chan, "enact_0")
    assert g.phase == Phase.POWER_RESOLUTION
    assert g.pending_power == Power.SPECIAL_ELECTION
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    successor = next(
        p for p in clone.players
        if p is not clone_pres and p.is_alive
    )
    clone._action_choose_president(clone_pres, f"choose_president_{successor.seat}")
    assert clone.special_election_override is None, (
        "override should be consumed after choose_president"
    )
    # After the electee is named, rotation advances from the original seat.
    assert clone.current_president_seat == successor.seat
