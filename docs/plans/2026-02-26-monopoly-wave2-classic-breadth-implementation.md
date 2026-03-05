# Monopoly Wave 2 Classic Breadth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Onboard 25 additional classic-themed Monopoly boards as selectable profiles with partial rule-pack fallback behavior and full regression safety.

**Architecture:** Reuse the existing board-profile resolver and board-rules registry added in Wave 1. Expand data-driven board profile and rule-pack coverage for a curated Top-25 classic set while keeping runtime mechanics stable via existing `partial` fallback semantics and deterministic announcements.

**Tech Stack:** Python 3.13, dataclasses, existing Monopoly runtime (`server/games/monopoly/game.py`), pytest, Fluent locale files, curated Monopoly catalog artifacts.

---

### Task 1: Create Wave 2 Source Artifact

**Files:**
- Create: `docs/plans/2026-02-26-monopoly-wave2-top25-classic.md`
- Read: `docs/plans/2026-02-26-monopoly-wave2-classic-breadth-design.md`
- Read: `docs/plans/2026-02-26-monopoly-themed-board-backlog.md`

**Step 1: Write failing existence check**

Run:

```bash
rg -n "Wave 2 Top 25 Classic" docs/plans/2026-02-26-monopoly-wave2-top25-classic.md
```

Expected: FAIL with missing file.

**Step 2: Create curated Top-25 source file**

```markdown
# Monopoly Wave 2 Top 25 Classic

| board_id | edition_id | bucket | status_target |
|---|---|---|---|
| disney_princesses | monopoly-b4644 | disney | partial_rules |
| ... 24 more rows ... |
```

Include all 25 rows exactly as approved in design.

**Step 3: Validate row count and schema**

Run:

```bash
python - <<'PY'
from pathlib import Path
p=Path('docs/plans/2026-02-26-monopoly-wave2-top25-classic.md')
rows=[line for line in p.read_text().splitlines() if line.startswith('| ') and '---' not in line]
print('rows',len(rows)-1)  # subtract header row
PY
```

Expected: `rows 25`.

**Step 4: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-wave2-top25-classic.md
git commit -m "Add Wave 2 Top 25 classic board source"
```

### Task 2: Extend Board Profiles for Wave 2

**Files:**
- Modify: `server/games/monopoly/board_profile.py`
- Create: `server/tests/test_monopoly_wave2_board_profile.py`
- Read: `docs/plans/2026-02-26-monopoly-wave2-top25-classic.md`

**Step 1: Write failing profile resolution tests**

```python
import pytest
from server.games.monopoly.board_profile import resolve_board_plan

WAVE2 = [
    "disney_princesses",
    "disney_animation",
    # ... all 25 ids ...
]

@pytest.mark.parametrize("board_id", WAVE2)
def test_wave2_boards_resolve_to_classic_board_rules(board_id):
    plan = resolve_board_plan("classic_standard", board_id, "auto")
    assert plan.effective_preset_id == "classic_standard"
    assert plan.effective_mode == "board_rules"
    assert plan.rule_pack_status == "partial"
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_profile.py -v`

Expected: FAIL because board IDs are not present.

**Step 3: Add 25 `BoardProfile` entries**

In `BOARD_PROFILES`, add each board with:

```python
"disney_princesses": BoardProfile(
    board_id="disney_princesses",
    label_key="monopoly-board-disney-princesses",
    anchor_edition_id="monopoly-b4644",
    compatible_preset_ids=("classic_standard",),
    fallback_preset_id="classic_standard",
    rule_pack_id="disney_princesses",
    rule_pack_status="partial",
)
```

Repeat for all 25 boards.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_profile.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_profile.py server/tests/test_monopoly_wave2_board_profile.py
git commit -m "Add Wave 2 classic board profiles"
```

### Task 3: Extend Board Rules Registry for Wave 2

**Files:**
- Modify: `server/games/monopoly/board_rules_registry.py`
- Create: `server/tests/test_monopoly_wave2_board_rules_registry.py`
- Read: `docs/plans/2026-02-26-monopoly-wave2-top25-classic.md`

**Step 1: Write failing registry tests for all Wave 2 packs**

```python
import pytest
from server.games.monopoly.board_rules_registry import get_rule_pack, supports_capability

WAVE2 = [
    "disney_princesses",
    # ... all 25 ids ...
]

@pytest.mark.parametrize("rule_pack_id", WAVE2)
def test_wave2_rule_pack_registered(rule_pack_id):
    pack = get_rule_pack(rule_pack_id)
    assert pack is not None
    assert pack.status == "partial"
    assert supports_capability(rule_pack_id, "pass_go_credit_override") is True
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_rules_registry.py -v`

Expected: FAIL until packs are added.

**Step 3: Register 25 packs**

For each board id, add:

```python
"disney_princesses": BoardRulePack(
    rule_pack_id="disney_princesses",
    status="partial",
    capability_ids=("pass_go_credit_override", "startup_board_announcement"),
)
```

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_rules_registry.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules_registry.py server/tests/test_monopoly_wave2_board_rules_registry.py
git commit -m "Add Wave 2 board rules registry entries"
```

### Task 4: Add Wave 2 Rule-Pack Stub Modules

**Files:**
- Create: `server/games/monopoly/board_rules/disney_princesses.py`
- Create: `server/games/monopoly/board_rules/disney_animation.py`
- Create: `server/games/monopoly/board_rules/disney_lion_king.py`
- Create: `server/games/monopoly/board_rules/disney_mickey_friends.py`
- Create: `server/games/monopoly/board_rules/disney_villains.py`
- Create: `server/games/monopoly/board_rules/disney_lightyear.py`
- Create: `server/games/monopoly/board_rules/marvel_80_years.py`
- Create: `server/games/monopoly/board_rules/marvel_avengers.py`
- Create: `server/games/monopoly/board_rules/marvel_spider_man.py`
- Create: `server/games/monopoly/board_rules/marvel_black_panther_wf.py`
- Create: `server/games/monopoly/board_rules/marvel_super_villains.py`
- Create: `server/games/monopoly/board_rules/marvel_deadpool.py`
- Create: `server/games/monopoly/board_rules/star_wars_40th.py`
- Create: `server/games/monopoly/board_rules/star_wars_boba_fett.py`
- Create: `server/games/monopoly/board_rules/star_wars_light_side.py`
- Create: `server/games/monopoly/board_rules/star_wars_the_child.py`
- Create: `server/games/monopoly/board_rules/star_wars_mandalorian.py`
- Create: `server/games/monopoly/board_rules/star_wars_complete_saga.py`
- Create: `server/games/monopoly/board_rules/harry_potter.py`
- Create: `server/games/monopoly/board_rules/fortnite.py`
- Create: `server/games/monopoly/board_rules/stranger_things.py`
- Create: `server/games/monopoly/board_rules/jurassic_park.py`
- Create: `server/games/monopoly/board_rules/lord_of_the_rings.py`
- Create: `server/games/monopoly/board_rules/animal_crossing.py`
- Create: `server/games/monopoly/board_rules/barbie.py`
- Modify: `server/games/monopoly/board_rules/__init__.py`
- Create: `server/tests/test_monopoly_wave2_rule_pack_modules.py`

**Step 1: Write failing import tests for stub modules**

```python
from server.games.monopoly.board_rules import disney_princesses, marvel_avengers, star_wars_40th


def test_wave2_stub_exposes_anchor_and_status():
    assert disney_princesses.ANCHOR_EDITION_ID.startswith("monopoly-")
    assert marvel_avengers.RULE_PACK_STATUS == "partial"
    assert isinstance(star_wars_40th.PASS_GO_CREDIT_OVERRIDE, int)
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_rule_pack_modules.py -v`

Expected: FAIL until modules are created.

**Step 3: Add minimal stub constant modules**

Each module should define:

```python
RULE_PACK_ID = "disney_princesses"
ANCHOR_EDITION_ID = "monopoly-b4644"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = ("pass_go_credit_override", "startup_board_announcement")
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
```

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_rule_pack_modules.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules server/tests/test_monopoly_wave2_rule_pack_modules.py
git commit -m "Add Wave 2 board rule-pack stubs"
```

### Task 5: Add Locale Labels for 25 New Boards

**Files:**
- Modify: `server/locales/en/monopoly.ftl`
- Modify: `server/locales/pl/monopoly.ftl`
- Modify: `server/locales/pt/monopoly.ftl`
- Modify: `server/locales/ru/monopoly.ftl`
- Modify: `server/locales/vi/monopoly.ftl`
- Modify: `server/locales/zh/monopoly.ftl`
- Create: `server/tests/test_monopoly_wave2_board_labels.py`

**Step 1: Write failing label tests**

```python
from server.messages.localization import Localization


def test_wave2_board_label_keys_exist_in_en():
    value = Localization.get("en", "monopoly-board-disney-princesses")
    assert value != "monopoly-board-disney-princesses"
```

Add one representative key assertion per locale file if needed.

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_labels.py -v`

Expected: FAIL because keys are missing.

**Step 3: Add label keys for all 25 board IDs in all locales**

Format:

```ftl
monopoly-board-disney-princesses = Disney Princesses
```

(Use same English string across non-English locales for now to keep parity and avoid missing keys.)

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_board_labels.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/locales/*/monopoly.ftl server/tests/test_monopoly_wave2_board_labels.py
git commit -m "Add Wave 2 board localization labels"
```

### Task 6: Extend Runtime Module Mapping for Wave 2 Pass-GO Hook

**Files:**
- Modify: `server/games/monopoly/board_rules_registry.py`
- Create: `server/tests/test_monopoly_wave2_pass_go_override.py`

**Step 1: Write failing test proving one Wave 2 board can override pass-GO in auto mode**

```python
from server.games.monopoly.game import MonopolyGame, MonopolyOptions
from server.users.test_user import MockUser


def test_wave2_board_pass_go_override_path(monkeypatch):
    game = MonopolyGame(options=MonopolyOptions(
        preset_id="classic_standard",
        board_id="disney_princesses",
        board_rules_mode="auto",
    ))
    ...
    monkeypatch.setattr(
        "server.games.monopoly.board_rules.disney_princesses.PASS_GO_CREDIT_OVERRIDE",
        275,
    )
    ...
    assert host.cash == 1775
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_pass_go_override.py -v`

Expected: FAIL if module mapping is incomplete.

**Step 3: Extend `RULE_PACK_MODULES` with all 25 module references**

Ensure each new `rule_pack_id` maps to the corresponding module object.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_pass_go_override.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules_registry.py server/tests/test_monopoly_wave2_pass_go_override.py
git commit -m "Wire Wave 2 board modules into capability runtime"
```

### Task 7: Add Wave 2 Startup Matrix Integration Tests

**Files:**
- Modify: `server/tests/test_monopoly_mario_boards.py`
- Create: `server/tests/test_monopoly_wave2_boards.py`

**Step 1: Write failing Wave 2 startup matrix tests**

```python
import pytest
from server.games.monopoly.game import MonopolyOptions

WAVE2 = [
    "disney_princesses",
    # ... 24 more ...
]

@pytest.mark.parametrize("board_id", WAVE2)
def test_wave2_board_starts_in_auto_board_rules(board_id):
    game = _start_two_player_game(MonopolyOptions(
        preset_id="classic_standard",
        board_id=board_id,
        board_rules_mode="auto",
    ))
    assert game.active_board_id == board_id
    assert game.active_board_effective_mode == "board_rules"
```

Add one test for incompatibility auto-fix sample (e.g. `preset_id="city"` + wave2 board).

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_boards.py -v`

Expected: FAIL until profiles/labels/mappings are complete.

**Step 3: Implement minimal fixes (if any) to satisfy matrix**

Only patch runtime where required; prefer data updates over behavior changes.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave2_boards.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_wave2_boards.py server/games/monopoly/*.py
# include any additional touched files
git commit -m "Add Wave 2 board startup integration matrix"
```

### Task 8: Update Backlog Status for Selected 25

**Files:**
- Modify: `docs/plans/2026-02-26-monopoly-themed-board-backlog.md`
- Read: `docs/plans/2026-02-26-monopoly-wave2-top25-classic.md`

**Step 1: Write failing status check script**

Run:

```bash
python - <<'PY'
from pathlib import Path
backlog = Path('docs/plans/2026-02-26-monopoly-themed-board-backlog.md').read_text()
for eid in [
    'monopoly-b4644',
    # ... all 25 ...
]:
    needle = f"| `{eid}` |"
    if needle not in backlog:
        raise SystemExit(f"missing row: {eid}")
    line = next(l for l in backlog.splitlines() if needle in l)
    if '`partial_rules`' not in line:
        raise SystemExit(f"not partial_rules: {eid}")
print('ok')
PY
```

Expected: FAIL before status update.

**Step 2: Update 25 rows from `not_started` to `partial_rules`**

Keep all non-selected rows untouched.

**Step 3: Run validation script again**

Expected: PASS with `ok`.

**Step 4: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-themed-board-backlog.md
git commit -m "Update backlog status for Wave 2 classic boards"
```

### Task 9: Final Verification and Stabilization

**Files:**
- Modify: tests/code only if regressions are found

**Step 1: Run focused Wave 2 tests**

Run:

```bash
cd server && ../.venv/bin/pytest \
  tests/test_monopoly_wave2_board_profile.py \
  tests/test_monopoly_wave2_board_rules_registry.py \
  tests/test_monopoly_wave2_rule_pack_modules.py \
  tests/test_monopoly_wave2_board_labels.py \
  tests/test_monopoly_wave2_pass_go_override.py \
  tests/test_monopoly_wave2_boards.py -v
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
cd server && ../.venv/bin/pytest \
  tests/test_integration.py::TestGameRegistryIntegration::test_pig_game_registered \
  tests/test_integration.py::TestGameRegistryIntegration::test_get_by_category -v
```

Expected: PASS.

**Step 4: Fix regressions minimally if needed**

Apply smallest possible patch, rerun only failed scope first, then rerun full verification.

**Step 5: Commit final stabilization**

```bash
git add server/games/monopoly/*.py server/games/monopoly/board_rules/*.py server/tests/test_monopoly*.py server/locales/*/monopoly.ftl docs/plans/2026-02-26-monopoly-themed-board-backlog.md docs/plans/2026-02-26-monopoly-wave2-top25-classic.md
git commit -m "Finalize Monopoly Wave 2 classic board breadth rollout"
```

## Done Definition
1. Top-25 classic board source file exists and matches approved list.
2. 25 new board profiles are selectable and resolve in `auto` mode.
3. 25 rule packs + modules are registered with deterministic partial fallback semantics.
4. Board labels exist for all new IDs across required locales.
5. At least one Wave 2 board proves pass-GO override capability path.
6. Wave 2 startup matrix tests pass.
7. Backlog statuses for selected 25 are updated to `partial_rules`.
8. Monopoly regression and integration smoke checks pass.
