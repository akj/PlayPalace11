# Secret Hitler — Design Spec

Date: 2026-04-23
Author: Andrew (with Claude brainstorming assist)
Status: Draft for implementation

## Overview

Add Secret Hitler to PlayPalace v11 as a new game under `server/games/secrethitler/`. Canonical base rules, 5–10 players, accessibility-first (screen-reader primary audience), minimal bots for testing. Shape mirrors Coup (hidden roles, bluffing, public/private message split) with one extra module (`powers.py`) for the five executive powers.

The physical game of Secret Hitler is a social-deduction legislative game. Players are secretly divided into Liberals (majority) and Fascists (minority, including a special Hitler role). Each round, a rotating president nominates a chancellor; the table votes Ja/Nein; on a passed vote, three policies are drawn and the chancellor enacts one. Five Liberal policies enacted → Liberals win; six Fascist policies → Fascists win; executing Hitler → Liberals win; electing Hitler chancellor after three Fascist policies are in play → Fascists win.

## Design decisions (from brainstorming)

### Scope — canonical base game only

- 5–10 players.
- Full set of executive powers.
- No expansions, no rewrite cards, no Secret Hitler XL roles in v1.

### Pacing / discussion — president-gated pre-vote window

The physical game lives on table talk between nomination and vote. Most online implementations let the game advance purely on required actions and rely on organic pauses plus chat. Our hybrid:

- **Pre-vote discussion gate.** After the president nominates, the menu shows only `call_vote` (to the president) and nothing actionable for other players until then. Other players can chat but cannot yet vote. The president presses "call for vote" when they judge discussion is done.
- **Safety timeout.** A configurable `president_vote_timeout_seconds` (default 180) auto-calls the vote if the president stalls.
- **Everywhere else.** After vote reveal, after policy enactment, after an executive power completes, game advances immediately to the next required action. The next president's nomination phase naturally absorbs reaction and discussion time.
- **Rationale.** One explicit gate rather than per-event "ready" checks; maps to the physical game's floor-control; avoids per-event ceremony that compounds with screen readers at 5–10 players.

### Bots — minimal, for testing only

Bots exist so the CLI `simulate` harness can run and so small human groups can fill to 5. They play legally and complete games. They do not need to be hard to beat. Sophistication is explicitly deferred.

### Theme — canonical names

Use the published names verbatim: Liberals, Fascists, Hitler, Ja!, Nein!. No re-theme and no toggle. Keeps the locale surface small and matches player expectations from the physical game. Re-theming can be added later as an option if desired.

### Dead (executed) players — limited spectators

After execution a player loses voting/nomination/legislation rights but remains at the table. They see only public announcements from that point forward — no new hidden info is granted to them, and their pre-execution knowledge of their own role does not change. Matches standard online implementations.

### Disconnection — pause with manual forfeit escape hatch

On disconnect, set `paused_for_reconnect=True` on the game; tick skips all phase transitions. Hidden state is preserved. On reconnect the returning player is re-shown their role and the current game state. If the player does not return, the table owner can forfeit them — treated as an execution (`is_alive=False`), which resolves the Hitler-killed win condition if applicable.

### Rules — published rulebook, no house rules

- Role counts by player: 5p (3L/1F/H), 6p (4L/1F/H), 7p (4L/2F/H), 8p (5L/2F/H), 9p (5L/3F/H), 10p (6L/3F/H).
- Hitler knows the fascists at 5–6 players; does not at 7–10.
- Policy deck: 6 Liberal + 11 Fascist; reshuffle (deck + discard) when fewer than 3 cards remain, then clear discard.
- Executive powers per fascist-track slot, per player-count bucket (5–6 / 7–8 / 9–10).
- Term limits: previous president and previous chancellor cannot be nominated. When ≤5 alive, only the previous chancellor is restricted.
- Election tracker: 3 failed votes → top policy enacts automatically, tracker resets to 0, term limits reset, no executive power triggers.
- Win conditions: 5 Liberal policies, 6 Fascist policies, Hitler executed, or Hitler elected Chancellor after 3+ Fascist policies already enacted.
- Veto: unlocks at 5 fascist policies; president and chancellor must both agree; an accepted veto discards both policies and advances the tracker.

## Architecture

### Module layout

```
server/games/secrethitler/
├── __init__.py
├── game.py       # SecretHitler(Game), phase dispatch, nomination/voting/legislation, win checks
├── powers.py     # investigate_loyalty, special_election, policy_peek, execution, veto resolution
├── cards.py      # Policy/Role/Party/Power enums, ROLE_COUNTS, FASCIST_TRACK_POWERS, deck composition
├── player.py     # SecretHitlerPlayer(Player), SecretHitlerOptions(GameOptions)
└── bot.py        # SecretHitlerBot — minimal action picker
```

Plus `server/locales/en/secrethitler.ftl` and unit/play/persistence tests under `server/tests/`.

Registration: `@register_game` on `SecretHitler(Game)`, exactly like `@register_game` on `CoupGame`. Adds a new `GameRegistry` entry keyed by `"secrethitler"`.

### Why this split

Coup (1657-line `game.py`) is the proven house pattern for hidden-role games. Extracting `powers.py` is the one additional split the code asks for — the five executive powers are self-contained transitions each threading 20–70 lines of rule-edge logic, and they're the highest-bug-density surface in the game. Keeping them isolated lets tests target them directly and keeps `game.py` projected at 1000–1200 lines. If `game.py` grows past ~1200 during implementation, consider a second extraction (`legislation.py`) — but only with evidence, not speculation.

### State representation

All game state is a set of fields on the `SecretHitler(Game)` dataclass (not a nested `GameState`), matching the house pattern (Coup, Pig, etc.). All fields are dataclasses / primitives / enums so Mashumaro round-trips cleanly; `--test-serialization` will verify this on every tick during CLI simulation.

**`SecretHitlerPlayer(Player)`** extends the base `Player` dataclass:

```python
@dataclass
class SecretHitlerPlayer(Player):
    seat: int = 0                         # stable 0-based seat; rotation uses this
    role: Role = Role.LIBERAL             # LIBERAL / FASCIST / HITLER
    is_alive: bool = True                 # False after execution or forfeit
    has_been_investigated: bool = False   # can only be investigated once
    connected: bool = True                # False during disconnection pause
```

Inherited from base: `id`, `name`, `is_bot`, `is_spectator`, `bot_think_ticks`, etc. Note `is_spectator` on the base class refers to pre-existing spectators, not executed players — keep `is_alive` as a distinct field for executed semantics.

**`SecretHitlerOptions(GameOptions)`** uses the declarative `option_field` / `IntOption` helpers:

```python
president_vote_timeout_seconds: int      # default 180, min 30,  max 600
bot_think_seconds: int                   # default 2,   min 0,   max 10
```

**Fields on `SecretHitler(Game)`** (selected — full list materializes at implementation):

```python
phase: Phase = Phase.LOBBY
players: list[SecretHitlerPlayer]
options: SecretHitlerOptions

# Deck
deck: list[Policy]
discard: list[Policy]

# Track counts
liberal_policies: int = 0
fascist_policies: int = 0
election_tracker: int = 0

# Rotation
president_seat: int = 0
special_election_override: int | None = None     # one-shot; consumed on use
current_president_seat: int | None = None
current_chancellor_seat: int | None = None
last_elected_president_seat: int | None = None
last_elected_chancellor_seat: int | None = None

# Nomination / voting
nominee_chancellor_seat: int | None = None
votes: dict[int, bool] = field(default_factory=dict)   # seat -> Ja(True)/Nein(False)
vote_call_deadline_tick: int | None = None

# Legislation
president_drawn_policies: list[Policy] | None = None   # 3 cards
chancellor_received_policies: list[Policy] | None = None # 2 cards
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
win_reason: str | None = None   # locale key
```

### Phase state machine

A single `Phase` enum drives dispatch. Transitions:

```
LOBBY ──[start]──▶ ROLE_REVEAL ──[all ack]──▶ NOMINATION

NOMINATION ──[president picks chancellor]──▶ (still NOMINATION, menu changes to call_vote)
NOMINATION ──[president calls vote OR timeout]──▶ VOTING

VOTING ──[all alive voted]──▶ tally
  passed  ──▶ check Hitler-after-3F win
              ├─ win: GAME_OVER
              └─ continue: PRES_LEGISLATION
  failed  ──▶ election_tracker += 1
              ├─ tracker == 3: auto-enact top policy, reset tracker, reset term limits, check win, → NOMINATION
              └─ else:         → NOMINATION (next president)

PRES_LEGISLATION ──[president discards 1 of 3]──▶ CHAN_LEGISLATION

CHAN_LEGISLATION
  ├─ [chancellor enacts 1 of 2]──▶ update track, check win, resolve power slot, → POWER_RESOLUTION or NOMINATION
  └─ [chancellor proposes veto (5F only)]──▶ president veto_accept / veto_reject
            accept: both policies discarded, tracker += 1 (chaos if 3), → NOMINATION
            reject: chancellor menu re-opens with enact_* only

POWER_RESOLUTION ──[power completes]──▶ check win ──▶ NOMINATION

GAME_OVER: terminal
```

### Action system

Follows Coup's pattern: `create_turn_action_set(player)` builds the phase-appropriate turn menu; `create_standard_action_set(player)` builds the persistent side menu. Action handlers are `_action_<name>(player, action_id)` methods. Per-choice actions (nominate_<seat>, discard_<i>, enact_<i>, etc.) use `show_in_actions_menu=False` so they don't pollute the persistent Actions menu.

**Turn menus by phase:**

| Phase | On-turn player | Menu items |
| --- | --- | --- |
| LOBBY | — | handled by `LobbyActionsMixin` |
| ROLE_REVEAL | all alive | `acknowledge_role` |
| NOMINATION (step 1) | current president | `nominate_<seat>` per eligible player |
| NOMINATION (step 2) | current president | `call_vote`, `cancel_nomination` |
| VOTING | all alive | `vote_ja`, `vote_nein` |
| PRES_LEGISLATION | president | `discard_<0..2>` for the three drawn policies |
| CHAN_LEGISLATION (normal) | chancellor | `enact_<0..1>` plus (when 5F) `propose_veto` |
| CHAN_LEGISLATION (veto proposed) | president | `veto_accept`, `veto_reject` |
| POWER_RESOLUTION / INVESTIGATE | president | `investigate_<seat>` per eligible player |
| POWER_RESOLUTION / SPECIAL_ELECTION | president | `choose_president_<seat>` per eligible player |
| POWER_RESOLUTION / POLICY_PEEK | president | `acknowledge_peek` |
| POWER_RESOLUTION / EXECUTION | president | `execute_<seat>` per eligible player |
| GAME_OVER | — | handled by `GameResultMixin` |

**Persistent (standard) actions** — available to every player at all times:

- `view_tracks` — "Liberal track: N of 5. Fascist track: M of 6."
- `view_government` — current president/chancellor/last-elected pair.
- `view_players` — roster with alive/executed status and seat order.
- `view_my_role` — re-reads the player's own role (and known-fascists if applicable).
- `view_election_tracker` — "Failed elections: N of 3."
- standard global actions provided by mixins.

**Keybinds.** `V` = vote (context-sensitive Ja/Nein), `N` = nominate target list, `R` = view my role, `S` = status (custom readout — per CLAUDE.md, override `_action_check_scores`, `_action_check_scores_detailed`, `_is_check_scores_enabled`, `_is_check_scores_detailed_enabled`).

**Menu focus guard.** At every phase transition, call `self.rebuild_player_menu(player, position=1)` for the on-turn player. This is the fix for the menu-focus bug documented in `game_development_guide.md` — persistent items like `view_tracks` shift position as phase-specific actions appear and disappear, stranding focus at the bottom without it.

## Messaging & locale strategy

Locale file: `server/locales/en/secrethitler.ftl`. Written before the game code — it is the implementation plan. Only the English file is authored in this PR; the `check-locales` pre-commit hook enforces parity across 29 languages and translators fill the rest.

**Broadcast discipline:**

- `broadcast_l` / `broadcast_personal_l` — table buffer; public announcements and narration of table state.
- `user.speak_l` — personal speech buffer; used only for direct command responses (e.g. "view my role", "view tracks").
- **Hidden-info rule.** Role identity, drawn/peeked policies, the specific contents of an individual vote before the reveal, and power-result details (e.g. investigated loyalty) are **only** delivered via `broadcast_personal_l` to the entitled players. They never appear on the public table buffer. This is a test invariant (see Testing below).

**Message groups** (counts are approximate — final locale file will nail these down):

1. **Role reveal** (private): `sh-you-are-liberal`, `sh-you-are-fascist`, `sh-you-are-hitler`, `sh-fascist-teammates` (Fluent select on player count for Hitler-included-or-not variants), `sh-hitler-knows-teammates` (5–6p only).
2. **Nomination** (public + president-personal): `sh-president-is`, `sh-you-are-president`, `sh-president-nominates`, `sh-president-can-call-vote`, `sh-vote-timeout-approaching`.
3. **Voting** (public for tallies, personal confirmations): `sh-voting-open`, `sh-you-voted-ja`, `sh-you-voted-nein`, `sh-players-still-voting`, `sh-vote-result`, `sh-vote-roll-call` (per-player reveal).
4. **Legislation** (policy content private): `sh-president-draws`, `sh-your-policies` (personal), `sh-president-discards` (public, no identity of card), `sh-chancellor-receives`, `sh-your-policies-chancellor` (personal), `sh-chancellor-enacts` (with Fluent select on policy party + running track totals).
5. **Election tracker / chaos**: `sh-tracker-advances`, `sh-chaos-top-policy`.
6. **Executive powers**: `sh-power-investigate` + `sh-you-see-party` (personal), `sh-power-special-election`, `sh-power-policy-peek` + `sh-you-peek` (personal), `sh-power-execution`.
7. **Veto**: `sh-chancellor-proposes-veto`, `sh-president-accepts-veto`, `sh-president-rejects-veto`.
8. **Win conditions**: `sh-liberals-win-policies`, `sh-liberals-win-execution`, `sh-fascists-win-policies`, `sh-fascists-win-hitler-elected`, `sh-final-roles`.

Estimated surface: 55–70 strings.

## Executive powers — detailed

Power unlock table (`cards.py`):

| Fascist policies enacted | 5–6 players | 7–8 players | 9–10 players |
| --- | --- | --- | --- |
| 1 | — | — | Investigate |
| 2 | — | Investigate | Investigate |
| 3 | Policy peek | Special election | Special election |
| 4 | Execution | Execution | Execution |
| 5 | Execution (+ veto unlocks) | Execution (+ veto unlocks) | Execution (+ veto unlocks) |
| 6 | (fascists win) | (fascists win) | (fascists win) |

**Per-power transitions:**

- **Investigate Loyalty.** President picks any alive player with `has_been_investigated=False`. President gets a personal message with the target's *party* (Liberal or Fascist — Hitler shows as Fascist). Target's `has_been_investigated` flips to True. Public announcement reveals who was investigated, not the result.
- **Special Election.** President picks any alive player other than themselves. Sets `special_election_override = target_seat`. Phase returns to NOMINATION with the override acting as the next president. After that government resolves (pass or fail), rotation resumes from the seat after the *original* seat-based president, not after the special electee. (Common bug source — has a dedicated unit test.)
- **Policy Peek.** President gets a personal message listing the top three policies in `deck`. No modification to the deck. Public announcement says the president peeked.
- **Execution.** President picks any alive player. Target's `is_alive=False`. If the target was Hitler: immediate Liberal win, short-circuit to GAME_OVER. Otherwise advance to NOMINATION.
- **Veto.** Unlocked when `fascist_policies == 5`. Inside CHAN_LEGISLATION, chancellor menu adds `propose_veto`. On propose: president menu offers `veto_accept` / `veto_reject`. On accept: both policies discarded, `election_tracker += 1` (which can trigger chaos). On reject: chancellor menu re-opens with `enact_*` only (no re-veto allowed this round).

**Flow gotchas (first-class tested):**

1. **Deck reshuffle.** Triggered when `len(deck) < 3`; combine `deck + discard`, shuffle, clear discard. Check *before* every draw and immediately after each enactment.
2. **Chaos enactment skips powers.** No executive power triggers on a chaos-enacted policy, even if the policy lands on a power slot.
3. **Chaos resets term limits.** Clear `last_elected_president_seat` and `last_elected_chancellor_seat` after a chaos enactment.
4. **Successful government locks term limits.** After a passed vote + enactment, set `last_elected_*` to the just-finished pair. Failed votes do not change these.
5. **Hitler-elected-chancellor win check.** Evaluated only when `fascist_policies >= 3` and the just-passed government's chancellor is Hitler. Check fires at vote-pass time, *before* drawing policies.
6. **Eligibility lists.** Nomination excludes dead players and term-limited players (with the ≤5 alive exception). Investigate excludes dead and already-investigated. Execute/special-election exclude dead (and self for special election).
7. **Election tracker only advances on failed vote or accepted veto.** Chaos resets it to 0.

## Bots

`bot.py` with `SecretHitlerBot` class, mirroring `CoupBot`. Uses `BotHelper` and `bot_think_ticks` for standard bot timing. Deliberately unsophisticated — goal is legal, game-completing play for CLI simulation and small-table fill, not challenge.

| Choice | Bot behavior |
| --- | --- |
| Nominate chancellor | Uniform random from eligible. |
| Call vote | Immediately — bot presidents skip the discussion window. |
| Vote Ja/Nein | Fascist bots: Ja if the government contains another fascist or Hitler, else Nein with p=0.5. Liberal bots: Ja with p=0.6, Nein otherwise. Hitler: always Ja. |
| President discard | Fascist/Hitler: discard a Liberal policy if possible. Liberal: discard a Fascist policy if possible. Ties broken randomly. |
| Chancellor enact | Same party preference as president discard. |
| Investigate target | Uniform random from eligible. |
| Special election target | Uniform random from eligible, excluding self. |
| Execute target | Uniform random from alive non-self; no suspicion modeling. |
| Policy peek | Instant acknowledge. |
| Veto propose (chancellor) | Never. |
| Veto accept/reject (president) | Always accept. |

Not implemented: suspicion tracking, memory of past votes, chat claims, bluffing. Estimated ~150–200 lines. Easy to swap for smarter bots later without changing `game.py`.

## Options & configuration

```python
@dataclass
class SecretHitlerOptions(GameOptions):
    president_vote_timeout_seconds: int  # default 180, min 30, max 600
    bot_think_seconds: int               # default 2, min 0, max 10
```

Not options: player count (driven by seating), number of bots (covered by `LobbyActionsMixin`), veto (always on — rulebook mechanic, not a variant).

`start_game()` refuses to start unless `5 <= len(players) <= 10` at the moment of start (before any executions can have happened), with a localized error message.

## Testing strategy

**Test files:**

- `server/tests/test_secrethitler.py` — unit + play tests.
- `server/tests/test_secrethitler_powers.py` — focused tests for the five powers and veto.
- `server/tests/test_secrethitler_persistence.py` — save/load roundtrip at every phase boundary.

**Required coverage:**

1. **CLI smoke.** `python -m server.cli simulate secrethitler --bots N --test-serialization` completes without error for N in 5..10. `--test-serialization` saves/restores state on every tick — primary serialization guarantee.
2. **Role dealing.** Correct role counts at each player count; Hitler knows fascists at 5–6 only; fascists always know each other and Hitler.
3. **Term limits.** Previous pres/chancellor blocked; ≤5 alive drops the president restriction; chaos resets term limits.
4. **Deck reshuffle.** Triggers when `<3` cards remain; combines deck+discard; clears discard.
5. **Win conditions.** All four reachable: 5 liberal policies, 6 fascist policies, Hitler executed, Hitler elected chancellor after ≥3 fascist policies.
6. **Special-election rotation.** After the electee's government resolves, rotation resumes from seat-after-original-president.
7. **Chaos enactment.** 3rd failed vote auto-enacts top policy, skips powers, resets tracker and term limits.
8. **Hidden-info discipline.** Assert roles, drawn policies, peeked policies, and investigation results never appear on public table buffers — only in personal buffers of entitled players.
9. **Persistence per phase.** Save and restore mid-nomination, mid-vote, mid-PRES_LEGISLATION, mid-CHAN_LEGISLATION, mid-POWER_RESOLUTION; hidden state and eligibility lists survive byte-identical.
10. **Play tests.** Full games of 5, 7, and 10 bots complete; each win path reachable with seeded RNG.

## Known risks

- **Hidden-info leakage in logs.** Server logs or packet traces must not include role names or drawn policies for players not entitled to them. The hidden-info-discipline test is the guard.
- **Menu focus bug.** `rebuild_player_menu(player, position=1)` required at every phase transition — easy to miss in POWER_RESOLUTION branches. Tested by walking arrow-key focus across transitions.
- **Disconnect + tick pause interaction.** The president vote-timeout countdown must respect `paused_for_reconnect`. Test: pause mid-timeout, reconnect, verify timer resumes rather than expires.
- **Serialization of `pending_power`.** Enum + optional target fields must round-trip cleanly. Covered by `--test-serialization`, but flag-worthy during review.
- **Packet schema.** No new packet types expected — all state fits the existing game-state envelope. If a new packet does emerge, `regen-packet-schema` pre-commit hook will force `server/packet_schema.json` and `clients/desktop/packet_schema.json` regen and sync.

## Out of scope for v1

- Smarter bots (suspicion tracking, claims, bluffing).
- Re-themed name sets.
- Expansions (Secret Hitler XL roles, rewrite cards, etc.).
- Veto variants or house rules.
- A dedicated spectator chat separation for executed players.

These may be added in follow-up specs once v1 ships.
