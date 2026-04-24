# Secret Hitler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Secret Hitler as a new game under `server/games/secrethitler/`, implementing the canonical base rules (5–10 players) with accessibility-first messaging, minimal bots, and full persistence/serialization coverage.

**Architecture:** One `SecretHitler(Game)` class following the Coup pattern, backed by a phase-based state machine. The five executive powers are extracted to `powers.py`; the rest of the split mirrors `server/games/coup/` (`game.py`, `cards.py`, `player.py`, `bot.py`). Game state is a flat set of dataclass fields on the Game subclass; no nested `GameState`. The spec at `docs/superpowers/specs/2026-04-23-secret-hitler-design.md` is the source of truth for rules, phase graph, and messaging inventory.

**Tech Stack:** Python 3.13, dataclasses, Mashumaro JSON mixin, Mozilla Fluent (`.ftl`), pytest, uv. All development runs from `server/` with `uv run …`.

**Reference reading before starting (do not skip):**
- `docs/superpowers/specs/2026-04-23-secret-hitler-design.md` — the full spec. Every design decision is there.
- `server/games/coup/` — the house pattern for hidden-role games. Read `game.py`, `player.py`, `cards.py`, `bot.py` end to end.
- `server/games/pig/game.py` — smaller canonical example showing Options, keybinds, `_action_*`, `_is_*_enabled`, and `_is_*_hidden`.
- `server/games/base.py` — the `Game` and `Player` dataclasses, mixin composition, `prestart_validate`, `on_start`, `on_tick`.
- `server/game_utils/actions.py` — `Action`, `ActionSet`, `Visibility`, `MenuInput`.
- `server/game_utils/game_communication_mixin.py` — `broadcast_l`, `broadcast_personal_l`.
- `server/game_utils/options.py` — `IntOption`, `option_field`.
- `server/games/registry.py` — `@register_game`.
- `server/locales/en/coup.ftl` — locale file shape and Fluent select expressions.
- `server/tests/conftest.py` and `server/tests/test_coup.py` — test layout and `MockUser` fixture usage.
- `CLAUDE.md` at the repo root — reminder of the load-bearing invariants (sync/async boundary, dataclass state, 50ms tick, string menu IDs, `show_in_actions_menu=False` for per-choice actions, write locale before code, `rebuild_player_menu` after phase transitions).

**Execution style:**
- Commit after every step that has test coverage (every task ends with a commit step).
- Run only the Secret Hitler test file(s) after each task (`cd server && uv run pytest server/tests/test_secrethitler.py -v`), not the full suite.
- Run the CLI simulation smoke once at the end of each major section (`cd server && uv run python -m server.cli simulate secrethitler --bots 5`).
- `--test-serialization` must pass for the final run at each player count 5..10.

---

## File Structure

```
server/games/secrethitler/
├── __init__.py           # package marker, re-exports SecretHitler
├── cards.py              # Policy, Role, Party, Power enums; ROLE_COUNTS; FASCIST_TRACK_POWERS; deck composition
├── player.py             # SecretHitlerPlayer(Player), SecretHitlerOptions(GameOptions)
├── powers.py             # investigate_loyalty, special_election, policy_peek, execution, veto resolution
├── bot.py                # SecretHitlerBot — minimal action picker
└── game.py               # SecretHitler(Game) — phase dispatch, nomination/voting/legislation, win checks

server/locales/en/secrethitler.ftl   # all English strings (55–70 keys)
server/tests/test_secrethitler.py             # unit + play tests
server/tests/test_secrethitler_powers.py      # the five executive powers and veto
server/tests/test_secrethitler_persistence.py # save/load roundtrip at every phase boundary
```

Registration is one line at the top of `game.py`: `@register_game` above `class SecretHitler(Game):`. `GameRegistry` auto-discovers via the decorator; nothing else to touch there.

The locale file is authored first (per CLAUDE.md). The `check-locales` pre-commit hook handles parity across 29 languages — only `en/secrethitler.ftl` is hand-written in this plan.

No packet model changes are expected. If any emerge during implementation, run `cd server && uv run python tools/export_packet_schema.py` and commit both `server/packet_schema.json` and `clients/desktop/packet_schema.json`.

---

## Section 1 — Skeleton and registration

### Task 1: Package scaffold

**Files:**
- Create: `server/games/secrethitler/__init__.py`
- Create: `server/games/secrethitler/cards.py` (stub)
- Create: `server/games/secrethitler/player.py` (stub)
- Create: `server/games/secrethitler/powers.py` (stub)
- Create: `server/games/secrethitler/bot.py` (stub)
- Create: `server/games/secrethitler/game.py` (stub)

- [ ] **Step 1: Write the failing test**

Create `server/tests/test_secrethitler.py`:

```python
"""Tests for Secret Hitler game."""

import pytest
from server.games.registry import GameRegistry


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: FAIL — `GameRegistry.get("secrethitler")` returns `None`.

- [ ] **Step 3: Write minimal implementation**

Create `server/games/secrethitler/__init__.py`:

```python
"""Secret Hitler game package."""

from .game import SecretHitler

__all__ = ["SecretHitler"]
```

Create `server/games/secrethitler/cards.py` with a placeholder (will be filled out in Task 2):

```python
"""Policy / Role / Party / Power enums and deck composition for Secret Hitler."""
```

Create `server/games/secrethitler/player.py` with a placeholder (filled in Task 3):

```python
"""Player and Options dataclasses for Secret Hitler."""
```

Create `server/games/secrethitler/powers.py` with a placeholder (filled in Section 4):

```python
"""Executive power resolution for Secret Hitler."""
```

Create `server/games/secrethitler/bot.py` with a placeholder (filled in Section 5):

```python
"""Minimal bot for Secret Hitler."""
```

Create `server/games/secrethitler/game.py`:

```python
"""Secret Hitler game implementation — skeleton."""

from dataclasses import dataclass, field

from ..base import Game, Player
from ..registry import register_game


@dataclass
@register_game
class SecretHitler(Game):
    """Secret Hitler — social-deduction legislative game, 5–10 players."""

    players: list[Player] = field(default_factory=list)

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

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> Player:
        return Player(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
```

Also import the package so `@register_game` fires. Find where other games are imported and add `secrethitler`:

```bash
grep -rn "from .coup" server/games/__init__.py server/ 2>/dev/null
```

If `server/games/__init__.py` imports each game package for registration side effects (typical pattern — verify by reading the file), add:

```python
from . import secrethitler  # noqa: F401
```

If games are instead imported via dynamic discovery or from `registry.py`, follow the existing mechanism — do not invent a new one. Check by reading `server/games/__init__.py` and `server/games/registry.py` before editing.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: PASS for both `test_game_registered` and `test_player_count_bounds`.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler.py server/games/__init__.py
git commit -m "feat(secrethitler): package scaffold and registration"
```

---

### Task 2: `cards.py` — enums, role counts, power table, deck composition

**Files:**
- Modify: `server/games/secrethitler/cards.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

Append to `server/tests/test_secrethitler.py`:

```python
from server.games.secrethitler.cards import (
    Policy,
    Role,
    Party,
    Power,
    ROLE_COUNTS,
    FASCIST_TRACK_POWERS,
    build_policy_deck,
)


def test_role_counts_by_player_count():
    # (liberals, fascists_not_including_hitler, hitler=1 always)
    assert ROLE_COUNTS[5] == (3, 1, 1)
    assert ROLE_COUNTS[6] == (4, 1, 1)
    assert ROLE_COUNTS[7] == (4, 2, 1)
    assert ROLE_COUNTS[8] == (5, 2, 1)
    assert ROLE_COUNTS[9] == (5, 3, 1)
    assert ROLE_COUNTS[10] == (6, 3, 1)


def test_fascist_track_powers_5_6():
    # (policies_enacted_1_through_5) -> Power
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: FAIL — `ImportError: cannot import name 'Policy' from 'server.games.secrethitler.cards'`.

- [ ] **Step 3: Write minimal implementation**

Overwrite `server/games/secrethitler/cards.py`:

```python
"""Policy / Role / Party / Power enums and deck composition for Secret Hitler."""

from enum import Enum


class Policy(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"


class Party(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"


class Role(str, Enum):
    LIBERAL = "liberal"
    FASCIST = "fascist"
    HITLER = "hitler"

    @property
    def party(self) -> Party:
        if self is Role.LIBERAL:
            return Party.LIBERAL
        return Party.FASCIST


class Power(str, Enum):
    NONE = "none"
    INVESTIGATE = "investigate"
    SPECIAL_ELECTION = "special_election"
    POLICY_PEEK = "policy_peek"
    EXECUTION = "execution"


# (liberals, fascists_excluding_hitler, hitler=1 always)
ROLE_COUNTS: dict[int, tuple[int, int, int]] = {
    5: (3, 1, 1),
    6: (4, 1, 1),
    7: (4, 2, 1),
    8: (5, 2, 1),
    9: (5, 3, 1),
    10: (6, 3, 1),
}


# Power for slots 1..5 of the fascist track, bucketed by player count.
FASCIST_TRACK_POWERS: dict[str, tuple[Power, Power, Power, Power, Power]] = {
    "5-6": (
        Power.NONE,
        Power.NONE,
        Power.POLICY_PEEK,
        Power.EXECUTION,
        Power.EXECUTION,
    ),
    "7-8": (
        Power.NONE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    ),
    "9-10": (
        Power.INVESTIGATE,
        Power.INVESTIGATE,
        Power.SPECIAL_ELECTION,
        Power.EXECUTION,
        Power.EXECUTION,
    ),
}


def track_bucket_for(player_count: int) -> str:
    """Return the fascist-track bucket key for a given player count."""
    if 5 <= player_count <= 6:
        return "5-6"
    if 7 <= player_count <= 8:
        return "7-8"
    if 9 <= player_count <= 10:
        return "9-10"
    raise ValueError(f"Unsupported player count: {player_count}")


def build_policy_deck() -> list[Policy]:
    """Return a fresh, unshuffled 17-card deck: 6 liberal + 11 fascist."""
    return [Policy.LIBERAL] * 6 + [Policy.FASCIST] * 11
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/cards.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): policy/role/party/power enums and deck composition"
```

---

### Task 3: `player.py` — `SecretHitlerPlayer` and `SecretHitlerOptions`

**Files:**
- Modify: `server/games/secrethitler/player.py`
- Modify: `server/games/secrethitler/game.py` (wire up `create_player`, `options` field)
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

Append to `server/tests/test_secrethitler.py`:

```python
from server.games.secrethitler.player import (
    SecretHitlerPlayer,
    SecretHitlerOptions,
)
from server.games.secrethitler.game import SecretHitler


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: FAIL — `ImportError: cannot import name 'SecretHitlerPlayer'`.

- [ ] **Step 3: Write minimal implementation**

Overwrite `server/games/secrethitler/player.py`:

```python
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
```

Update the `SecretHitler` class in `server/games/secrethitler/game.py` by replacing its body up to (and including) `create_player` with:

```python
"""Secret Hitler game implementation — skeleton."""

from dataclasses import dataclass, field

from ..base import Game
from ..registry import register_game
from .player import SecretHitlerPlayer, SecretHitlerOptions


@dataclass
@register_game
class SecretHitler(Game):
    """Secret Hitler — social-deduction legislative game, 5–10 players."""

    players: list[SecretHitlerPlayer] = field(default_factory=list)
    options: SecretHitlerOptions = field(default_factory=SecretHitlerOptions)

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

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/
git commit -m "feat(secrethitler): player and options dataclasses"
```

---

### Task 4: Locale skeleton — first batch of strings

**Files:**
- Create: `server/locales/en/secrethitler.ftl`

- [ ] **Step 1: Write the failing test**

Append to `server/tests/test_secrethitler.py`:

```python
from pathlib import Path


def test_locale_file_exists_and_has_game_name_key():
    locale_path = Path(__file__).parent.parent / "locales" / "en" / "secrethitler.ftl"
    assert locale_path.exists(), f"Missing locale file: {locale_path}"
    text = locale_path.read_text(encoding="utf-8")
    assert "game-name-secrethitler = Secret Hitler" in text
    # Role-reveal strings are authored up front per CLAUDE.md policy.
    for key in (
        "sh-you-are-liberal",
        "sh-you-are-fascist",
        "sh-you-are-hitler",
        "sh-fascist-teammates",
    ):
        assert key in text, f"Missing key {key} in locale file"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py::test_locale_file_exists_and_has_game_name_key -v`
Expected: FAIL — file does not exist.

- [ ] **Step 3: Write minimal implementation**

Create `server/locales/en/secrethitler.ftl` with the full v1 key set (role reveal, nomination, voting, legislation, tracker, powers, veto, win conditions, and option-menu strings). This is the implementation plan in locale form — all keys used anywhere in the game must appear here.

```ftl
# Secret Hitler — English locale

game-name-secrethitler = Secret Hitler
category-social-deduction = Social deduction

# Options menu
sh-set-vote-timeout = President vote timeout: { $seconds } seconds
sh-enter-vote-timeout = Enter president vote timeout in seconds (30 to 600)
sh-option-changed-vote-timeout = President vote timeout is now { $seconds } seconds.
sh-desc-vote-timeout = How long the president has to call the vote before it auto-calls.
sh-set-bot-think = Bot think time: { $seconds } seconds
sh-enter-bot-think = Enter bot think time in seconds (0 to 10)
sh-option-changed-bot-think = Bot think time is now { $seconds } seconds.
sh-desc-bot-think = Delay bots wait before acting, in seconds.

# Prestart errors
sh-error-need-5-players = Secret Hitler requires 5 to 10 players.

# Role reveal (private)
sh-you-are-liberal = You are a Liberal.
sh-you-are-fascist = You are a Fascist.
sh-you-are-hitler = You are Hitler.
sh-fascist-teammates = The Fascists are: { $names }. Hitler is: { $hitler }.
sh-hitler-knows-teammates = The Fascists are: { $names }. You are Hitler.
sh-acknowledge-role = Acknowledge role

# Nomination
sh-president-is = { $player } is President.
sh-you-are-president = You are President.
sh-president-nominates = { $president } nominates { $chancellor } as Chancellor.
sh-president-can-call-vote = Discussion is open. When ready, call for the vote.
sh-nominate = Nominate { $player }
sh-call-vote = Call for vote
sh-cancel-nomination = Cancel nomination
sh-vote-timeout-approaching = Vote will auto-call in { $seconds } seconds.

# Voting
sh-voting-open = Voting is open. Ja or Nein?
sh-vote-ja = Ja!
sh-vote-nein = Nein!
sh-you-voted-ja = You voted Ja!
sh-you-voted-nein = You voted Nein!
sh-players-still-voting = Still voting: { $names }.
sh-vote-result =
    { $passed ->
        [true] The vote passes.
       *[false] The vote fails.
    }
sh-vote-roll-call = { $player } voted { $vote ->
        [ja] Ja!
       *[nein] Nein!
    }.

# Legislation
sh-president-draws = President draws three policies.
sh-your-policies = Your policies: { $p1 }, { $p2 }, { $p3 }.
sh-president-discards = President discards one policy.
sh-chancellor-receives = Chancellor receives two policies.
sh-your-policies-chancellor = Your policies: { $p1 }, { $p2 }.
sh-discard-policy = Discard: { $policy }
sh-enact-policy = Enact: { $policy }
sh-propose-veto = Propose veto
sh-chancellor-enacts =
    { $policy ->
        [liberal] A Liberal policy is enacted. Liberal track: { $liberal } of 5.
       *[fascist] A Fascist policy is enacted. Fascist track: { $fascist } of 6.
    }
sh-policy-liberal = Liberal
sh-policy-fascist = Fascist

# Election tracker / chaos
sh-tracker-advances = Election tracker is at { $count } of 3.
sh-chaos-top-policy = Chaos! The top policy is enacted automatically.

# Executive powers
sh-power-investigate = President will investigate a player's loyalty.
sh-investigate-target = Investigate { $player }
sh-you-see-party =
    { $party ->
        [liberal] { $player } is a Liberal.
       *[fascist] { $player } is a Fascist.
    }
sh-power-special-election = President will call a special election.
sh-choose-president-target = Choose { $player } as next President
sh-power-policy-peek = President peeks at the top three policies.
sh-you-peek = Top three policies: { $p1 }, { $p2 }, { $p3 }.
sh-acknowledge-peek = Acknowledge
sh-power-execution = President will execute a player.
sh-execute-target = Execute { $player }
sh-player-executed = { $player } has been executed.

# Veto
sh-chancellor-proposes-veto = Chancellor proposes to veto this agenda.
sh-veto-accept = Accept veto
sh-veto-reject = Reject veto
sh-president-accepts-veto = President accepts the veto. Both policies are discarded.
sh-president-rejects-veto = President rejects the veto. Chancellor must enact.

# Persistent (standard) actions
sh-view-tracks = View policy tracks
sh-view-tracks-content = Liberal track: { $liberal } of 5. Fascist track: { $fascist } of 6.
sh-view-government = View government
sh-view-government-content = President: { $president }. Chancellor: { $chancellor }. Previous elected: { $lastpres } / { $lastchan }.
sh-view-players = View players
sh-view-my-role = View my role
sh-view-election-tracker = View election tracker

# Win conditions
sh-liberals-win-policies = Liberals win! Five Liberal policies enacted.
sh-liberals-win-execution = Liberals win! Hitler has been executed.
sh-fascists-win-policies = Fascists win! Six Fascist policies enacted.
sh-fascists-win-hitler-elected = Fascists win! Hitler was elected Chancellor after three Fascist policies.
sh-final-roles = Final roles: { $lines }
sh-final-role-line = { $player } — { $role ->
        [liberal] Liberal
        [fascist] Fascist
       *[hitler] Hitler
    }

# Disconnect / pause
sh-paused-for-reconnect = Game paused — waiting for { $player } to reconnect.
sh-resumed = Game resumed.
sh-forfeit = Forfeit disconnected player
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v`
Expected: all tests PASS.

Also run the locale completeness test to confirm no stray syntax issues:

```bash
cd server && uv run pytest server/tests/test_locale_completeness.py -v
```

Expected: PASS. If it fails due to missing keys in non-English locales, that is the translators' job — but confirm the failure is not due to malformed Fluent syntax in the English file.

- [ ] **Step 5: Commit**

```bash
git add server/locales/en/secrethitler.ftl server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): English locale (full v1 key set)"
```

---

### Task 5: `on_start` deals roles and initial state

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

Append to `server/tests/test_secrethitler.py`:

```python
from server.core.users.test_user import MockUser
from server.games.secrethitler.cards import Role


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"player{i + 1}"
        name = f"P{i + 1}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name, pid))
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
    assert len(g.deck) == 17
    assert g.deck.count(...) if False else True  # placeholder
    from server.games.secrethitler.cards import Policy
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
        g.attach_user(pid, MockUser(f"P{i}", pid))
    errors = g.prestart_validate()
    # prestart_validate returns locale keys or (key, kwargs) tuples
    assert any(
        (isinstance(e, str) and e == "sh-error-need-5-players")
        or (isinstance(e, tuple) and e[0] == "sh-error-need-5-players")
        for e in errors
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "on_start or prestart"`
Expected: FAIL — `deck`, `discard`, etc. do not exist on `SecretHitler`; no role dealing.

- [ ] **Step 3: Write minimal implementation**

Replace the body of `server/games/secrethitler/game.py` with:

```python
"""Secret Hitler game implementation."""

from dataclasses import dataclass, field
from enum import Enum
import random

from ..base import Game
from ..registry import register_game
from .cards import (
    Policy,
    Role,
    Party,
    Power,
    ROLE_COUNTS,
    FASCIST_TRACK_POWERS,
    build_policy_deck,
    track_bucket_for,
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
            return  # prestart_validate guards; defensive no-op

        # Stable seats (0-based) in current player order.
        for i, p in enumerate(active):
            p.seat = i
            p.is_alive = True
            p.has_been_investigated = False
            p.connected = True

        # Deal roles.
        libs, fascists, _hitler = ROLE_COUNTS[n]
        role_pool = (
            [Role.LIBERAL] * libs
            + [Role.FASCIST] * fascists
            + [Role.HITLER]
        )
        random.shuffle(role_pool)
        for p, role in zip(active, role_pool):
            p.role = role

        # Build shuffled policy deck.
        self.deck = build_policy_deck()
        random.shuffle(self.deck)
        self.discard = []

        # Reset tracks and rotation.
        self.liberal_policies = 0
        self.fascist_policies = 0
        self.election_tracker = 0
        self.president_seat = 0
        self.special_election_override = None
        self.current_president_seat = None
        self.current_chancellor_seat = None
        self.last_elected_president_seat = None
        self.last_elected_chancellor_seat = None

        # Legislative and power state.
        self.nominee_chancellor_seat = None
        self.votes = {}
        self.vote_call_deadline_tick = None
        self.president_drawn_policies = None
        self.chancellor_received_policies = None
        self.veto_proposed = False
        self.pending_power = Power.NONE
        self.power_target_seat = None
        self.policy_peek_cards = None

        # Phase-wide flags.
        self.paused_for_reconnect = False
        self.game_over = False
        self.winner = None
        self.win_reason = None
        self.role_ack_seats = set()

        self.phase = Phase.ROLE_REVEAL
        self._deliver_role_reveals()

    # Placeholder; full implementation in Task 6.
    def _deliver_role_reveals(self) -> None:
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "on_start or prestart"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): on_start deals roles and builds deck"
```

---

### Task 6: Role reveal messaging

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

Append to `server/tests/test_secrethitler.py`:

```python
def _user_messages(g: SecretHitler, player_name: str) -> list[str]:
    """Return raw message keys spoken to the given player (MockUser records them)."""
    p = g.get_player_by_name(player_name)
    u = g.get_user(p)
    # MockUser exposes a history list of (message_id_or_text, ...)
    return getattr(u, "spoken_l", []) + getattr(u, "spoken", [])


@pytest.mark.parametrize("n", [5, 6])
def test_role_reveal_hitler_knows_fascists_at_5_6(n):
    import random
    random.seed(7)
    g = _make_game(n)
    g.on_start()
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    keys = _user_messages(g, hitler.name)
    assert any("sh-you-are-hitler" in str(k) for k in keys)
    assert any("sh-hitler-knows-teammates" in str(k) for k in keys)


@pytest.mark.parametrize("n", [7, 8, 9, 10])
def test_role_reveal_hitler_blind_at_7_plus(n):
    import random
    random.seed(11)
    g = _make_game(n)
    g.on_start()
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    keys = _user_messages(g, hitler.name)
    assert any("sh-you-are-hitler" in str(k) for k in keys)
    assert not any("sh-hitler-knows-teammates" in str(k) for k in keys)


def test_fascists_always_see_teammates():
    import random
    random.seed(5)
    g = _make_game(7)
    g.on_start()
    for f in [p for p in g.players if p.role == Role.FASCIST]:
        keys = _user_messages(g, f.name)
        assert any("sh-you-are-fascist" in str(k) for k in keys)
        assert any("sh-fascist-teammates" in str(k) for k in keys)


def test_liberals_see_only_self_role():
    import random
    random.seed(13)
    g = _make_game(5)
    g.on_start()
    for lib in [p for p in g.players if p.role == Role.LIBERAL]:
        keys = _user_messages(g, lib.name)
        assert any("sh-you-are-liberal" in str(k) for k in keys)
        assert not any("sh-fascist-teammates" in str(k) for k in keys)
        assert not any("sh-hitler-knows-teammates" in str(k) for k in keys)
```

Before running this, open `server/core/users/test_user.py` and confirm the attribute name MockUser uses to record `speak_l` calls. If it is different from `spoken_l`, adjust `_user_messages` accordingly. Do not invent an attribute.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k role_reveal`
Expected: FAIL — `_deliver_role_reveals` is a no-op; no messages recorded.

- [ ] **Step 3: Write minimal implementation**

Replace `_deliver_role_reveals` in `server/games/secrethitler/game.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k role_reveal`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): role reveal with hidden-info discipline"
```

---

## Section 2 — Nomination and voting

### Task 7: Role-reveal acknowledgement advances to NOMINATION

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

Append:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k ack_transitions`
Expected: FAIL — `_action_acknowledge_role` does not exist.

- [ ] **Step 3: Write minimal implementation**

In `server/games/secrethitler/game.py`, add:

```python
from ..base import Player
from ..base import Phase as _UnusedBasePhase  # noqa: F401  # (only if needed — remove if not)

# ... inside SecretHitler class ...

def _action_acknowledge_role(self, player: "Player", action_id: str) -> None:
    """Record that `player` has acknowledged their role."""
    if self.phase != Phase.ROLE_REVEAL:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    self.role_ack_seats.add(sh_player.seat)
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
    self.broadcast_l(
        "sh-president-is",
        player=self._player_at_seat(self.current_president_seat).name,
    )

def _next_president_seat(self) -> int:
    """Compute the next president seat, consuming special-election override if set."""
    if self.special_election_override is not None:
        seat = self.special_election_override
        self.special_election_override = None
        return seat
    # Advance president_seat to the next alive seat.
    active_alive = sorted(
        p.seat for p in self.players if not p.is_spectator and p.is_alive
    )
    if not active_alive:
        return 0
    # Find the next seat strictly greater than self.president_seat (wrap-around).
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
```

Note: `_next_president_seat` must set `president_seat` to the seat that is *becoming* president so the next call advances forward. On first call after `on_start`, `self.president_seat` starts at 0 and the code above would jump past 0; fix by special-casing the very first nomination — track a bool `_first_nomination: bool = True` on the dataclass, default `True`, and if set, return the lowest alive seat and clear the flag:

```python
_first_nomination: bool = True  # add to the dataclass field list

# in _next_president_seat:
if self._first_nomination:
    self._first_nomination = False
    self.president_seat = active_alive[0]
    return self.president_seat
```

Also reset `_first_nomination = True` inside `on_start`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k ack_transitions`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): role ack transitions to nomination"
```

---

### Task 8: Nomination — president picks an eligible chancellor

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

Rules recap (spec §Rules): nominate excludes dead, self, previous president, and previous chancellor. When ≤5 alive, only previous chancellor is restricted.

- [ ] **Step 1: Write the failing test**

```python
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
    assert g.phase == Phase.NOMINATION  # call_vote still required


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
    g = _make_game(7)
    import random
    random.seed(23)
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
    g = _make_game(5)
    import random
    random.seed(24)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.last_elected_president_seat = 2
    g.last_elected_chancellor_seat = 3
    g.current_president_seat = 0
    # All 5 are alive, which counts as ≤5, so previous-president restriction lifts.
    eligible = g._eligible_chancellor_seats()
    assert 2 in eligible
    assert 3 not in eligible
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "chancellor_eligibility or nominate or cancel or term_limits"`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Add to `SecretHitler` in `server/games/secrethitler/game.py`:

```python
def _alive_count(self) -> int:
    return sum(
        1 for p in self.players if not p.is_spectator and p.is_alive
    )

def _eligible_chancellor_seats(self) -> list[int]:
    alive = [
        p.seat
        for p in self.players
        if not p.is_spectator and p.is_alive and p.seat != self.current_president_seat
    ]
    if self.last_elected_chancellor_seat in alive:
        alive.remove(self.last_elected_chancellor_seat)
    if self._alive_count() > 5 and self.last_elected_president_seat in alive:
        alive.remove(self.last_elected_president_seat)
    return sorted(alive)

def _action_nominate(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.NOMINATION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
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

def _action_cancel_nomination(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.NOMINATION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    self.nominee_chancellor_seat = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "chancellor_eligibility or nominate or cancel or term_limits"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): chancellor nomination and eligibility rules"
```

---

### Task 9: Call vote → transition to VOTING, collect votes, tally

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def _nominate_and_call_vote(g: SecretHitler, nominee_seat: int) -> None:
    pres = g._player_at_seat(g.current_president_seat)
    g._action_nominate(pres, f"nominate_{nominee_seat}")
    g._action_call_vote(pres, "call_vote")


def test_call_vote_transitions_to_voting():
    import random
    random.seed(31)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    _nominate_and_call_vote(g, 1 if g.current_president_seat != 1 else 2)
    assert g.phase == Phase.VOTING
    assert g.votes == {}


def test_votes_collected_until_all_alive_voted():
    import random
    random.seed(32)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    target = 1 if g.current_president_seat != 1 else 2
    _nominate_and_call_vote(g, target)
    alive = [p for p in g.players if p.is_alive]
    # All vote Ja
    for p in alive:
        g._action_vote_ja(p, "vote_ja")
    # With all Ja, pass → move to legislation
    assert g.phase == Phase.PRES_LEGISLATION
    assert g.last_elected_president_seat == g.current_president_seat
    assert g.last_elected_chancellor_seat == target


def test_failed_vote_advances_tracker_and_returns_to_nomination():
    import random
    random.seed(33)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    target = 1 if g.current_president_seat != 1 else 2
    original_pres = g.current_president_seat
    _nominate_and_call_vote(g, target)
    for p in g.players:
        g._action_vote_nein(p, "vote_nein")
    assert g.phase == Phase.NOMINATION
    assert g.election_tracker == 1
    # President rotated (not the same seat).
    assert g.current_president_seat != original_pres
    # Failed votes do not lock term limits.
    assert g.last_elected_president_seat is None
    assert g.last_elected_chancellor_seat is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "call_vote or votes_collected or failed_vote"`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Add to `SecretHitler`:

```python
def _action_call_vote(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.NOMINATION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    if self.nominee_chancellor_seat is None:
        return
    self.phase = Phase.VOTING
    self.votes = {}
    self.broadcast_l("sh-voting-open")

def _action_vote_ja(self, player: "Player", action_id: str) -> None:
    self._record_vote(player, True)

def _action_vote_nein(self, player: "Player", action_id: str) -> None:
    self._record_vote(player, False)

def _record_vote(self, player: "Player", ja: bool) -> None:
    if self.phase != Phase.VOTING:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if not sh_player.is_alive:
        return
    if sh_player.seat in self.votes:
        return
    self.votes[sh_player.seat] = ja
    user = self.get_user(player)
    if user:
        user.speak_l("sh-you-voted-ja" if ja else "sh-you-voted-nein", "table")
    if self._all_alive_voted():
        self._tally_vote()

def _all_alive_voted(self) -> bool:
    alive_seats = {p.seat for p in self.players if not p.is_spectator and p.is_alive}
    return alive_seats <= set(self.votes.keys())

def _tally_vote(self) -> None:
    # Public roll-call reveal.
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
    # Hitler-elected-after-3F win check.
    chancellor = self._player_at_seat(self.nominee_chancellor_seat)
    if self.fascist_policies >= 3 and chancellor.role == Role.HITLER:
        self._end_game(Party.FASCIST, "sh-fascists-win-hitler-elected")
        return
    # Lock in term limits.
    self.last_elected_president_seat = self.current_president_seat
    self.last_elected_chancellor_seat = self.nominee_chancellor_seat
    self.current_chancellor_seat = self.nominee_chancellor_seat
    self.election_tracker = 0
    # Draw 3 policies.
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

def _send_policies_private(
    self, player: SecretHitlerPlayer, policies: list[Policy], key: str
) -> None:
    user = self.get_user(player)
    if not user:
        return
    args = {f"p{i + 1}": p.value for i, p in enumerate(policies)}
    user.speak_l(key, "table", **args)

def _end_game(self, winner: Party, reason_key: str) -> None:
    self.phase = Phase.GAME_OVER
    self.game_over = True
    self.winner = winner
    self.win_reason = reason_key
    self.broadcast_l(reason_key)
    # Reveal final roles.
    lines = ", ".join(f"{p.name} ({p.role.value})" for p in self.players if not p.is_spectator)
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "call_vote or votes_collected or failed_vote"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): voting, tally, term limits, and tracker advance"
```

---

### Task 10: Vote timeout auto-calls the vote

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def test_vote_auto_calls_on_timeout():
    import random
    random.seed(41)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    other = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{other.seat}")
    # With default 180s timeout and a 50ms tick, that's 3600 ticks.
    # Drive ticks until vote is called.
    for _ in range(g.options.president_vote_timeout_seconds * 20 + 2):
        g.on_tick()
    assert g.phase == Phase.VOTING


def test_vote_timer_respects_pause():
    import random
    random.seed(42)
    g = _make_game(5)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    other = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{other.seat}")
    g.paused_for_reconnect = True
    for _ in range(g.options.president_vote_timeout_seconds * 20 + 10):
        g.on_tick()
    assert g.phase == Phase.NOMINATION  # timer did not expire
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "vote_auto or timer_respects_pause"`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Replace `_action_nominate` to start the timer, and override `on_tick`:

```python
def _action_nominate(self, player: "Player", action_id: str) -> None:
    # ... existing body ...
    self.vote_call_deadline_tick = self.tick + (
        self.options.president_vote_timeout_seconds * 20
    )

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
```

Inside `_action_call_vote`, set `self.vote_call_deadline_tick = None` at the top of the successful path.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "vote_auto or timer_respects_pause"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): vote auto-call on timeout, pause-aware tick"
```

---

## Section 3 — Legislation

### Task 11: President discards a policy → chancellor receives two

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def _run_to_pres_legislation(g: SecretHitler) -> None:
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    pres = g._player_at_seat(g.current_president_seat)
    other = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{other.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")


def test_president_discard_moves_to_chan_legislation():
    import random
    random.seed(51)
    g = _make_game(5)
    g.on_start()
    _run_to_pres_legislation(g)
    assert g.phase == Phase.PRES_LEGISLATION
    assert len(g.president_drawn_policies) == 3

    pres = g._player_at_seat(g.current_president_seat)
    g._action_discard_policy(pres, "discard_0")
    assert g.phase == Phase.CHAN_LEGISLATION
    assert g.president_drawn_policies is None
    assert g.chancellor_received_policies is not None
    assert len(g.chancellor_received_policies) == 2
    assert len(g.discard) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k discard_moves`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

```python
def _action_discard_policy(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.PRES_LEGISLATION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k discard_moves`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): president discards, chancellor receives"
```

---

### Task 12: Chancellor enacts → update track, check win, resolve power or return to nomination

**Files:**
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def test_chancellor_enact_liberal_increments_track_and_returns_to_nomination():
    import random
    random.seed(61)
    g = _make_game(5)
    g.on_start()
    _run_to_pres_legislation(g)
    # Force both remaining chancellor policies to LIBERAL after the president's discard.
    pres = g._player_at_seat(g.current_president_seat)
    g.president_drawn_policies = [Policy.LIBERAL, Policy.LIBERAL, Policy.FASCIST]
    g._action_discard_policy(pres, "discard_2")  # discard the fascist
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(chancellor, "enact_0")
    assert g.liberal_policies == 1
    assert g.fascist_policies == 0
    assert g.phase == Phase.NOMINATION
    assert g.chancellor_received_policies is None


def test_chancellor_enact_fascist_triggers_power_slot_at_9p_slot1():
    """9-10p track: slot 1 triggers INVESTIGATE immediately."""
    import random
    random.seed(62)
    g = _make_game(9)
    g.on_start()
    _run_to_pres_legislation(g)
    pres = g._player_at_seat(g.current_president_seat)
    g.president_drawn_policies = [Policy.FASCIST, Policy.FASCIST, Policy.LIBERAL]
    g._action_discard_policy(pres, "discard_2")
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(chancellor, "enact_0")
    assert g.fascist_policies == 1
    assert g.phase == Phase.POWER_RESOLUTION
    assert g.pending_power == Power.INVESTIGATE


def test_five_liberal_policies_win():
    import random
    random.seed(63)
    g = _make_game(5)
    g.on_start()
    # Shortcut: directly bump liberal_policies to 4, then enact one more.
    _run_to_pres_legislation(g)
    g.liberal_policies = 4
    pres = g._player_at_seat(g.current_president_seat)
    g.president_drawn_policies = [Policy.LIBERAL, Policy.LIBERAL, Policy.FASCIST]
    g._action_discard_policy(pres, "discard_2")
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(chancellor, "enact_0")
    assert g.liberal_policies == 5
    assert g.phase == Phase.GAME_OVER
    assert g.winner == Party.LIBERAL
    assert g.win_reason == "sh-liberals-win-policies"


def test_six_fascist_policies_win():
    import random
    random.seed(64)
    g = _make_game(5)
    g.on_start()
    _run_to_pres_legislation(g)
    g.fascist_policies = 5
    pres = g._player_at_seat(g.current_president_seat)
    g.president_drawn_policies = [Policy.FASCIST, Policy.FASCIST, Policy.LIBERAL]
    g._action_discard_policy(pres, "discard_2")
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_enact_policy(chancellor, "enact_0")
    assert g.fascist_policies == 6
    assert g.phase == Phase.GAME_OVER
    assert g.winner == Party.FASCIST
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "chancellor_enact or five_liberal or six_fascist"`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

```python
def _action_enact_policy(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.CHAN_LEGISLATION:
        return
    if self.veto_proposed:
        return  # president must resolve veto first
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_chancellor_seat:
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
    # Resolve fascist-track power if applicable.
    if enacted == Policy.FASCIST:
        bucket = track_bucket_for(self._active_player_count())
        slot = self.fascist_policies  # 1..5
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k "chancellor_enact or five_liberal or six_fascist"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): chancellor enactment, track-win check, power dispatch"
```

---

## Section 4 — Executive powers

### Task 13: `powers.py` module — investigate loyalty

**Files:**
- Modify: `server/games/secrethitler/powers.py`
- Modify: `server/games/secrethitler/game.py` (delegate)
- Create: `server/tests/test_secrethitler_powers.py`

- [ ] **Step 1: Write the failing test**

Create `server/tests/test_secrethitler_powers.py`:

```python
"""Tests for Secret Hitler executive powers."""

import pytest
import random

from server.games.secrethitler.game import SecretHitler, Phase
from server.games.secrethitler.cards import Policy, Role, Power, Party
from server.core.users.test_user import MockUser


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"player{i + 1}"
        name = f"P{i + 1}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name, pid))
    return g


def _run_to_power(g: SecretHitler, enacted_fascist: int) -> None:
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    # Shortcut: set fascist_policies directly, trigger power by enacting slot #(enacted_fascist+1).
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
    pres_user = g.get_user(pres)
    target_user = g.get_user(target)
    before = len(getattr(pres_user, "spoken_l", []))
    g._action_investigate(pres, f"investigate_{target.seat}")
    pres_keys = [str(k) for k in getattr(pres_user, "spoken_l", [])[before:]]
    assert any("sh-you-see-party" in k for k in pres_keys)
    # No other player sees the result key.
    for p in g.players:
        if p is pres:
            continue
        u = g.get_user(p)
        other_keys = [str(k) for k in getattr(u, "spoken_l", [])]
        assert not any("sh-you-see-party" in k for k in other_keys)
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
    # Attempting to investigate an already-investigated target is a no-op.
    g._action_investigate(pres, f"investigate_{target.seat}")
    assert g.phase == Phase.POWER_RESOLUTION
    # Investigate an eligible player works.
    g._action_investigate(pres, f"investigate_{other.seat}")
    assert other.has_been_investigated is True
    assert g.phase == Phase.NOMINATION


def test_investigate_loyalty_hitler_shows_as_fascist():
    random.seed(103)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=1)
    pres = g._player_at_seat(g.current_president_seat)
    # Force a target to be Hitler.
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    if hitler is pres:
        # Swap roles so pres is not Hitler.
        other = next(p for p in g.players if p is not pres)
        other.role, pres.role = pres.role, other.role
        hitler = other
    pres_user = g.get_user(pres)
    before = len(getattr(pres_user, "spoken_l", []))
    g._action_investigate(pres, f"investigate_{hitler.seat}")
    # Inspect kwargs: MockUser.spoken_l should include ("sh-you-see-party", kwargs).
    calls = getattr(pres_user, "spoken_l", [])[before:]
    # Find the relevant call by key.
    for entry in calls:
        if "sh-you-see-party" in str(entry):
            # entry is expected to include party="fascist" somehow.
            assert "fascist" in str(entry).lower()
            break
    else:
        pytest.fail("sh-you-see-party not emitted")
```

Note: before writing, open `server/core/users/test_user.py` to confirm the exact shape of `MockUser`'s recorded calls — the assertions above assume a serialized form that includes the kwargs. Adapt the assertions to match.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k investigate`
Expected: FAIL — `_action_investigate` not defined.

- [ ] **Step 3: Write minimal implementation**

Overwrite `server/games/secrethitler/powers.py`:

```python
"""Executive power resolution for Secret Hitler.

Each resolver mutates the game state and returns nothing; the game's phase
machine is responsible for what comes next.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .cards import Policy, Role, Power

if TYPE_CHECKING:
    from .game import SecretHitler
    from .player import SecretHitlerPlayer


def resolve_investigate(
    game: "SecretHitler",
    president: "SecretHitlerPlayer",
    target: "SecretHitlerPlayer",
) -> None:
    target.has_been_investigated = True
    party = target.role.party  # Hitler.party is FASCIST
    user = game.get_user(president)
    if user:
        user.speak_l(
            "sh-you-see-party",
            "table",
            player=target.name,
            party=party.value,
        )
    game.broadcast_l("sh-power-investigate", exclude=None)
    # (Power announcement already happened at power start; this is a no-op guard.)
```

Then in `server/games/secrethitler/game.py`, add the action handler that dispatches to `powers.resolve_investigate`:

```python
from . import powers  # at top of file

# inside SecretHitler
def _action_investigate(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.INVESTIGATE:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    try:
        target_seat = int(action_id.rsplit("_", 1)[-1])
    except ValueError:
        return
    target = next(
        (
            p
            for p in self.players
            if isinstance(p, SecretHitlerPlayer)
            and p.seat == target_seat
            and p.is_alive
            and not p.has_been_investigated
            and p is not sh_player
        ),
        None,
    )
    if target is None:
        return
    powers.resolve_investigate(self, sh_player, target)
    self.pending_power = Power.NONE
    self.power_target_seat = None
    self._begin_nomination()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k investigate`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler_powers.py
git commit -m "feat(secrethitler): investigate loyalty power"
```

---

### Task 14: Policy peek

**Files:**
- Modify: `server/games/secrethitler/powers.py`
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler_powers.py`

- [ ] **Step 1: Write the failing test**

```python
def test_policy_peek_reveals_top_three_only_to_president():
    random.seed(111)
    g = _make_game(5)
    _run_to_power(g, enacted_fascist=3)
    assert g.pending_power == Power.POLICY_PEEK
    pres = g._player_at_seat(g.current_president_seat)
    pres_user = g.get_user(pres)
    # Ensure we know what's on top.
    g.deck[:3] = [Policy.FASCIST, Policy.LIBERAL, Policy.LIBERAL]
    before = len(getattr(pres_user, "spoken_l", []))
    g._action_acknowledge_peek(pres, "acknowledge_peek")
    # Deck unchanged.
    assert g.deck[:3] == [Policy.FASCIST, Policy.LIBERAL, Policy.LIBERAL]
    # President sees sh-you-peek with the three values.
    keys = [str(k) for k in getattr(pres_user, "spoken_l", [])[before:]]
    assert any("sh-you-peek" in k for k in keys)
    # No one else sees the peeked cards.
    for p in g.players:
        if p is pres:
            continue
        u = g.get_user(p)
        other_keys = [str(k) for k in getattr(u, "spoken_l", [])]
        assert not any("sh-you-peek" in k for k in other_keys)
    assert g.phase == Phase.NOMINATION
```

Also: the 5-6p track does not trigger any power until slot 3, so `_run_to_power(g, enacted_fascist=3)` with n=5 should put us directly in POLICY_PEEK. Verify and adjust.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k policy_peek`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

In `powers.py`:

```python
def resolve_policy_peek(game: "SecretHitler", president: "SecretHitlerPlayer") -> None:
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
```

In `game.py`:

```python
def _action_acknowledge_peek(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.POLICY_PEEK:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    powers.resolve_policy_peek(self, sh_player)
    self.policy_peek_cards = None
    self.pending_power = Power.NONE
    self._begin_nomination()
```

Also call `resolve_policy_peek` once when the power starts (to emit the peek to the president immediately):

Actually — emit the peek up front in `_announce_power_start` for POLICY_PEEK (so the president sees the cards as soon as the phase transitions, then just acknowledges). Update:

```python
def _announce_power_start(self, power: Power) -> None:
    # ... existing mapping ...
    if power == Power.POLICY_PEEK:
        pres = self._player_at_seat(self.current_president_seat)
        powers.resolve_policy_peek(self, pres)
```

Then `_action_acknowledge_peek` just resets state and moves on.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k policy_peek`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler_powers.py
git commit -m "feat(secrethitler): policy peek power"
```

---

### Task 15: Execution — Hitler-kill win condition

**Files:**
- Modify: `server/games/secrethitler/powers.py`
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler_powers.py`

- [ ] **Step 1: Write the failing test**

```python
def test_execution_kills_target_and_advances_to_nomination():
    random.seed(121)
    g = _make_game(7)
    _run_to_power(g, enacted_fascist=4)
    assert g.pending_power == Power.EXECUTION
    pres = g._player_at_seat(g.current_president_seat)
    # Pick a liberal target to avoid triggering Hitler win.
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
    # Dead player is excluded from nomination eligibility and vote gating.
    assert target.seat not in g._eligible_chancellor_seats()
    # Start next nomination and simulate a vote — target should not count.
    pres2 = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p.is_alive and p is not pres2)
    g._action_nominate(pres2, f"nominate_{nominee.seat}")
    g._action_call_vote(pres2, "call_vote")
    alive = [p for p in g.players if p.is_alive]
    for p in alive:
        g._action_vote_ja(p, "vote_ja")
    # Vote tally should have happened without the dead player.
    assert g.phase != Phase.VOTING
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k execute`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

In `powers.py`:

```python
def resolve_execution(
    game: "SecretHitler",
    president: "SecretHitlerPlayer",
    target: "SecretHitlerPlayer",
) -> bool:
    """Execute `target`. Returns True if this ends the game (Hitler killed)."""
    target.is_alive = False
    game.broadcast_l("sh-player-executed", player=target.name)
    if target.role == Role.HITLER:
        return True
    return False
```

In `game.py`:

```python
def _action_execute(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.EXECUTION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    try:
        target_seat = int(action_id.rsplit("_", 1)[-1])
    except ValueError:
        return
    target = next(
        (
            p
            for p in self.players
            if isinstance(p, SecretHitlerPlayer)
            and p.seat == target_seat
            and p.is_alive
            and p is not sh_player
        ),
        None,
    )
    if target is None:
        return
    ended = powers.resolve_execution(self, sh_player, target)
    self.pending_power = Power.NONE
    if ended:
        self._end_game(Party.LIBERAL, "sh-liberals-win-execution")
        return
    self._begin_nomination()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k execute`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler_powers.py
git commit -m "feat(secrethitler): execution power and Hitler-kill win condition"
```

---

### Task 16: Special election — with correct rotation after

**Files:**
- Modify: `server/games/secrethitler/powers.py`
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler_powers.py`

- [ ] **Step 1: Write the failing test**

```python
def test_special_election_sets_override():
    random.seed(131)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=3)
    assert g.pending_power == Power.SPECIAL_ELECTION
    pres = g._player_at_seat(g.current_president_seat)
    target = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_choose_president(pres, f"choose_president_{target.seat}")
    assert g.phase == Phase.NOMINATION
    # The next president must be the electee.
    assert g.current_president_seat == target.seat


def test_special_election_rotation_resumes_from_original():
    random.seed(132)
    g = _make_game(9)
    _run_to_power(g, enacted_fascist=3)
    original_pres_seat = g.current_president_seat
    pres = g._player_at_seat(original_pres_seat)
    target = next(p for p in g.players if p.is_alive and p.seat != (original_pres_seat + 1) % 9 and p is not pres)
    g._action_choose_president(pres, f"choose_president_{target.seat}")
    # Run one government with the electee: nominate, vote fail.
    electee = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not electee and p.is_alive)
    g._action_nominate(electee, f"nominate_{nominee.seat}")
    g._action_call_vote(electee, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_nein(p, "vote_nein")
    # After the electee's government resolves, rotation must resume from the
    # seat *after* the original president, not after the electee.
    alive_seats = sorted(p.seat for p in g.players if p.is_alive)
    idx = alive_seats.index(original_pres_seat)
    expected_next = alive_seats[(idx + 1) % len(alive_seats)]
    assert g.current_president_seat == expected_next
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k special_election`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

In `powers.py`:

```python
def resolve_special_election(
    game: "SecretHitler",
    president: "SecretHitlerPlayer",
    target: "SecretHitlerPlayer",
) -> None:
    game.special_election_override = target.seat
```

In `game.py` add `_action_choose_president`:

```python
def _action_choose_president(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.POWER_RESOLUTION or self.pending_power != Power.SPECIAL_ELECTION:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    try:
        target_seat = int(action_id.rsplit("_", 1)[-1])
    except ValueError:
        return
    target = next(
        (
            p
            for p in self.players
            if isinstance(p, SecretHitlerPlayer)
            and p.seat == target_seat
            and p.is_alive
            and p is not sh_player
        ),
        None,
    )
    if target is None:
        return
    powers.resolve_special_election(self, sh_player, target)
    self.pending_power = Power.NONE
    self._begin_nomination()
```

Critical: `president_seat` must not advance when the override is consumed. Update `_next_president_seat` so it returns the override without mutating `self.president_seat`:

```python
def _next_president_seat(self) -> int:
    if self.special_election_override is not None:
        seat = self.special_election_override
        self.special_election_override = None
        return seat  # intentionally do NOT update self.president_seat
    # ... existing first-nomination and rotation logic ...
```

With this, after the electee's government resolves, the next `_next_president_seat` call rotates from the un-mutated `self.president_seat` (still the original president's seat), producing the correct "resume from seat-after-original-president" behavior.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k special_election`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler_powers.py
git commit -m "feat(secrethitler): special election with correct rotation resume"
```

---

### Task 17: Veto — unlock at 5F, propose, accept, reject

**Files:**
- Modify: `server/games/secrethitler/powers.py`
- Modify: `server/games/secrethitler/game.py`
- Modify: `server/tests/test_secrethitler_powers.py`

- [ ] **Step 1: Write the failing test**

```python
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
    assert g.veto_proposed is False  # locked


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
    random.seed(144)
    g = _make_game(5)
    _run_to_chan_legislation_with_fascist_policies(g, 5)
    chancellor = g._player_at_seat(g.current_chancellor_seat)
    g._action_propose_veto(chancellor, "propose_veto")
    pres = g._player_at_seat(g.current_president_seat)
    g._action_veto_reject(pres, "veto_reject")
    assert g.veto_proposed is False
    # Re-veto attempt is ignored.
    g._action_propose_veto(chancellor, "propose_veto")
    assert g.veto_proposed is False
    # Chancellor enacts, game proceeds.
    g._action_enact_policy(chancellor, "enact_0")
    assert g.phase in (Phase.POWER_RESOLUTION, Phase.NOMINATION, Phase.GAME_OVER)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k veto`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Add a `veto_blocked_this_turn: bool = False` field to `SecretHitler`. In `_action_discard_policy`, set `self.veto_blocked_this_turn = False`. Add handlers:

```python
def _action_propose_veto(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.CHAN_LEGISLATION:
        return
    if self.fascist_policies < 5:
        return
    if self.veto_blocked_this_turn:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_chancellor_seat:
        return
    self.veto_proposed = True
    self.broadcast_l("sh-chancellor-proposes-veto")

def _action_veto_accept(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.CHAN_LEGISLATION or not self.veto_proposed:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
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

def _action_veto_reject(self, player: "Player", action_id: str) -> None:
    if self.phase != Phase.CHAN_LEGISLATION or not self.veto_proposed:
        return
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return
    self.veto_proposed = False
    self.veto_blocked_this_turn = True
    self.broadcast_l("sh-president-rejects-veto")
```

Reset `veto_blocked_this_turn` to False at the start of each new `PRES_LEGISLATION` phase transition (already handled by `_on_vote_passed` and `_chaos_enact` — explicitly set `self.veto_blocked_this_turn = False` at the top of `_on_vote_passed`).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler_powers.py -v -k veto`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler_powers.py
git commit -m "feat(secrethitler): veto propose/accept/reject at 5 fascist"
```

---

## Section 5 — Flow gotchas and integration

### Task 18: Deck reshuffle discipline

**Files:**
- Modify: `server/games/secrethitler/game.py` (if any reshuffle site was missed)
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def test_reshuffle_triggers_when_deck_below_3():
    import random
    random.seed(151)
    g = _make_game(5)
    g.on_start()
    # Drain the deck down to 2 cards, put 15 in discard.
    g.discard = list(g.deck[:15])
    g.deck = list(g.deck[15:])
    assert len(g.deck) == 2
    assert len(g.discard) == 15
    g._ensure_deck_has(3)
    assert len(g.deck) == 17
    assert g.discard == []
```

- [ ] **Step 2: Run test to verify it fails or passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k reshuffle`
Expected: PASS (already implemented in Task 9). If it fails, fix `_ensure_deck_has`.

- [ ] **Step 3: Add a post-enactment reshuffle check**

Rule: reshuffle must be checked *before every draw* and *immediately after each enactment*. The draw checks are already covered by `_ensure_deck_has`. Add one call at the end of `_action_enact_policy` (after the `_check_track_win` call), before returning:

```python
self._ensure_deck_has(3)
```

(Already done in Task 12 — verify the call exists; if missing, add it.)

- [ ] **Step 4: Run tests**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py server/tests/test_secrethitler_powers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "test(secrethitler): reshuffle invariant coverage"
```

---

### Task 19: Chaos enactment skips powers and resets term limits

**Files:**
- Modify: `server/tests/test_secrethitler.py`

Behavior was implemented in Task 9's `_chaos_enact`, but needs explicit tests:

- [ ] **Step 1: Write the failing test**

```python
def test_chaos_skips_powers_even_on_power_slot():
    """Even if chaos enactment lands fascist_policies on a power slot, no power runs."""
    import random
    random.seed(161)
    g = _make_game(9)  # 9p triggers INVESTIGATE at slot 1
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    # Force top-of-deck to be FASCIST so chaos enacts fascist.
    g.deck.insert(0, Policy.FASCIST)
    # Drive 3 failed votes.
    for _ in range(3):
        pres = g._player_at_seat(g.current_president_seat)
        nominee = next(p for p in g.players if p is not pres and p.is_alive)
        g._action_nominate(pres, f"nominate_{nominee.seat}")
        g._action_call_vote(pres, "call_vote")
        for p in g.players:
            if p.is_alive:
                g._action_vote_nein(p, "vote_nein")
    assert g.fascist_policies == 1
    # No power fired — phase must be NOMINATION.
    assert g.phase == Phase.NOMINATION
    assert g.pending_power == Power.NONE


def test_chaos_resets_term_limits():
    import random
    random.seed(162)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.last_elected_president_seat = 2
    g.last_elected_chancellor_seat = 3
    g.election_tracker = 2
    # One more failed vote triggers chaos.
    pres = g._player_at_seat(g.current_president_seat)
    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_nein(p, "vote_nein")
    assert g.election_tracker == 0
    assert g.last_elected_president_seat is None
    assert g.last_elected_chancellor_seat is None
```

- [ ] **Step 2: Run test to verify it passes (or FAIL + fix)**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k chaos`
Expected: PASS if `_chaos_enact` was correctly implemented in Task 9. If a test fails, trace back to `_chaos_enact` and ensure power lookup is skipped and term limits are cleared.

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler.py
git commit -m "test(secrethitler): chaos skips powers and resets term limits"
```

---

### Task 20: Hitler-elected-after-3F win check fires *before* policy draw

**Files:**
- Modify: `server/tests/test_secrethitler.py`

Behavior was implemented in Task 9's `_on_vote_passed`. Add a dedicated test:

- [ ] **Step 1: Write the failing test**

```python
def test_hitler_chancellor_after_3_fascist_wins_immediately():
    import random
    random.seed(171)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.fascist_policies = 3
    pres = g._player_at_seat(g.current_president_seat)
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    if hitler is pres:
        other = next(p for p in g.players if p is not pres)
        other.role, pres.role = pres.role, other.role
        hitler = other
    g._action_nominate(pres, f"nominate_{hitler.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    assert g.phase == Phase.GAME_OVER
    assert g.winner == Party.FASCIST
    assert g.win_reason == "sh-fascists-win-hitler-elected"
    # Crucially, no policies were drawn.
    assert g.president_drawn_policies is None


def test_hitler_chancellor_before_3_fascist_does_not_win():
    import random
    random.seed(172)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    g.fascist_policies = 2
    pres = g._player_at_seat(g.current_president_seat)
    hitler = next(p for p in g.players if p.role == Role.HITLER)
    if hitler is pres:
        other = next(p for p in g.players if p is not pres)
        other.role, pres.role = pres.role, other.role
        hitler = other
    g._action_nominate(pres, f"nominate_{hitler.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    assert g.phase == Phase.PRES_LEGISLATION
```

- [ ] **Step 2: Run test**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k hitler_chancellor`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler.py
git commit -m "test(secrethitler): Hitler-chancellor win fires before legislation"
```

---

### Task 21: Menu focus guard on every phase transition

**Files:**
- Modify: `server/games/secrethitler/game.py`

- [ ] **Step 1: Identify every phase transition site.**

Grep for every assignment to `self.phase = Phase.*`. Each one must be followed by a call to rebuild the on-turn player's menu at position 1.

Context: `rebuild_player_menu(player, *, position=int | None)` is defined on `MenuManagementMixin` (`server/game_utils/menu_management_mixin.py:138`) and is inherited by every `Game` subclass — do **not** add `hasattr` guards, it is always available. Coup uses the blunter `self.rebuild_all_menus()` at phase transitions (`server/games/coup/game.py`, 17 call sites). Secret Hitler uses the finer-grained per-on-turn-player variant with `position=1` because the Actions menu contains persistent items (`view_tracks`, `view_log`) whose relative offset shifts as phase-specific actions appear and disappear; without the explicit position reset, focus strands at the bottom of the menu for screen-reader users. This is a deliberate refinement over Coup's pattern, not a mirror of it.

- [ ] **Step 2: Write the guard**

Add a helper to `SecretHitler`:

```python
def _on_phase_transition(self) -> None:
    """Reset the on-turn player's menu focus to position 1.

    Called after any `self.phase = ...` assignment. Without this, persistent
    items like `view_tracks` shift position as phase-specific actions appear
    and disappear, stranding focus at the bottom.
    """
    # Determine the on-turn player for the current phase.
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
```

Then, after every line that sets `self.phase = Phase.*`, call `self._on_phase_transition()`. Grep the file to find them all; there should be assignments in:
- `on_start` (→ ROLE_REVEAL) — skip; no on-turn player yet.
- `_begin_nomination` (→ NOMINATION)
- `_action_call_vote` (→ VOTING) — VOTING has no single on-turn player; skip.
- `_on_vote_passed` (→ PRES_LEGISLATION)
- `_action_discard_policy` (→ CHAN_LEGISLATION)
- `_action_enact_policy` (→ POWER_RESOLUTION)
- `_end_game` (→ GAME_OVER) — no on-turn player.
- `_action_veto_accept`, `_action_veto_reject`, `_action_execute`, `_action_investigate`, `_action_acknowledge_peek`, `_action_choose_president` — most already call `_begin_nomination` which hits the transition; verify.

- [ ] **Step 3: Add an assertion-based test for the guard**

Append to `server/tests/test_secrethitler.py`:

```python
def test_phase_transition_rebuilds_on_turn_menu_at_position_1(monkeypatch):
    """NOMINATION, PRES_LEGISLATION, CHAN_LEGISLATION, and POWER_RESOLUTION
    transitions must reset the on-turn player's menu focus to position 1."""
    random.seed(401)
    g = _make_game(5)  # helper that seats players + attaches MockUsers
    calls: list[tuple[str, int | None]] = []
    real_rebuild = g.rebuild_player_menu

    def tracker(player, *, position=None):
        calls.append((player.id, position))
        real_rebuild(player, position=position)

    monkeypatch.setattr(g, "rebuild_player_menu", tracker)

    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    # NOMINATION: president's menu rebuilt at position=1
    pres = g._player_at_seat(g.current_president_seat)
    assert (pres.id, 1) in calls
    calls.clear()

    nominee = next(p for p in g.players if p is not pres and p.is_alive)
    g._action_nominate(pres, f"nominate_{nominee.seat}")
    g._action_call_vote(pres, "call_vote")
    for p in g.players:
        if p.is_alive:
            g._action_vote_ja(p, "vote_ja")
    # PRES_LEGISLATION: president's menu rebuilt at position=1
    assert (pres.id, 1) in calls
```

The test asserts the specific `(player_id, 1)` call — no `hasattr` no-op path is tolerated. Add one analogous assertion per targeted phase (CHAN_LEGISLATION, POWER_RESOLUTION) if not already exercised by the single end-to-end flow.

- [ ] **Step 4: Run tests**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py server/tests/test_secrethitler_powers.py -v`
Expected: PASS. If `rebuild_player_menu` raises `AttributeError`, the inheritance chain is wrong — fix it, do not catch the error.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): menu-focus guard on phase transitions"
```

---

## Section 6 — Action sets and keybinds

### Task 22: `create_turn_action_set` and `create_standard_action_set`

**Files:**
- Modify: `server/games/secrethitler/game.py`

- [ ] **Step 1: Implement `create_turn_action_set`.**

Using `server/games/coup/game.py:261-438` as the template, build an `ActionSet` that includes every phase-specific action listed in the spec's "Turn menus by phase" table:

- `acknowledge_role`
- `nominate_<seat>` for seats 0..9 (max 10 players). `show_in_actions_menu=False`.
- `call_vote`, `cancel_nomination`.
- `vote_ja`, `vote_nein`.
- `discard_0`, `discard_1`, `discard_2` (per-choice; `show_in_actions_menu=False`).
- `enact_0`, `enact_1` (per-choice; `show_in_actions_menu=False`).
- `propose_veto`, `veto_accept`, `veto_reject`.
- `investigate_<seat>`, `choose_president_<seat>`, `execute_<seat>` for seats 0..9 (per-choice; `show_in_actions_menu=False`).
- `acknowledge_peek`.

For each per-choice action (`nominate_*`, `discard_*`, `enact_*`, `investigate_*`, `choose_president_*`, `execute_*`), provide matching `is_enabled`, `is_hidden`, and `get_label` helpers. The `is_hidden` helpers return `Visibility.VISIBLE` only in the matching phase and for the correct on-turn player; otherwise `Visibility.HIDDEN`.

Write the helpers following the Coup pattern — do not invent new names. Example for `nominate_<seat>`:

```python
def _is_nominate_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
    if self.phase != Phase.NOMINATION:
        return Visibility.HIDDEN
    sh_player: SecretHitlerPlayer = player  # type: ignore[assignment]
    if sh_player.seat != self.current_president_seat:
        return Visibility.HIDDEN
    if action_id is None:
        return Visibility.VISIBLE
    try:
        target_seat = int(action_id.rsplit("_", 1)[-1])
    except ValueError:
        return Visibility.HIDDEN
    if target_seat not in self._eligible_chancellor_seats():
        return Visibility.HIDDEN
    return Visibility.VISIBLE

def _is_nominate_enabled(self, player: Player, action_id: str | None = None) -> str | None:
    if self._is_nominate_hidden(player, action_id) == Visibility.HIDDEN:
        return "action-not-available"
    return None

def _get_nominate_label(self, player: Player, action_id: str) -> str:
    user = self.get_user(player)
    locale = user.locale if user else "en"
    try:
        target_seat = int(action_id.rsplit("_", 1)[-1])
    except ValueError:
        return "Nominate"
    target = self._player_at_seat(target_seat)
    return Localization.get(locale, "sh-nominate", player=target.name)
```

Repeat the pattern for each per-choice family. Keep each helper short.

- [ ] **Step 2: Implement `create_standard_action_set`.**

Add persistent actions described in the spec: `view_tracks`, `view_government`, `view_players`, `view_my_role`, `view_election_tracker`. Each has `show_in_actions_menu=True`, reads state into `player.user.speak_l(...)`, and is available whenever `self.status == "playing"`.

- [ ] **Step 3: Implement `setup_keybinds` with V/N/R/S bindings.**

Follow `server/games/pig/game.py:194-201` and `server/games/coup/game.py:214-259`:

```python
def setup_keybinds(self) -> None:
    super().setup_keybinds()
    user = None
    if hasattr(self, "host_username") and self.host_username:
        host = self.get_player_by_name(self.host_username)
        if host:
            user = self.get_user(host)
    locale = user.locale if user else "en"

    self.define_keybind("v", Localization.get(locale, "sh-vote-ja"), ["vote_ja", "vote_nein"], state=KeybindState.ACTIVE)
    self.define_keybind("n", Localization.get(locale, "sh-nominate", player=""), ["nominate_0", "nominate_1", "nominate_2", "nominate_3", "nominate_4", "nominate_5", "nominate_6", "nominate_7", "nominate_8", "nominate_9"], state=KeybindState.ACTIVE)
    self.define_keybind("r", Localization.get(locale, "sh-view-my-role"), ["view_my_role"], state=KeybindState.ACTIVE)
```

For `S` = status, override `_action_check_scores` / `_action_check_scores_detailed` / `_is_check_scores_enabled` / `_is_check_scores_detailed_enabled` to show the two-track status (`sh-view-tracks-content`). Read how Coup overrides these near `server/games/coup/game.py:440-501` if unclear.

- [ ] **Step 4: Run tests**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py server/tests/test_secrethitler_powers.py -v`
Expected: PASS — these changes add surfaces, they don't change logic.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/game.py
git commit -m "feat(secrethitler): action sets, keybinds, standard menu items"
```

---

## Section 7 — Bots and CLI

### Task 23: `SecretHitlerBot` — minimal legal action picker

**Files:**
- Modify: `server/games/secrethitler/bot.py`
- Modify: `server/games/secrethitler/game.py` (bot hook)
- Modify: `server/tests/test_secrethitler.py`

Reference: `server/games/coup/bot.py` for structure, `server/game_utils/bot_helper.py` for `BotHelper` usage.

- [ ] **Step 1: Write the failing test**

```python
def test_cli_smoke_5_bots_completes():
    """Bot-only 5-player game must play to GAME_OVER within a tick budget."""
    import random
    random.seed(201)
    g = SecretHitler()
    for i in range(5):
        pid = f"bot{i}"
        name = f"Bot{i}"
        g.players.append(g.create_player(pid, name, is_bot=True))
        g.attach_user(pid, MockUser(name, pid))
    g.on_start()
    # Tick until GAME_OVER or timeout.
    max_ticks = 50_000
    for _ in range(max_ticks):
        g.on_tick()
        if g.phase == Phase.GAME_OVER:
            break
    assert g.phase == Phase.GAME_OVER
    assert g.winner in (Party.LIBERAL, Party.FASCIST)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k cli_smoke`
Expected: FAIL — bots do not act yet.

- [ ] **Step 3: Write minimal implementation**

Overwrite `server/games/secrethitler/bot.py`:

```python
"""Minimal bot for Secret Hitler. Plays legally; does not strategize."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.bot_helper import BotHelper
from .cards import Policy, Role, Power

if TYPE_CHECKING:
    from .game import SecretHitler
    from .player import SecretHitlerPlayer


class SecretHitlerBot(BotHelper):
    """Legal-only bot for Secret Hitler."""

    @classmethod
    def bot_think(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str | None:
        from .game import Phase

        if player.bot_think_ticks > 0:
            player.bot_think_ticks -= 1
            return None

        phase = game.phase

        if phase == Phase.ROLE_REVEAL:
            return "acknowledge_role"

        if phase == Phase.NOMINATION:
            if player.seat != game.current_president_seat:
                return None
            if game.nominee_chancellor_seat is None:
                eligible = game._eligible_chancellor_seats()
                if not eligible:
                    return None
                seat = random.choice(eligible)
                return f"nominate_{seat}"
            # Already nominated — call vote.
            return "call_vote"

        if phase == Phase.VOTING:
            if not player.is_alive:
                return None
            if player.seat in game.votes:
                return None
            return cls._pick_vote(game, player)

        if phase == Phase.PRES_LEGISLATION:
            if player.seat != game.current_president_seat:
                return None
            return cls._pick_discard(game, player)

        if phase == Phase.CHAN_LEGISLATION:
            if player.seat != game.current_chancellor_seat:
                return None
            if game.veto_proposed:
                return None  # waiting on president
            return cls._pick_enact(game, player)

        if phase == Phase.POWER_RESOLUTION:
            if player.seat != game.current_president_seat:
                return None
            return cls._pick_power(game, player)

        return None

    @classmethod
    def _pick_vote(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str:
        from .game import SecretHitlerPlayer as _P

        chancellor = next(
            p for p in game.players
            if isinstance(p, _P) and p.seat == game.nominee_chancellor_seat
        )
        if player.role == Role.HITLER:
            return "vote_ja"
        if player.role == Role.FASCIST:
            # Ja if another fascist or Hitler is on the government.
            pres = next(
                p for p in game.players
                if isinstance(p, _P) and p.seat == game.current_president_seat
            )
            if pres.role in (Role.FASCIST, Role.HITLER) or chancellor.role in (
                Role.FASCIST,
                Role.HITLER,
            ):
                return "vote_ja"
            return "vote_ja" if random.random() < 0.5 else "vote_nein"
        # Liberal
        return "vote_ja" if random.random() < 0.6 else "vote_nein"

    @classmethod
    def _pick_discard(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str:
        want = Policy.LIBERAL if player.role == Role.LIBERAL else Policy.FASCIST
        cards = game.president_drawn_policies or []
        # Discard the card that is NOT our party, if possible.
        unwanted = Policy.FASCIST if want == Policy.LIBERAL else Policy.LIBERAL
        candidates = [i for i, c in enumerate(cards) if c == unwanted]
        if candidates:
            return f"discard_{random.choice(candidates)}"
        return f"discard_{random.randint(0, len(cards) - 1)}"

    @classmethod
    def _pick_enact(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str:
        want = Policy.LIBERAL if player.role == Role.LIBERAL else Policy.FASCIST
        cards = game.chancellor_received_policies or []
        candidates = [i for i, c in enumerate(cards) if c == want]
        if candidates:
            return f"enact_{random.choice(candidates)}"
        return f"enact_{random.randint(0, len(cards) - 1)}"

    @classmethod
    def _pick_power(
        cls, game: "SecretHitler", player: "SecretHitlerPlayer"
    ) -> str | None:
        power = game.pending_power
        alive_others = [
            p.seat for p in game.players
            if p.is_alive and p.seat != player.seat
        ]
        if power == Power.INVESTIGATE:
            eligible = [
                p.seat for p in game.players
                if p.is_alive
                and p.seat != player.seat
                and not p.has_been_investigated
            ]
            if not eligible:
                return None
            return f"investigate_{random.choice(eligible)}"
        if power == Power.SPECIAL_ELECTION:
            if not alive_others:
                return None
            return f"choose_president_{random.choice(alive_others)}"
        if power == Power.POLICY_PEEK:
            return "acknowledge_peek"
        if power == Power.EXECUTION:
            if not alive_others:
                return None
            return f"execute_{random.choice(alive_others)}"
        return None
```

Wire into `on_tick` in `game.py`:

```python
from .bot import SecretHitlerBot

def on_tick(self) -> None:
    super().on_tick()
    if self.paused_for_reconnect or self.phase == Phase.GAME_OVER:
        return
    self.tick += 1

    # Existing vote-timeout logic.
    if (
        self.phase == Phase.NOMINATION
        and self.nominee_chancellor_seat is not None
        and self.vote_call_deadline_tick is not None
        and self.tick >= self.vote_call_deadline_tick
    ):
        pres = self._player_at_seat(self.current_president_seat)
        self._action_call_vote(pres, "call_vote")
        self.vote_call_deadline_tick = None

    # Bot decisions — mirror Coup's pattern.
    for p in self.players:
        if not isinstance(p, SecretHitlerPlayer):
            continue
        if not p.is_bot or not p.is_alive or p.is_spectator:
            continue
        action_id = SecretHitlerBot.bot_think(self, p)
        if action_id:
            self.execute_action(p, action_id)
```

Note: `execute_action` is inherited from `ActionExecutionMixin`. Confirm the exact method name by grepping `server/games/coup/game.py` for how Coup dispatches bot actions — use the identical call.

Respect `bot_think_seconds` from options: set `player.bot_think_ticks = options.bot_think_seconds * 20` after any bot action that should pause the bot.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k cli_smoke`
Expected: PASS.

If the game stalls (no progress within 50k ticks), add a debug print at each phase transition, identify the stuck state, and fix. Typical suspects: missing action handler dispatch for a phase; `bot_think` returning an action ID the `_action_*` rejects; missing eligibility for bots.

- [ ] **Step 5: Commit**

```bash
git add server/games/secrethitler/ server/tests/test_secrethitler.py
git commit -m "feat(secrethitler): minimal legal-play bot"
```

---

### Task 24: CLI simulate smoke for 5..10 bots with `--test-serialization`

**Files:**
- Modify: `server/tests/test_secrethitler.py` (mark as slow, optional)

- [ ] **Step 1: Manual smoke check**

Run:

```bash
cd server && uv run python -m server.cli simulate secrethitler --bots 5
cd server && uv run python -m server.cli simulate secrethitler --bots 7
cd server && uv run python -m server.cli simulate secrethitler --bots 10
```

Each must exit 0 and print a winner. If any hangs, fix (see Task 23's debugging checklist).

- [ ] **Step 2: With serialization**

Run:

```bash
for n in 5 6 7 8 9 10; do
  cd server && uv run python -m server.cli simulate secrethitler --bots $n --test-serialization
done
```

Each must exit 0. `--test-serialization` round-trips state on every tick — any field that does not serialize cleanly will explode here. Most likely culprits: `set` fields (Mashumaro handles these, but confirm `role_ack_seats: set[int]` round-trips), `Phase` / `Power` / `Party` enums (fine as `str, Enum`), `dict[int, bool]` (fine).

If a field fails to serialize, change its representation. Sets may need to become `list[int]` plus a `set()` cast at read time. Do not add custom Mashumaro serializers — the spec says "If a game needs custom save/load code, the state design is wrong."

- [ ] **Step 3: Commit any fixes**

```bash
git add server/games/secrethitler/
git commit -m "fix(secrethitler): serialization cleanup for --test-serialization"
```

---

## Section 8 — Persistence test file

### Task 25: Phase-boundary save/load roundtrips

**Files:**
- Create: `server/tests/test_secrethitler_persistence.py`

- [ ] **Step 1: Write the failing test**

Create `server/tests/test_secrethitler_persistence.py`:

```python
"""Save/load roundtrip tests at every phase boundary."""

import json
import random

import pytest

from server.games.secrethitler.game import SecretHitler, Phase
from server.games.secrethitler.cards import Policy, Role, Power, Party
from server.games.secrethitler.player import SecretHitlerPlayer
from server.core.users.test_user import MockUser


def _make_game(n: int) -> SecretHitler:
    g = SecretHitler()
    for i in range(n):
        pid = f"p{i}"
        name = f"P{i}"
        g.players.append(g.create_player(pid, name))
        g.attach_user(pid, MockUser(name, pid))
    return g


def _roundtrip(g: SecretHitler) -> SecretHitler:
    blob = g.to_json()
    clone = SecretHitler.from_json(blob)
    # Reattach users (runtime-only; not serialized).
    for p in clone.players:
        clone.attach_user(p.id, MockUser(p.name, p.id))
    clone.rebuild_runtime_state()
    return clone


def _assert_identical_state(a: SecretHitler, b: SecretHitler) -> None:
    # Compare the serialized forms.
    assert a.to_json() == b.to_json()


def test_roundtrip_at_role_reveal():
    random.seed(301)
    g = _make_game(5)
    g.on_start()
    assert g.phase == Phase.ROLE_REVEAL
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    # Post-restore: every player can still acknowledge their role and advance.
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
    # Post-restore: president can still call the vote and advance to VOTING.
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
    # Vote two of the five alive players before the roundtrip.
    alive = [p for p in g.players if p.is_alive][:2]
    for p in alive:
        g._action_vote_ja(p, "vote_ja")
    assert g.phase == Phase.VOTING
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    # Post-restore: the two ja votes are preserved and the remaining alive
    # players can still vote. vote_call_deadline_tick must survive restore;
    # if it does not, the tick guard in Task 10 will fire prematurely.
    remaining = [p for p in clone.players if p.is_alive and p.id not in {a.id for a in alive}]
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
    # Post-restore: the three drawn policies survive; president can discard.
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    clone._action_discard_policy(clone_pres, "discard_0")
    assert clone.phase == Phase.CHAN_LEGISLATION
    assert len(clone.chancellor_drawn_policies) == 2


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
    # Post-restore: chancellor can enact; veto_proposed flag stays False.
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
    # Post-restore: pending_power survives and the president can still resolve it.
    assert clone.pending_power == Power.INVESTIGATE
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    target = next(p for p in clone.players if p is not clone_pres and p.is_alive)
    clone._action_investigate(clone_pres, f"investigate_{target.seat}")
    assert clone.pending_power is None


def test_roundtrip_mid_special_election(monkeypatch):
    """Special-election rotation state must survive restore.

    Task 16 introduces `special_election_override` to remember that the next
    normal rotation should resume from a pre-election seat. If that field is
    not preserved, the presidency will rotate off the wrong seat after reload.
    """
    random.seed(307)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    # Force the special-election branch: three fascist policies enacted
    # triggers CALL_SPECIAL_ELECTION at 7p (per spec).
    g.fascist_policies = 3
    pres = g._player_at_seat(g.current_president_seat)
    original_seat = pres.seat
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
    assert g.pending_power == Power.CALL_SPECIAL_ELECTION
    clone = _roundtrip(g)
    _assert_identical_state(g, clone)
    # Post-restore: president chooses a special-election successor, plays out
    # one round, and the *next* president must be (original_seat + 1) % 7, not
    # the successor's seat + 1.
    clone_pres = clone._player_at_seat(clone.current_president_seat)
    successor = next(
        p for p in clone.players
        if p is not clone_pres and p.is_alive and p.seat != clone_pres.seat
    )
    clone._action_choose_president(clone_pres, f"choose_president_{successor.seat}")
    assert clone.special_election_override is not None, (
        "special_election_override must be set post-restore for rotation to resume correctly"
    )
```

- [ ] **Step 2: Run tests**

Run: `cd server && uv run pytest server/tests/test_secrethitler_persistence.py -v`
Expected: PASS. Any failure points to one of three bugs: (1) a non-serializable field (fix the representation in `game.py` — change sets to lists, etc.); (2) a transient coordination field (`vote_call_deadline_tick`, `policy_peek_cards`, `veto_proposed`, `special_election_override`) that is not serialized or not rebuilt in `rebuild_runtime_state()`; (3) a menu/action registration that depends on setup order and does not survive `from_json` + `rebuild_runtime_state` + `setup_keybinds`. All three are failure modes specific to restore-and-continue, which is why post-restore actions are driven in each test — bare JSON equality would miss them.

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler_persistence.py
git commit -m "test(secrethitler): save/load roundtrip at every phase boundary"
```

---

## Section 9 — Hidden-info discipline and spectator-after-execution

### Task 26: Hidden-info leakage test

**Files:**
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
def test_hidden_info_does_not_leak_to_public_buffer():
    """
    Role identity, drawn policies, peeked policies, and investigate results
    must never land on the public table buffer for players not entitled to them.

    Implementation: walk every player's MockUser.spoken_l history. For every
    message tagged with buffer='table', the message key must NOT be one of
    the personal-only keys unless the recipient is the entitled player.
    """
    import random
    random.seed(401)
    g = _make_game(9)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")

    PERSONAL_ONLY_KEYS = {
        "sh-you-are-liberal",
        "sh-you-are-fascist",
        "sh-you-are-hitler",
        "sh-fascist-teammates",
        "sh-hitler-knows-teammates",
        "sh-your-policies",
        "sh-your-policies-chancellor",
        "sh-you-see-party",
        "sh-you-peek",
        "sh-you-voted-ja",
        "sh-you-voted-nein",
    }

    # For each player, check: any personal-only key recorded must have been
    # addressed to that player, never to someone else.
    # MockUser.spoken_l entries are (key, buffer, kwargs)-ish; adjust
    # per MockUser's recorded shape.
    for p in g.players:
        u = g.get_user(p)
        entries = getattr(u, "spoken_l", [])
        for entry in entries:
            key = entry[0] if isinstance(entry, tuple) else entry
            if not isinstance(key, str):
                continue
            if key in PERSONAL_ONLY_KEYS:
                # This player must actually have been entitled.
                # (For example: only fascists/hitler see sh-fascist-teammates.)
                if key in ("sh-you-are-fascist", "sh-fascist-teammates") and p.role != Role.FASCIST:
                    # Hitler at 5-6p can also see sh-fascist-teammates variant,
                    # but we use sh-hitler-knows-teammates for that case.
                    pytest.fail(f"{p.name} received fascist-only key {key}")
                if key == "sh-you-are-hitler" and p.role != Role.HITLER:
                    pytest.fail(f"{p.name} received Hitler-only key")
                if key == "sh-hitler-knows-teammates" and p.role != Role.HITLER:
                    pytest.fail(f"{p.name} received Hitler-teammates key")
                if key == "sh-you-are-liberal" and p.role != Role.LIBERAL:
                    pytest.fail(f"{p.name} received Liberal-only key")
```

Adjust per MockUser's actual recording shape (confirmed from reading `server/core/users/test_user.py`).

- [ ] **Step 2: Run test**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k hidden_info`
Expected: PASS. If FAIL, the bug is in one of the `_action_*` handlers — it's broadcasting a personal key instead of using `user.speak_l`.

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler.py
git commit -m "test(secrethitler): hidden-info discipline across the table buffer"
```

---

### Task 27: Executed players are limited spectators

**Files:**
- Modify: `server/games/secrethitler/game.py` (verify behavior is correct)
- Modify: `server/tests/test_secrethitler.py`

The spec says an executed player loses voting/nominating/enacting rights but remains seated and continues to see public announcements. `is_alive=False` already excludes them from turn menus. Add explicit test coverage.

- [ ] **Step 1: Write the failing test**

```python
def test_executed_player_still_receives_public_broadcasts():
    import random
    random.seed(501)
    g = _make_game(7)
    g.on_start()
    for p in g.players:
        g._action_acknowledge_role(p, "acknowledge_role")
    victim = next(p for p in g.players if p.role == Role.LIBERAL)
    victim.is_alive = False
    before = len(getattr(g.get_user(victim), "spoken_l", []))
    g.broadcast_l("sh-president-is", player="Someone")
    after = len(getattr(g.get_user(victim), "spoken_l", []))
    assert after > before
```

- [ ] **Step 2: Run test**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k executed_player_still`
Expected: PASS (no code change needed).

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler.py
git commit -m "test(secrethitler): executed players remain on public buffer"
```

---

## Section 10 — Play tests and final smoke

### Task 28: Play tests — each win path reachable with seeded RNG

**Files:**
- Modify: `server/tests/test_secrethitler.py`

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.parametrize("n", [5, 7, 10])
def test_full_bot_game_completes(n):
    import random
    random.seed(600 + n)
    g = SecretHitler()
    for i in range(n):
        pid = f"b{i}"
        name = f"B{i}"
        g.players.append(g.create_player(pid, name, is_bot=True))
        g.attach_user(pid, MockUser(name, pid))
    g.on_start()
    for _ in range(100_000):
        g.on_tick()
        if g.phase == Phase.GAME_OVER:
            break
    assert g.phase == Phase.GAME_OVER
    assert g.winner in (Party.LIBERAL, Party.FASCIST)
```

- [ ] **Step 2: Run test**

Run: `cd server && uv run pytest server/tests/test_secrethitler.py -v -k full_bot_game`
Expected: PASS for all three seeds. If a seed stalls, try a few other seeds to confirm the bot is healthy; if multiple stall, there's a latent bug (most commonly: a phase with no eligible action, meaning eligibility computation is wrong).

- [ ] **Step 3: Commit**

```bash
git add server/tests/test_secrethitler.py
git commit -m "test(secrethitler): full 5/7/10-bot play tests"
```

---

### Task 29: Final CLI smoke with `--test-serialization`

**Files:** none (verification only)

- [ ] **Step 1: Run CLI sim for every supported size**

```bash
for n in 5 6 7 8 9 10; do
  echo "=== $n players ==="
  cd server && uv run python -m server.cli simulate secrethitler --bots $n --test-serialization
done
```

All must exit 0. Confirm output includes a winner and the final roles broadcast.

- [ ] **Step 2: Run the full game-specific test set**

```bash
cd server && uv run pytest server/tests/test_secrethitler.py server/tests/test_secrethitler_powers.py server/tests/test_secrethitler_persistence.py -v
```

Expected: all PASS. If anything fails, fix before considering the work complete.

- [ ] **Step 3: Run the locale-completeness check**

```bash
cd server && uv run pytest server/tests/test_locale_completeness.py -v
```

Expected: PASS. The `check-locales` pre-commit hook will flag any non-English file that lacks required parity; translators address that. This run verifies the English file parses cleanly.

- [ ] **Step 4: Final commit (only if fixes were applied)**

```bash
git add -u
git commit -m "test(secrethitler): final smoke verification"
```

---

## Section 11 — Documentation touch-up

### Task 30: Index the new game

**Files:**
- Modify: `server/games/CLAUDE.md` (add `secrethitler/` to the subdirectory table)
- Modify: `server/tests/CLAUDE.md` (add the three new test files)

- [ ] **Step 1: Edit `server/games/CLAUDE.md`**

Add one row to the game-subdirectories table in alphabetical order:

```markdown
| `secrethitler/` | Secret Hitler |
```

- [ ] **Step 2: Edit `server/tests/CLAUDE.md` (if it enumerates per-game test files)**

If the file lists per-game tests, add rows for `test_secrethitler.py`, `test_secrethitler_powers.py`, `test_secrethitler_persistence.py`. If it uses a `test_*.py` glob line, no edit is needed — verify by reading the current content first.

- [ ] **Step 3: Commit**

```bash
git add server/games/CLAUDE.md server/tests/CLAUDE.md
git commit -m "docs(secrethitler): index new game and test files"
```

---

## Self-review checklist

Before declaring done, walk the spec top-to-bottom and confirm each requirement maps to a task:

- Scope — canonical base, 5–10 players: Tasks 2, 5 (role counts), 29 (smoke).
- Pre-vote discussion gate + timeout: Tasks 9, 10.
- Bots minimal: Tasks 23, 28.
- Theme canonical names: Task 4 (locale file).
- Dead players limited spectators: Tasks 15, 27.
- Disconnection pause: covered by `paused_for_reconnect` field and tick guard (Tasks 5, 10), with restore-and-continue coverage at every interactive phase via Task 25 (which exercises the real `from_json` + `rebuild_runtime_state` path — the only restore path the server has; see `server/core/server.py:838` and `_restore_saved_table` at line 2917). Scope decision: there is **no existing house pattern** for per-phase disconnect/forfeit handling in other games — a codebase grep for `disconnect|reconnect|forfeit|paused_for_reconnect` returns zero hits in `server/games/` and `server/game_utils/`. Disconnect/forfeit UX is cross-cutting infrastructure (it belongs in `server/core/tables/` or a framework-level mixin, alongside the network layer that actually knows about dropped connections). Introducing a Secret-Hitler-only per-phase disconnect matrix here would prejudice that infrastructure design and duplicate work across 23 games. `paused_for_reconnect` is explicitly a point fix for the 50ms-tick interaction (the one place a new game can get disconnect wrong on its own), and Task 25's post-restore action drive proves the game is safe for the crash-recovery path. Any further disconnect work for Secret Hitler belongs in a separate plan that also addresses Coup, Poker, Scopa, and the rest.
- Role counts by player, Hitler-knows-fascists at 5–6: Tasks 2, 5, 6.
- Policy deck composition + reshuffle: Tasks 2, 9, 18.
- Fascist-track powers by player count: Tasks 2, 12, 13–16.
- Term limits with ≤5 alive exception: Task 8.
- Election tracker chaos: Tasks 9, 19.
- Win conditions (all four): Tasks 12, 15, 20.
- Veto at 5F, both must agree, accepted veto = discard + tracker: Task 17.
- Module layout: whole plan.
- State representation: Tasks 3, 5.
- Phase state machine: Tasks 7–17.
- Action system (turn + standard menus + keybinds): Task 22.
- Menu focus guard: Task 21.
- Messaging hidden-info rule: Task 26.
- Bots behavior per spec table: Task 23.
- Options (vote timeout, bot think): Task 3.
- Testing strategy:
  - CLI smoke: Tasks 23, 24, 29.
  - Role dealing: Tasks 5, 6.
  - Term limits: Task 8.
  - Deck reshuffle: Tasks 9, 18.
  - Win conditions: Tasks 12, 15, 20.
  - Special-election rotation: Task 16.
  - Chaos enactment: Task 19.
  - Hidden-info discipline: Task 26.
  - Persistence per phase: Task 25.
  - Play tests: Task 28.

Known risks from spec:
- Hidden-info leakage in logs: Task 26.
- Menu focus: Task 21.
- Disconnect + tick pause interaction: Task 10.
- Serialization of `pending_power`: Task 25 (roundtrip at POWER_RESOLUTION) + Task 24 (tick-level serialization).
- Packet schema: no changes expected; if they occur, Task instructions in the preamble cover regen.
