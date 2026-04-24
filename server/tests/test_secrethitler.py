"""Tests for Secret Hitler game."""

import pytest
from server.games.registry import GameRegistry
from server.games.secrethitler.cards import (
    Policy,
    Role,
    Party,
    Power,
    ROLE_COUNTS,
    FASCIST_TRACK_POWERS,
    build_policy_deck,
)


def test_game_registered():
    """Secret Hitler must be registered under type 'secrethitler'."""
    cls = GameRegistry.get("secrethitler")
    assert cls is not None
    assert cls.get_type() == "secrethitler"
    assert cls.get_name() == "Secret Hitler"


def test_player_count_bounds():
    cls = GameRegistry.get("secrethitler")
    assert cls.get_min_players() == 5
    assert cls.get_max_players() == 10


def test_role_counts_by_player_count():
    assert ROLE_COUNTS[5] == (3, 1, 1)
    assert ROLE_COUNTS[6] == (4, 1, 1)
    assert ROLE_COUNTS[7] == (4, 2, 1)
    assert ROLE_COUNTS[8] == (5, 2, 1)
    assert ROLE_COUNTS[9] == (5, 3, 1)
    assert ROLE_COUNTS[10] == (6, 3, 1)


def test_fascist_track_powers_5_6():
    track = FASCIST_TRACK_POWERS["5-6"]
    assert track == (
        Power.NONE,
        Power.NONE,
        Power.POLICY_PEEK,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_fascist_track_powers_7_8():
    track = FASCIST_TRACK_POWERS["7-8"]
    assert track == (
        Power.NONE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_fascist_track_powers_9_10():
    track = FASCIST_TRACK_POWERS["9-10"]
    assert track == (
        Power.INVESTIGATE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    )


def test_policy_deck_composition():
    deck = build_policy_deck()
    assert len(deck) == 17
    assert deck.count(Policy.LIBERAL) == 6
    assert deck.count(Policy.FASCIST) == 11


def test_party_of_role():
    assert Role.LIBERAL.party is Party.LIBERAL
    assert Role.FASCIST.party is Party.FASCIST
    assert Role.HITLER.party is Party.FASCIST


from server.games.secrethitler.player import (
    SecretHitlerPlayer,
    SecretHitlerOptions,
)
from server.games.secrethitler.game import SecretHitler, Phase


def test_player_defaults():
    p = SecretHitlerPlayer(id="x", name="Alice")
    assert p.seat == 0
    assert p.role == Role.LIBERAL
    assert p.is_alive is True
    assert p.has_been_investigated is False
    assert p.connected is True


def test_options_defaults():
    o = SecretHitlerOptions()
    assert o.president_vote_timeout_seconds == 180
    assert o.bot_think_seconds == 2


def test_game_creates_typed_players_and_options():
    g = SecretHitler()
    p = g.create_player("player1", "Alice")
    assert isinstance(p, SecretHitlerPlayer)
    assert isinstance(g.options, SecretHitlerOptions)


from pathlib import Path


def test_locale_file_exists_and_has_game_name_key():
    locale_path = Path(__file__).parent.parent / "locales" / "en" / "secrethitler.ftl"
    assert locale_path.exists(), f"Missing locale file: {locale_path}"
    text = locale_path.read_text(encoding="utf-8")
    assert "game-name-secrethitler = Secret Hitler" in text
    for key in (
        "sh-you-are-liberal",
        "sh-you-are-fascist",
        "sh-you-are-hitler",
        "sh-fascist-teammates",
    ):
        assert key in text, f"Missing key {key} in locale file"


from server.core.users.test_user import MockUser


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"player{i + 1}"
        name = f"P{i + 1}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name))
    return g


@pytest.mark.parametrize("n", [5, 6, 7, 8, 9, 10])
def test_on_start_deals_correct_roles(n):
    import random
    random.seed(42)
    g = _make_game(n)
    g.on_start()

    roles = [p.role for p in g.players]
    liberals = roles.count(Role.LIBERAL)
    fascists = roles.count(Role.FASCIST)
    hitlers = roles.count(Role.HITLER)

    from server.games.secrethitler.cards import ROLE_COUNTS
    expected = ROLE_COUNTS[n]
    assert (liberals, fascists, hitlers) == expected


def test_on_start_assigns_stable_seats():
    g = _make_game(5)
    g.on_start()
    seats = sorted(p.seat for p in g.players)
    assert seats == [0, 1, 2, 3, 4]


def test_on_start_builds_shuffled_deck():
    import random
    random.seed(0)
    g = _make_game(5)
    g.on_start()
    from server.games.secrethitler.cards import Policy
    assert len(g.deck) == 17
    assert g.deck.count(Policy.LIBERAL) == 6
    assert g.deck.count(Policy.FASCIST) == 11
    assert g.discard == []
    assert g.liberal_policies == 0
    assert g.fascist_policies == 0
    assert g.election_tracker == 0


def test_on_start_refuses_bad_player_count():
    g = SecretHitler()
    for i in range(4):
        pid = f"p{i}"
        g.players.append(g.create_player(pid, f"P{i}"))
        g.attach_user(pid, MockUser(f"P{i}"))
    errors = g.prestart_validate()
    # prestart_validate returns list of locale keys OR list of (key, kwargs) tuples.
    assert any(
        (isinstance(e, str) and e == "sh-error-need-5-players")
        or (isinstance(e, tuple) and e[0] == "sh-error-need-5-players")
        for e in errors
    )


def _spoken(g: SecretHitler, player_name: str) -> list[str]:
    """Return rendered speech text delivered to the given player."""
    p = g.get_player_by_name(player_name)
    u = g.get_user(p)
    return u.get_spoken_messages() if u else []


@pytest.mark.parametrize("n", [5, 6])
def test_role_reveal_hitler_knows_fascists_at_5_6(n):
    import random
    random.seed(7)
    g = _make_game(n)
    g.on_start()
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    msgs = _spoken(g, hitler.name)
    # Hitler gets both "You are Hitler." and the teammates line.
    assert any("You are Hitler" in m for m in msgs)
    assert any(m.startswith("The Fascists are:") for m in msgs), (
        f"Hitler at n={n} should see teammates; got {msgs!r}"
    )


@pytest.mark.parametrize("n", [7, 8, 9, 10])
def test_role_reveal_hitler_blind_at_7_plus(n):
    import random
    random.seed(11)
    g = _make_game(n)
    g.on_start()
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    msgs = _spoken(g, hitler.name)
    assert any("You are Hitler" in m for m in msgs)
    # No teammates disclosure for Hitler at 7+.
    assert not any(m.startswith("The Fascists are:") for m in msgs), (
        f"Hitler at n={n} must not see teammates; got {msgs!r}"
    )


def test_fascists_always_see_teammates():
    import random
    random.seed(5)
    g = _make_game(7)
    g.on_start()
    for f in [p for p in g.players if p.role == Role.FASCIST]:
        msgs = _spoken(g, f.name)
        assert any("You are a Fascist" in m for m in msgs)
        assert any(m.startswith("The Fascists are:") for m in msgs)


def test_liberals_see_only_self_role():
    import random
    random.seed(13)
    g = _make_game(5)
    g.on_start()
    for lib in [p for p in g.players if p.role == Role.LIBERAL]:
        msgs = _spoken(g, lib.name)
        assert any("You are a Liberal" in m for m in msgs)
        assert not any(m.startswith("The Fascists are:") for m in msgs)
        assert not any("You are Hitler" in m for m in msgs)
        assert not any("You are a Fascist" in m for m in msgs)


# ---------------------------------------------------------------------------
# Task 7 — Role-ack transitions to NOMINATION
# ---------------------------------------------------------------------------

def test_role_ack_transitions_to_nomination():
    import random
    random.seed(3)
    g = _make_game(5)
    g.on_start()
    assert g.phase == Phase.ROLE_REVEAL
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    assert g.phase == Phase.NOMINATION
    # Seat 0 is the first president.
    assert g.current_president_seat == 0
    assert g.current_chancellor_seat is None
    assert g.nominee_chancellor_seat is None


# ---------------------------------------------------------------------------
# Task 8 — Nomination and chancellor eligibility
# ---------------------------------------------------------------------------

def test_chancellor_eligibility_initial_game():
    """At game start, no term-limits apply; every alive non-president is eligible."""
    import random
    random.seed(19)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    eligible = g._eligible_chancellor_seats()
    assert pres.seat not in eligible
    assert sorted(eligible) == sorted(p.seat for p in g.players if p is not pres)


def test_nominate_sets_nominee_and_stays_in_nomination():
    import random
    random.seed(21)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    other = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{other.seat}")
    assert g.nominee_chancellor_seat == other.seat
    assert g.phase == Phase.NOMINATION


def test_cancel_nomination_clears_nominee():
    import random
    random.seed(22)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    other = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{other.seat}")
    g._action_cancel_nomination(pres, "cancel_nomination")
    assert g.nominee_chancellor_seat is None
    assert g.phase == Phase.NOMINATION


def test_term_limits_exclude_last_elected_pair_with_6_plus_alive():
    import random
    random.seed(23)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.last_elected_president_seat = 2
    g.last_elected_chancellor_seat = 3
    g.current_president_seat = 0
    eligible = g._eligible_chancellor_seats()
    assert 2 not in eligible
    assert 3 not in eligible
    assert 0 not in eligible  # self


def test_term_limits_only_chancellor_when_5_or_fewer_alive():
    import random
    random.seed(24)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.last_elected_president_seat = 2
    g.last_elected_chancellor_seat = 3
    g.current_president_seat = 0
    eligible = g._eligible_chancellor_seats()
    assert 2 in eligible
    assert 3 not in eligible
