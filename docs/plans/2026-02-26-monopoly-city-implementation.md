# Monopoly City Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement full-fidelity `city` preset behavior from anchor edition `monopoly-1790`, including complete winner-loop handling in the first pass.

**Architecture:** Keep `MonopolyGame` as the single runtime entrypoint and add City-specific modules for profile resolution, board/rules data, and deterministic City engine behavior. Route City-only mechanics through preset-guarded hooks so non-City presets remain unchanged. Use anchor notes as the sole rules source (`anchor-first`).

**Tech Stack:** Python 3.13, dataclasses, pytest, existing Monopoly engine (`server/games/monopoly/game.py`), curated Monopoly catalog JSON, Fluent localization files.

---

### Task 1: Capture Anchor Rules Notes For `monopoly-1790`

**Files:**
- Create: `docs/plans/2026-02-26-monopoly-city-anchor-notes.md`
- Read: `server/games/monopoly/catalog/monopoly_manual_variants_curated.json`

**Step 1: Create a structured notes template**

```markdown
# Monopoly City Anchor Notes (monopoly-1790)

## Source
- Edition ID: monopoly-1790
- Policy: anchor-first
- Manual URL(s): ...

## Rules Extract
- Setup
- Turn flow
- Space/action effects
- Payment/economy rules
- Win condition
- Tie-break rules

## Normalized Rule Table
| Rule Key | Anchor Text | Normalized Value | Confidence |
|---|---|---|---|
```

**Step 2: Verify anchor manual rows exist in curated catalog**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path('server/games/monopoly/catalog/monopoly_manual_variants_curated.json').read_text())
hits = [r for r in rows if r.get('edition_id') == 'monopoly-1790']
print(len(hits))
print(sorted({r.get('locale') for r in hits}))
print(next((r.get('pdf_url') for r in hits if r.get('locale') == 'en-us'), ''))
PY
```

Expected: at least one row, includes `en-us`, prints City PDF URL.

**Step 3: Populate anchor notes from the PDF/manual content**

Add normalized City rules and exact source snippets into the notes file.

**Step 4: Validate notes completeness**

Run:

```bash
rg -n "Setup|Turn flow|Win condition|Normalized Rule Table" docs/plans/2026-02-26-monopoly-city-anchor-notes.md
```

Expected: all required sections present.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-city-anchor-notes.md
git commit -m "Add Monopoly City anchor notes"
```

### Task 2: Add City Profile Resolver

**Files:**
- Create: `server/games/monopoly/city_profile.py`
- Create: `server/tests/test_monopoly_city_profile.py`
- Read: `docs/plans/2026-02-26-monopoly-city-anchor-notes.md`

**Step 1: Write the failing tests**

```python
from server.games.monopoly.city_profile import (
    DEFAULT_CITY_PROFILE,
    resolve_city_profile,
)


def test_resolve_city_profile_uses_city_anchor_defaults():
    profile = resolve_city_profile("city")
    assert profile.preset_id == "city"
    assert profile.anchor_edition_id == "monopoly-1790"
    assert profile.source_policy == "anchor-first"
    assert profile.win_rule_key != ""


def test_resolve_city_profile_falls_back_to_default():
    assert resolve_city_profile("unknown") == DEFAULT_CITY_PROFILE
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city_profile.py -v`
Expected: FAIL (module does not exist yet).

**Step 3: Implement minimal resolver**

```python
@dataclass(frozen=True)
class CityProfile:
    preset_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"
    win_rule_key: str = ""
    win_threshold: int = 0
    rule_flags: tuple[str, ...] = ()
    provenance_notes: tuple[str, ...] = ()
```

Populate `DEFAULT_CITY_PROFILE` using normalized values from anchor notes.

**Step 4: Run tests to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/city_profile.py server/tests/test_monopoly_city_profile.py
git commit -m "Add Monopoly City profile resolver"
```

### Task 3: Add City Rules Data Module

**Files:**
- Create: `server/games/monopoly/city_rules.py`
- Create: `server/tests/test_monopoly_city_rules.py`
- Read: `docs/plans/2026-02-26-monopoly-city-anchor-notes.md`

**Step 1: Write failing tests for normalized rule constants/data**

```python
from server.games.monopoly.city_rules import (
    CITY_RULESET,
    CITY_SPACE_DEFINITIONS,
)


def test_city_ruleset_is_anchor_backed():
    assert CITY_RULESET.anchor_edition_id == "monopoly-1790"


def test_city_spaces_loaded_for_runtime_resolution():
    assert len(CITY_SPACE_DEFINITIONS) > 0
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city_rules.py -v`
Expected: FAIL.

**Step 3: Implement minimal data module**

```python
@dataclass(frozen=True)
class CityRuleset:
    anchor_edition_id: str
    win_rule_key: str
    win_threshold: int

CITY_RULESET = CityRuleset(...)
CITY_SPACE_DEFINITIONS: tuple[dict, ...] = (...)
```

Use only manual-backed entries from anchor notes.

**Step 4: Run tests to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/city_rules.py server/tests/test_monopoly_city_rules.py
git commit -m "Add Monopoly City rules data"
```

### Task 4: Add Deterministic City Engine Core

**Files:**
- Create: `server/games/monopoly/city_engine.py`
- Create: `server/tests/test_monopoly_city_engine.py`
- Read: `server/games/monopoly/city_profile.py`
- Read: `server/games/monopoly/city_rules.py`

**Step 1: Write failing engine tests**

```python
from server.games.monopoly.city_engine import CityEngine
from server.games.monopoly.city_profile import DEFAULT_CITY_PROFILE


def test_city_engine_initializes_turn_state():
    engine = CityEngine(DEFAULT_CITY_PROFILE)
    engine.on_turn_start("p1", 0)
    assert engine.current_turn_player_id == "p1"


def test_city_engine_reports_winner_when_threshold_reached():
    engine = CityEngine(DEFAULT_CITY_PROFILE)
    engine.record_progress("p1", DEFAULT_CITY_PROFILE.win_threshold)
    winner = engine.evaluate_winner(("p1", "p2"))
    assert winner == "p1"
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city_engine.py -v`
Expected: FAIL.

**Step 3: Implement minimal engine**

```python
@dataclass(frozen=True)
class CityOutcome:
    status: str = "allow"
    cash_delta: int = 0
    message_key: str = ""

@dataclass
class CityEngine:
    ...
    def on_turn_start(...): ...
    def record_progress(...): ...
    def evaluate_winner(...): ...
```

**Step 4: Run tests to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/city_engine.py server/tests/test_monopoly_city_engine.py
git commit -m "Add deterministic Monopoly City engine core"
```

### Task 5: Initialize City Profile/Engine In `MonopolyGame`

**Files:**
- Modify: `server/games/monopoly/game.py`
- Create: `server/tests/test_monopoly_city.py`

**Step 1: Write failing integration test**

```python
from server.games.monopoly.game import MonopolyGame, MonopolyOptions


def test_city_on_start_initializes_profile_and_engine():
    game = MonopolyGame(options=MonopolyOptions(preset_id="city"))
    # add players + start
    ...
    assert game.city_profile is not None
    assert game.city_engine is not None
    assert game.city_profile.anchor_edition_id == "monopoly-1790"
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city.py::test_city_on_start_initializes_profile_and_engine -v`
Expected: FAIL.

**Step 3: Implement minimal integration**

- Add imports and dataclass fields:
  - `city_profile: CityProfile | None = None`
  - `city_engine: CityEngine | None = None`
- Initialize/reset these in `on_start` using `active_preset_id == "city"`.

**Step 4: Run test to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_city.py
git commit -m "Initialize Monopoly City engine in game startup"
```

### Task 6: Wire City Progress And Effects Through Turn Resolution

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/tests/test_monopoly_city.py`

**Step 1: Add failing integration test for one anchor-backed City mechanic**

```python
def test_city_anchor_mechanic_updates_progress_and_cash(monkeypatch):
    game = _start_two_player_city_game()
    player = game.current_player
    ...
    game.execute_action(player, "roll_dice")
    assert game.city_engine is not None
    assert game.city_engine.progress_for(player.id) > 0
```

Use the exact mechanic and expected values from anchor notes.

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city.py::test_city_anchor_mechanic_updates_progress_and_cash -v`
Expected: FAIL.

**Step 3: Implement minimal hook wiring**

- Add City engine calls in City branch of space/payment resolution.
- Apply any City cash effects via existing debit/credit helpers.
- Keep hook path deterministic and preset-guarded.

**Step 4: Run test to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_city.py
git commit -m "Wire Monopoly City space effects"
```

### Task 7: Implement Full City Winner Loop

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/tests/test_monopoly_city.py`

**Step 1: Write failing winner-loop tests**

```python
def test_city_game_finishes_when_anchor_win_condition_met():
    game = _start_two_player_city_game()
    ...
    assert game.status == "finished"
    assert game.current_player is not None


def test_city_tie_break_rule_follows_anchor_notes():
    game = _start_two_player_city_game()
    ...
    assert game.current_player.id == expected_winner_id
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city.py::test_city_game_finishes_when_anchor_win_condition_met tests/test_monopoly_city.py::test_city_tie_break_rule_follows_anchor_notes -v`
Expected: FAIL.

**Step 3: Implement minimal winner-loop checks**

- Add a City endgame evaluator in `MonopolyGame`.
- Evaluate winner after City-relevant mutations.
- Transition to finished state and announce winner deterministically.

**Step 4: Run tests to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_city.py
git commit -m "Add Monopoly City winner loop"
```

### Task 8: Add City Localization Keys

**Files:**
- Modify: `server/locales/en/monopoly.ftl`
- Modify: `server/locales/pl/monopoly.ftl`
- Modify: `server/locales/pt/monopoly.ftl`
- Modify: `server/locales/ru/monopoly.ftl`
- Modify: `server/locales/vi/monopoly.ftl`
- Modify: `server/locales/zh/monopoly.ftl`
- Modify: `server/tests/test_monopoly_city.py`

**Step 1: Write failing test for City message emission path**

```python
def test_city_emits_localized_winner_message(monkeypatch):
    game = _start_two_player_city_game()
    ...
    # trigger City win
    ...
    # assert message path executed without localization key fallback
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_city.py::test_city_emits_localized_winner_message -v`
Expected: FAIL.

**Step 3: Add City message keys across all locales**

Add keys for City actions/effects/winner events based on anchor-backed mechanics.

**Step 4: Run test to verify pass**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/locales/en/monopoly.ftl server/locales/pl/monopoly.ftl server/locales/pt/monopoly.ftl server/locales/ru/monopoly.ftl server/locales/vi/monopoly.ftl server/locales/zh/monopoly.ftl server/tests/test_monopoly_city.py
git commit -m "Add Monopoly City localization keys"
```

### Task 9: Final Verification And Stabilization

**Files:**
- Modify: tests/code only if regressions are found

**Step 1: Run focused City tests**

Run:

```bash
cd server && ../.venv/bin/pytest tests/test_monopoly_city_profile.py tests/test_monopoly_city_rules.py tests/test_monopoly_city_engine.py tests/test_monopoly_city.py -v
```

Expected: PASS.

**Step 2: Run Monopoly regression suite**

Run:

```bash
cd server && ../.venv/bin/pytest -k monopoly -v
```

Expected: PASS.

**Step 3: Run integration smoke checks**

Run:

```bash
cd server && ../.venv/bin/pytest tests/test_integration.py::TestGameRegistryIntegration::test_pig_game_registered tests/test_integration.py::TestGameRegistryIntegration::test_get_by_category -v
```

Expected: PASS.

**Step 4: Fix regressions minimally if needed**

Apply smallest possible targeted patches and rerun failed commands.

**Step 5: Commit**

```bash
git add server/games/monopoly/*.py server/tests/test_monopoly*.py server/locales/*/monopoly.ftl docs/plans/2026-02-26-monopoly-city-anchor-notes.md
git commit -m "Finalize Monopoly City preset integration"
```

## Done Definition

1. City rules are extracted and normalized from `monopoly-1790` in anchor notes.
2. `city` preset initializes profile + engine with strict `anchor-first` policy.
3. Anchor-backed City mechanics are wired into runtime flow deterministically.
4. Full City winner loop ships in first pass.
5. Monopoly regression and integration smoke checks pass.
