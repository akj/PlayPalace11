# Monopoly Board Profiles Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add board-level selection with dual-mode behavior (skin-only and auto board-rules), starting with Wave 1 Mario boards and compatibility auto-fix.

**Architecture:** Keep `MonopolyGame` as the single runtime entrypoint and introduce a data-first board profile resolver that normalizes `{preset_id, board_id, board_rules_mode}` into one deterministic runtime plan. Layer board-rule packs behind capability gates so partial packs can safely fall back to preset behavior. Keep preset logic intact and additive, with explicit announcements for auto-fix and simplification.

**Tech Stack:** Python 3.13, dataclasses, existing Monopoly engine in `server/games/monopoly/game.py`, pytest, Fluent localization (`server/locales/*/monopoly.ftl`), curated Monopoly catalog JSON.

---

### Task 1: Capture Mario Anchors and Seed Themed Backlog

**Files:**
- Create: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`
- Create: `docs/plans/2026-02-26-monopoly-themed-board-backlog.md`
- Read: `server/games/monopoly/catalog/playable_presets.json`
- Read: `server/games/monopoly/catalog/monopoly_editions_curated.json`
- Read: `server/games/monopoly/catalog/monopoly_manual_variants_curated.json`

**Step 1: Run pre-check to confirm docs do not exist yet**

Run:

```bash
rg -n "Monopoly Mario Board Anchor Notes|Themed Board Backlog" docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md docs/plans/2026-02-26-monopoly-themed-board-backlog.md
```

Expected: FAIL with "No such file or directory".

**Step 2: Generate Wave 1 Mario edition references from catalog**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
play = json.loads(Path('server/games/monopoly/catalog/playable_presets.json').read_text())
editions = {r['edition_id']: r for r in json.loads(Path('server/games/monopoly/catalog/monopoly_editions_curated.json').read_text())}
manuals = json.loads(Path('server/games/monopoly/catalog/monopoly_manual_variants_curated.json').read_text())
wave1 = ['monopoly-c4382','monopoly-e1870','monopoly-e9517','monopoly-f6818','monopoly-f4817']
for eid in wave1:
    row = editions[eid]
    print(eid, '|', row.get('display_name',''))
    for m in manuals:
        if m.get('edition_id') == eid and m.get('locale') == 'en-us':
            print('  en-us manual:', m.get('instruction_url'))
            print('  en-us pdf:', m.get('pdf_url'))
            break
PY
```

Expected: PASS with Wave 1 edition IDs and at least one manual URL per board where available.

**Step 3: Write anchor notes and backlog docs**

Create `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md` with sections:

```markdown
# Monopoly Mario Board Anchor Notes

## Wave 1 Boards
- monopoly-c4382
- monopoly-e1870
- monopoly-e9517
- monopoly-f6818
- monopoly-f4817

## Source Policy
- anchor-first

## Normalized Rule Table
| board_id | anchor_edition_id | compatible_presets | rule_pack_id | rule_pack_status | pass_go_credit | notes |
|---|---|---|---|---|---:|---|
```

Create `docs/plans/2026-02-26-monopoly-themed-board-backlog.md` with table:

```markdown
# Monopoly Themed Board Backlog

| edition_id | display_name | target_preset | status |
|---|---|---|---|
| ... | ... | classic_standard/junior | not_started |
```

**Step 4: Validate docs contain required sections**

Run:

```bash
rg -n "Wave 1 Boards|Source Policy|Normalized Rule Table" docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md
rg -n "Themed Board Backlog|status" docs/plans/2026-02-26-monopoly-themed-board-backlog.md
```

Expected: PASS with line matches.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md docs/plans/2026-02-26-monopoly-themed-board-backlog.md
git commit -m "Add Mario board anchors and themed backlog"
```

### Task 2: Add Board Profile Resolver Module

**Files:**
- Create: `server/games/monopoly/board_profile.py`
- Create: `server/tests/test_monopoly_board_profile.py`
- Read: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`

**Step 1: Write failing resolver tests**

```python
from server.games.monopoly.board_profile import (
    DEFAULT_BOARD_ID,
    resolve_board_plan,
)


def test_resolve_board_plan_keeps_compatible_preset():
    plan = resolve_board_plan("classic_standard", "mario_kart", "auto")
    assert plan.effective_preset_id == "classic_standard"
    assert plan.effective_mode == "board_rules"


def test_resolve_board_plan_autofixes_incompatible_preset():
    plan = resolve_board_plan("classic_standard", "junior_super_mario", "auto")
    assert plan.effective_preset_id == "junior"
    assert plan.auto_fixed_from_preset_id == "classic_standard"


def test_resolve_board_plan_forces_skin_only_override():
    plan = resolve_board_plan("classic_standard", "mario_movie", "skin_only")
    assert plan.effective_mode == "skin_only"


def test_resolve_board_plan_unknown_board_falls_back_to_default():
    plan = resolve_board_plan("classic_standard", "does_not_exist", "auto")
    assert plan.effective_board_id == DEFAULT_BOARD_ID
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_profile.py -v`

Expected: FAIL with `ModuleNotFoundError` for `board_profile`.

**Step 3: Implement minimal resolver**

```python
from dataclasses import dataclass

DEFAULT_BOARD_ID = "classic_default"

@dataclass(frozen=True)
class BoardProfile:
    board_id: str
    label_key: str
    anchor_edition_id: str
    compatible_preset_ids: tuple[str, ...]
    fallback_preset_id: str
    rule_pack_id: str | None = None
    rule_pack_status: str = "none"

@dataclass(frozen=True)
class ResolvedBoardPlan:
    requested_preset_id: str
    requested_board_id: str
    requested_mode: str
    effective_preset_id: str
    effective_board_id: str
    effective_mode: str
    rule_pack_id: str | None
    rule_pack_status: str
    auto_fixed_from_preset_id: str | None = None

BOARD_PROFILES: dict[str, BoardProfile] = {
    "classic_default": BoardProfile(...),
    "mario_collectors": BoardProfile(...),
    "mario_kart": BoardProfile(...),
    "mario_celebration": BoardProfile(...),
    "mario_movie": BoardProfile(...),
    "junior_super_mario": BoardProfile(...),
}

def resolve_board_plan(preset_id: str, board_id: str, mode: str) -> ResolvedBoardPlan:
    ...
```

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_profile.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_profile.py server/tests/test_monopoly_board_profile.py
git commit -m "Add Monopoly board profile resolver"
```

### Task 3: Add Board Rules Registry and Capability Contract

**Files:**
- Create: `server/games/monopoly/board_rules_registry.py`
- Create: `server/tests/test_monopoly_board_rules_registry.py`
- Read: `server/games/monopoly/board_profile.py`

**Step 1: Write failing registry tests**

```python
from server.games.monopoly.board_rules_registry import (
    get_rule_pack,
    supports_capability,
)


def test_wave1_mario_packs_are_registered():
    assert get_rule_pack("mario_kart") is not None
    assert get_rule_pack("mario_movie") is not None


def test_capability_lookup_handles_missing_pack():
    assert supports_capability("missing", "pass_go_credit") is False
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`

Expected: FAIL with `ModuleNotFoundError`.

**Step 3: Implement minimal registry**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class BoardRulePack:
    rule_pack_id: str
    status: str
    capability_ids: tuple[str, ...]

RULE_PACKS: dict[str, BoardRulePack] = {
    "mario_collectors": BoardRulePack(...),
    "mario_kart": BoardRulePack(...),
    "mario_celebration": BoardRulePack(...),
    "mario_movie": BoardRulePack(...),
    "junior_super_mario": BoardRulePack(...),
}

def get_rule_pack(rule_pack_id: str) -> BoardRulePack | None:
    return RULE_PACKS.get(rule_pack_id)

def supports_capability(rule_pack_id: str, capability_id: str) -> bool:
    pack = get_rule_pack(rule_pack_id)
    return bool(pack and capability_id in pack.capability_ids)
```

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules_registry.py server/tests/test_monopoly_board_rules_registry.py
git commit -m "Add Monopoly board rules registry"
```

### Task 4: Add Wave 1 Mario Rule-Pack Modules

**Files:**
- Create: `server/games/monopoly/board_rules/__init__.py`
- Create: `server/games/monopoly/board_rules/mario_collectors.py`
- Create: `server/games/monopoly/board_rules/mario_kart.py`
- Create: `server/games/monopoly/board_rules/mario_celebration.py`
- Create: `server/games/monopoly/board_rules/mario_movie.py`
- Create: `server/games/monopoly/board_rules/junior_super_mario.py`
- Create: `server/tests/test_monopoly_mario_rule_packs.py`
- Read: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`

**Step 1: Write failing tests for pack metadata + anchor values**

```python
from server.games.monopoly.board_rules import mario_kart, mario_movie


def test_mario_pack_exposes_anchor_edition_id():
    assert mario_kart.ANCHOR_EDITION_ID.startswith("monopoly-")


def test_mario_pack_exposes_pass_go_contract():
    assert isinstance(mario_movie.PASS_GO_CREDIT_OVERRIDE, int | None)
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py -v`

Expected: FAIL with import/module errors.

**Step 3: Implement pack modules with deterministic capability exports**

```python
ANCHOR_EDITION_ID = "monopoly-e1870"
RULE_PACK_ID = "mario_kart"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE: int | None = 200
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
```

Repeat for each Wave 1 board using anchor-notes-backed constants.

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules server/tests/test_monopoly_mario_rule_packs.py
git commit -m "Add Wave 1 Mario board rule-pack modules"
```

### Task 5: Add `board_id` and `board_rules_mode` Lobby Options

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/locales/en/monopoly.ftl`
- Modify: `server/locales/pl/monopoly.ftl`
- Modify: `server/locales/pt/monopoly.ftl`
- Modify: `server/locales/ru/monopoly.ftl`
- Modify: `server/locales/vi/monopoly.ftl`
- Modify: `server/locales/zh/monopoly.ftl`
- Create: `server/tests/test_monopoly_board_options.py`

**Step 1: Write failing options tests**

```python
from server.games.monopoly.game import MonopolyGame
from server.users.test_user import MockUser


def test_monopoly_options_include_board_and_mode_selectors():
    game = MonopolyGame()
    host = game.create_player("p1", "Host")
    game.players = [host]
    game.host = host.name
    action_set = game.get_action_set(host, "options")
    assert action_set.get_action("set_board_id") is not None
    assert action_set.get_action("set_board_rules_mode") is not None
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_options.py -v`

Expected: FAIL because option actions do not exist yet.

**Step 3: Implement options and localization keys**

Add to `MonopolyOptions`:

```python
board_id: str = option_field(MenuOption(...))
board_rules_mode: str = option_field(MenuOption(...))
```

Add keys in all locales:

```ftl
monopoly-set-board = Board: { $board }
monopoly-select-board = Select a Monopoly board
monopoly-option-changed-board = Board set to { $board }.
monopoly-set-board-rules-mode = Board rules mode: { $mode }
monopoly-select-board-rules-mode = Select board rules mode
monopoly-option-changed-board-rules-mode = Board rules mode set to { $mode }.
monopoly-board-rules-mode-auto = Auto
monopoly-board-rules-mode-skin-only = Skin only
```

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_options.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/locales/*/monopoly.ftl server/tests/test_monopoly_board_options.py
git commit -m "Add Monopoly board and rules-mode options"
```

### Task 6: Integrate Board Resolver Into `on_start` with Compatibility Auto-Fix

**Files:**
- Modify: `server/games/monopoly/game.py`
- Create: `server/tests/test_monopoly_board_selection.py`

**Step 1: Write failing integration tests for startup resolution**

```python
from server.games.monopoly.game import MonopolyGame, MonopolyOptions
from server.users.test_user import MockUser


def _start(options: MonopolyOptions) -> MonopolyGame:
    game = MonopolyGame(options=options)
    game.add_player("Host", MockUser("Host"))
    game.add_player("Guest", MockUser("Guest"))
    game.host = "Host"
    game.on_start()
    return game


def test_board_selection_sets_active_board_fields():
    game = _start(MonopolyOptions(preset_id="classic_standard", board_id="mario_kart"))
    assert game.active_board_id == "mario_kart"


def test_incompatible_board_autofixes_preset():
    game = _start(MonopolyOptions(preset_id="classic_standard", board_id="junior_super_mario"))
    assert game.active_preset_id == "junior"
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_selection.py -v`

Expected: FAIL because board resolver is not wired.

**Step 3: Implement startup integration**

In `game.py`:

```python
from .board_profile import resolve_board_plan

active_board_id: str = "classic_default"
active_board_anchor_edition_id: str = ""
active_board_rules_mode: str = "auto"
active_board_effective_mode: str = "skin_only"
active_board_rule_pack_id: str = ""

...
board_plan = resolve_board_plan(self.options.preset_id, self.options.board_id, self.options.board_rules_mode)
if board_plan.auto_fixed_from_preset_id is not None:
    self.options.preset_id = board_plan.effective_preset_id
...
self.active_board_id = board_plan.effective_board_id
self.active_board_effective_mode = board_plan.effective_mode
```

Add broadcast key call for auto-fix event.

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_selection.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_board_selection.py
git commit -m "Resolve board selection and auto-fix preset compatibility"
```

### Task 7: Add Auto-Fix and Simplification Announcements

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/locales/en/monopoly.ftl`
- Modify: `server/locales/pl/monopoly.ftl`
- Modify: `server/locales/pt/monopoly.ftl`
- Modify: `server/locales/ru/monopoly.ftl`
- Modify: `server/locales/vi/monopoly.ftl`
- Modify: `server/locales/zh/monopoly.ftl`
- Modify: `server/tests/test_monopoly_board_selection.py`

**Step 1: Write failing message-path tests**

```python
def test_board_autofix_emits_announcement(monkeypatch):
    ...
    assert "monopoly-board-preset-autofixed" in emitted


def test_partial_rule_pack_emits_simplified_notice(monkeypatch):
    ...
    assert "monopoly-board-rules-simplified" in emitted
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_selection.py::test_board_autofix_emits_announcement tests/test_monopoly_board_selection.py::test_partial_rule_pack_emits_simplified_notice -v`

Expected: FAIL because messages are not emitted.

**Step 3: Implement broadcasts and localization keys**

Add keys in all locales:

```ftl
monopoly-board-preset-autofixed = Board { $board } is incompatible with { $from_preset }; switched to { $to_preset }.
monopoly-board-rules-simplified = Board rules for { $board } are partially implemented; base preset behavior is used for missing mechanics.
monopoly-board-active = Active board: { $board } (mode: { $mode }).
```

Emit these keys in `on_start` after board resolution.

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_selection.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/locales/*/monopoly.ftl server/tests/test_monopoly_board_selection.py
git commit -m "Add board auto-fix and simplification announcements"
```

### Task 8: Wire First Board Capability Hook Through Runtime

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/games/monopoly/board_rules_registry.py`
- Modify: `server/tests/test_monopoly_mario_boards.py` (create if missing)

**Step 1: Write failing runtime tests for board capability path**

```python
from server.games.monopoly.game import MonopolyGame, MonopolyOptions


def test_board_rules_auto_applies_pass_go_override(monkeypatch):
    game = _start_two_player_game(MonopolyOptions(
        preset_id="classic_standard",
        board_id="mario_kart",
        board_rules_mode="auto",
    ))
    host = game.current_player
    host.position = 39
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))
    game.execute_action(host, "roll_dice")
    assert host.cash >= 1700
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`

Expected: FAIL because board capability hooks are not applied.

**Step 3: Implement minimal hook in move/economy path**

In `game.py`:

```python
def _resolve_board_pass_go_credit(self, base_credit: int) -> int:
    ...

# in _move_player pass-go block
pass_go_cash = self._resolve_board_pass_go_credit(pass_go_cash)
```

Use rule-pack registry only when effective mode is `board_rules`; otherwise use base preset amount.

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/games/monopoly/board_rules_registry.py server/tests/test_monopoly_mario_boards.py
git commit -m "Wire first Monopoly board capability hook"
```

### Task 9: Add Wave 1 Board Integration Coverage (Skin-Only + Board-Rules)

**Files:**
- Modify: `server/tests/test_monopoly_mario_boards.py`
- Read: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`

**Step 1: Write failing matrix tests for all Wave 1 boards**

```python
import pytest

@pytest.mark.parametrize("board_id,preset_id", [
    ("mario_collectors", "classic_standard"),
    ("mario_kart", "classic_standard"),
    ("mario_celebration", "classic_standard"),
    ("mario_movie", "classic_standard"),
    ("junior_super_mario", "junior"),
])
def test_wave1_board_starts_with_resolved_mode(board_id, preset_id):
    game = _start_two_player_game(MonopolyOptions(
        preset_id=preset_id,
        board_id=board_id,
        board_rules_mode="auto",
    ))
    assert game.active_board_id == board_id


def test_skin_only_override_disables_board_rule_path():
    ...
```

**Step 2: Run tests to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`

Expected: FAIL on missing fields/behavior.

**Step 3: Implement minimal fixes for matrix pass**

Add only minimal runtime adjustments required for deterministic matrix pass; keep fallback behavior explicit.

**Step 4: Run tests to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_mario_boards.py server/games/monopoly/game.py
# include any touched board profile/registry modules as needed
git commit -m "Add Wave 1 Mario board integration tests"
```

### Task 10: Final Verification and Stabilization

**Files:**
- Modify: tests/code only if regressions are found

**Step 1: Run focused board profile/rules tests**

Run:

```bash
cd server && ../.venv/bin/pytest \
  tests/test_monopoly_board_profile.py \
  tests/test_monopoly_board_rules_registry.py \
  tests/test_monopoly_board_options.py \
  tests/test_monopoly_board_selection.py \
  tests/test_monopoly_mario_rule_packs.py \
  tests/test_monopoly_mario_boards.py -v
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

Apply smallest possible targeted patches and rerun failed commands.

**Step 5: Commit**

```bash
git add server/games/monopoly/*.py server/games/monopoly/board_rules/*.py server/tests/test_monopoly*.py server/locales/*/monopoly.ftl docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md docs/plans/2026-02-26-monopoly-themed-board-backlog.md
git commit -m "Finalize Monopoly board profile Wave 1 integration"
```

## Done Definition
1. `board_id` and `board_rules_mode` exist as lobby options next to `preset_id`.
2. Resolver deterministically normalizes compatibility and mode.
3. Incompatible board/preset combinations auto-fix and announce the preset switch.
4. `auto` mode applies board-rule capabilities when available; `skin_only` bypasses them.
5. Partial packs emit simplification notice and safely fall back to base preset behavior.
6. Wave 1 Mario boards are represented with anchor-backed metadata and tested startup/runtime paths.
7. Backlog document exists for all remaining themed boards.
8. Monopoly regression and integration smoke checks pass.
