# Monopoly Junior Modern And Legacy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add fully selectable `junior_modern` and `junior_legacy` Monopoly presets with near-complete, anchor-driven rules and no regressions to existing presets.

**Architecture:** Keep one shared Junior execution path inside `MonopolyGame`, selected by preset profile. Encode modern and legacy differences in explicit Junior ruleset data keyed by preset ID and anchored to `monopoly-f8562` (modern) and `monopoly-00441` (legacy). Preserve classic/speed/builder behavior by isolating Junior dispatch and state transitions.

**Tech Stack:** Python 3.13, pytest, existing Monopoly game architecture (`server/games/monopoly/game.py`), Fluent localization files (`server/locales/*/monopoly.ftl`).

---

## Execution Notes

- Required skills during implementation: `@verification-before-completion`
- Optional research helper if manual interpretation is blocked: `@pdf` via skill-installer workflow
- Keep commits small and sentence-case, matching repository style.
- Run commands from repository root unless stated otherwise.

### Task 1: Add New Junior Preset IDs To Lobby And Localization

**Files:**
- Modify: `server/games/monopoly/game.py`
- Modify: `server/locales/en/monopoly.ftl`
- Modify: `server/locales/pl/monopoly.ftl`
- Modify: `server/locales/pt/monopoly.ftl`
- Modify: `server/locales/ru/monopoly.ftl`
- Modify: `server/locales/vi/monopoly.ftl`
- Modify: `server/locales/zh/monopoly.ftl`
- Test: `server/tests/test_monopoly.py`

**Step 1: Write the failing test**

```python
def test_monopoly_options_present_catalog_preset_choices():
    game = _create_two_player_game()
    host_player = game.players[0]
    options_action_set = game.get_action_set(host_player, "options")
    set_preset_action = options_action_set.get_action("set_preset_id")
    menu_options = game._get_menu_options_for_action(set_preset_action, host_player)
    assert "junior_modern" in menu_options
    assert "junior_legacy" in menu_options
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly.py::test_monopoly_options_present_catalog_preset_choices -v`
Expected: FAIL because options do not include `junior_modern` / `junior_legacy`.

**Step 3: Write minimal implementation**

```python
PRESET_LABEL_KEYS = {
    # ...
    "junior_modern": "monopoly-preset-junior-modern",
    "junior_legacy": "monopoly-preset-junior-legacy",
}
```

```fluent
monopoly-preset-junior-modern = Monopoly Junior (Modern)
monopoly-preset-junior-legacy = Monopoly Junior (Legacy)
```

**Step 4: Run test to verify it passes**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly.py::test_monopoly_options_present_catalog_preset_choices -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/locales/en/monopoly.ftl server/locales/pl/monopoly.ftl server/locales/pt/monopoly.ftl server/locales/ru/monopoly.ftl server/locales/vi/monopoly.ftl server/locales/zh/monopoly.ftl server/tests/test_monopoly.py
git commit -m "Add junior modern and legacy preset options"
```

### Task 2: Create Junior Ruleset Data Module With Anchor Metadata

**Files:**
- Create: `server/games/monopoly/junior_rules.py`
- Test: `server/tests/test_monopoly_junior_rules.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.junior_rules import get_junior_ruleset

def test_junior_ruleset_anchors_are_fixed():
    modern = get_junior_ruleset("junior_modern")
    legacy = get_junior_ruleset("junior_legacy")
    assert modern.anchor_edition_id == "monopoly-f8562"
    assert legacy.anchor_edition_id == "monopoly-00441"
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior_rules.py::test_junior_ruleset_anchors_are_fixed -v`
Expected: FAIL with module/file not found.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class JuniorRuleset:
    preset_id: str
    anchor_edition_id: str
    source_policy: str
    starting_cash: int
    pass_go_cash: int
    dice_count: int

JUNIOR_RULESETS = {
    "junior_modern": JuniorRuleset(
        preset_id="junior_modern",
        anchor_edition_id="monopoly-f8562",
        source_policy="anchor-first",
        starting_cash=0,  # replace with anchor-derived values in Task 3
        pass_go_cash=0,
        dice_count=1,
    ),
    "junior_legacy": JuniorRuleset(
        preset_id="junior_legacy",
        anchor_edition_id="monopoly-00441",
        source_policy="anchor-first",
        starting_cash=0,  # replace with anchor-derived values in Task 3
        pass_go_cash=0,
        dice_count=1,
    ),
}

def get_junior_ruleset(preset_id: str) -> JuniorRuleset:
    return JUNIOR_RULESETS[preset_id]
```

**Step 4: Run test to verify it passes**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior_rules.py::test_junior_ruleset_anchors_are_fixed -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/junior_rules.py server/tests/test_monopoly_junior_rules.py
git commit -m "Add junior ruleset anchor metadata module"
```

### Task 3: Fill Near-Complete Anchor Ruleset Values And Provenance Notes

**Files:**
- Modify: `server/games/monopoly/junior_rules.py`
- Create: `docs/plans/2026-02-26-monopoly-junior-anchor-notes.md`
- Test: `server/tests/test_monopoly_junior_rules.py`

**Step 1: Write the failing test**

```python
def test_junior_rulesets_define_core_fields():
    modern = get_junior_ruleset("junior_modern")
    legacy = get_junior_ruleset("junior_legacy")
    assert modern.starting_cash > 0
    assert legacy.starting_cash > 0
    assert modern.game_end_mode in {"bankruptcy", "board_complete", "timer"}
    assert legacy.game_end_mode in {"bankruptcy", "board_complete", "timer"}
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior_rules.py::test_junior_rulesets_define_core_fields -v`
Expected: FAIL due missing fields/zero placeholder values.

**Step 3: Write minimal implementation**

```python
@dataclass(frozen=True)
class JuniorRuleset:
    # ...
    game_end_mode: str
    rent_mode: str
    jail_mode: str
    cards_mode: str
    provenance_notes: tuple[str, ...]
```

```python
"junior_modern": JuniorRuleset(
    # ...
    game_end_mode="...",
    rent_mode="...",
    jail_mode="...",
    cards_mode="...",
    provenance_notes=(
        "Anchor manual: monopoly-f8562",
        "Conflict policy: anchor-first",
    ),
)
```

Also record conflict/fallback decisions in `docs/plans/2026-02-26-monopoly-junior-anchor-notes.md`.

**Step 4: Run test to verify it passes**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior_rules.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/junior_rules.py server/tests/test_monopoly_junior_rules.py docs/plans/2026-02-26-monopoly-junior-anchor-notes.md
git commit -m "Document and codify junior anchor rulesets"
```

### Task 4: Wire Junior Ruleset Selection On Game Start

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly.py`

**Step 1: Write the failing test**

```python
def test_monopoly_on_start_supports_junior_modern_alias():
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    assert game.active_preset_id == "junior_modern"
    assert game.active_anchor_edition_id == "monopoly-f8562"

def test_monopoly_on_start_supports_junior_legacy_alias():
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_legacy"))
    assert game.active_preset_id == "junior_legacy"
    assert game.active_anchor_edition_id == "monopoly-00441"
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly.py::test_monopoly_on_start_supports_junior_modern_alias tests/test_monopoly.py::test_monopoly_on_start_supports_junior_legacy_alias -v`
Expected: FAIL due fallback behavior/missing alias support.

**Step 3: Write minimal implementation**

```python
if self.options.preset_id in {"junior_modern", "junior_legacy"}:
    base = _catalog_get_preset("junior") or self._fallback_preset()
    alias_name = "Monopoly Junior (Modern)" if ... else "Monopoly Junior (Legacy)"
    anchor_id = "monopoly-f8562" if ... else "monopoly-00441"
    return MonopolyPreset(
        preset_id=self.options.preset_id,
        family_key="junior",
        name=alias_name,
        description="Junior anchor-mapped profile.",
        anchor_edition_id=anchor_id,
        edition_ids=tuple(base.edition_ids),
    )
```

**Step 4: Run test to verify it passes**

Run: same command as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly.py
git commit -m "Map junior modern and legacy preset aliases"
```

### Task 5: Add Junior Turn Dispatch And Dice Model

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly_junior.py`

**Step 1: Write the failing test**

```python
def test_junior_roll_uses_ruleset_dice_count(monkeypatch):
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    host = game.current_player
    rolls = iter([3])  # one die expected
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))
    game.execute_action(host, "roll_dice")
    assert game.turn_last_roll == [3]
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py::test_junior_roll_uses_ruleset_dice_count -v`
Expected: FAIL because current code always rolls two dice.

**Step 3: Write minimal implementation**

```python
def _is_junior_preset(self) -> bool:
    return self.active_preset_id in {"junior_modern", "junior_legacy"}

def _roll_dice_for_current_ruleset(self) -> list[int]:
    if self._is_junior_preset():
        return [random.randint(1, 6) for _ in range(self.junior_ruleset.dice_count)]
    return [random.randint(1, 6), random.randint(1, 6)]
```

Use this helper inside `_action_roll_dice`.

**Step 4: Run test to verify it passes**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior.py
git commit -m "Add junior turn dispatch and dice handling"
```

### Task 6: Implement Junior Economy, Purchase, And Rent Rules

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly_junior.py`

**Step 1: Write the failing test**

```python
def test_junior_modern_purchase_and_rent_follow_ruleset(monkeypatch):
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    host = game.current_player
    guest = game.players[1]
    # deterministic moves to buy then pay rent
    ...
    assert host.cash == ...
    assert guest.cash == ...
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py::test_junior_modern_purchase_and_rent_follow_ruleset -v`
Expected: FAIL due classic rent/buy logic path.

**Step 3: Write minimal implementation**

```python
def _calculate_junior_rent_due(self, space: MonopolySpace, owner_id: str) -> int:
    mode = self.junior_ruleset.rent_mode
    if mode == "anchor-modern":
        ...
    if mode == "anchor-legacy":
        ...
    return space.rent
```

Route unowned-property and rent-resolution through Junior handlers when `_is_junior_preset()`.

**Step 4: Run test to verify it passes**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior.py
git commit -m "Implement junior purchase and rent resolution"
```

### Task 7: Implement Junior Cards, Jail, And Special Space Rules

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly_junior.py`

**Step 1: Write the failing test**

```python
def test_junior_legacy_jail_behavior_uses_ruleset(monkeypatch):
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_legacy"))
    host = game.current_player
    host.in_jail = True
    ...
    assert host.in_jail is False
    assert host.cash == ...
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py::test_junior_legacy_jail_behavior_uses_ruleset -v`
Expected: FAIL due classic jail constants/flow.

**Step 3: Write minimal implementation**

```python
def _resolve_junior_card_effect(...):
    if self.junior_ruleset.cards_mode == "anchor-modern":
        ...
    elif self.junior_ruleset.cards_mode == "anchor-legacy":
        ...
```

```python
def _apply_junior_jail_rules(self, player: MonopolyPlayer, roll: list[int]) -> str:
    mode = self.junior_ruleset.jail_mode
    ...
```

**Step 4: Run test to verify it passes**

Run: same command as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior.py
git commit -m "Implement junior cards and jail rules"
```

### Task 8: Implement Junior Endgame And Winner Evaluation

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly_junior.py`

**Step 1: Write the failing test**

```python
def test_junior_modern_endgame_uses_anchor_policy():
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    # construct near-end state according to anchor rule
    ...
    game._check_junior_endgame()
    assert game.status == "finished"
    assert game.current_player.name == "Host"
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py::test_junior_modern_endgame_uses_anchor_policy -v`
Expected: FAIL because no Junior-specific endgame evaluator exists.

**Step 3: Write minimal implementation**

```python
def _check_junior_endgame(self) -> bool:
    mode = self.junior_ruleset.game_end_mode
    if mode == "board_complete":
        ...
    elif mode == "bankruptcy":
        ...
    if finished:
        self.status = "finished"
        self.game_active = False
        self.broadcast_l("monopoly-winner-by-bankruptcy", ...)
    return finished
```

Call this from Junior resolution points.

**Step 4: Run test to verify it passes**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior.py
git commit -m "Add junior endgame evaluation logic"
```

### Task 9: Gate Actions And Bot Logic For Junior Compatibility

**Files:**
- Modify: `server/games/monopoly/game.py`
- Test: `server/tests/test_monopoly_junior.py`

**Step 1: Write the failing test**

```python
def test_junior_hides_incompatible_actions():
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    host = game.current_player
    turn_set = game.get_action_set(host, "turn")
    assert turn_set.get_action("build_house").is_hidden_fn(host) != Visibility.VISIBLE
```

```python
def test_junior_bot_uses_junior_turn_path():
    game = _start_two_player_game(MonopolyOptions(preset_id="junior_modern"))
    host = game.current_player
    host.is_bot = True
    assert game.bot_think(host) in {"roll_dice", "buy_property", "end_turn"}
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py::test_junior_hides_incompatible_actions tests/test_monopoly_junior.py::test_junior_bot_uses_junior_turn_path -v`
Expected: FAIL due classic action visibility/bot heuristics.

**Step 3: Write minimal implementation**

```python
def _is_classic_only_action(self, action_id: str) -> bool:
    return action_id in {"build_house", "sell_house", "mortgage_property", ...}
```

```python
def bot_think(self, player: MonopolyPlayer) -> str | None:
    if self._is_junior_preset():
        return self._bot_think_junior(player)
    ...
```

**Step 4: Run test to verify it passes**

Run: same as Step 2
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior.py
git commit -m "Gate junior actions and bot decisions"
```

### Task 10: Full Verification And Regression Gate

**Files:**
- Modify: `server/tests/test_monopoly.py` (only if needed for updates)
- Modify: `server/tests/test_monopoly_junior.py` (stabilization only)
- Modify: `docs/plans/2026-02-26-monopoly-junior-anchor-notes.md` (if final clarifications are needed)

**Step 1: Write any missing failing regression test**

```python
def test_non_junior_presets_unaffected_by_junior_dispatch():
    game = _start_two_player_game(MonopolyOptions(preset_id="speed"))
    assert game.active_preset_id == "speed"
    assert not getattr(game, "junior_ruleset", None) or game.active_preset_id != "junior_modern"
```

**Step 2: Run test to verify it fails (if behavior regressed)**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly.py::test_non_junior_presets_unaffected_by_junior_dispatch -v`
Expected: FAIL only if regression exists; otherwise this step confirms no regression.

**Step 3: Write minimal implementation/fix (if needed)**

```python
if not self._is_junior_preset():
    self.junior_ruleset = None
```

**Step 4: Run full verification suite**

Run:

```bash
cd server && ../.venv/bin/pytest tests/test_monopoly_junior.py -v
cd server && ../.venv/bin/pytest tests/test_monopoly.py -v
cd server && ../.venv/bin/pytest -k monopoly -v
cd server && ../.venv/bin/pytest tests/test_integration.py::TestGameRegistryIntegration::test_pig_game_registered tests/test_integration.py::TestGameRegistryIntegration::test_get_by_category -v
```

Expected: PASS for all selected suites.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly.py server/tests/test_monopoly_junior.py server/games/monopoly/game.py docs/plans/2026-02-26-monopoly-junior-anchor-notes.md
git commit -m "Finalize junior modern and legacy variant implementation"
```

### Task 11: Final Documentation And PR Notes

**Files:**
- Modify: `docs/plans/2026-02-26-monopoly-junior-anchor-notes.md`
- Modify: `README.md` (if preset list/documentation lives here)

**Step 1: Write failing doc-check step**

Define expected docs checklist:
- both new preset IDs documented,
- anchor IDs documented,
- conflict policy documented.

**Step 2: Run doc check manually**

Run: `rg -n "junior_modern|junior_legacy|monopoly-f8562|monopoly-00441|anchor-first" README.md docs/plans/2026-02-26-monopoly-junior-anchor-notes.md`
Expected: all markers found.

**Step 3: Write minimal documentation updates**

```markdown
- junior_modern (anchor: monopoly-f8562)
- junior_legacy (anchor: monopoly-00441)
- Conflict policy: anchor-first
```

**Step 4: Re-run doc check**

Run: same as Step 2
Expected: all markers present.

**Step 5: Commit**

```bash
git add README.md docs/plans/2026-02-26-monopoly-junior-anchor-notes.md
git commit -m "Document junior variant anchors and policy"
```

## Done Definition

- `junior_modern` and `junior_legacy` are selectable in lobby.
- Both are playable with near-complete anchor-driven rules.
- Manual conflict and fallback decisions are explicitly recorded.
- Existing Monopoly preset behavior remains unchanged.
- All verification commands in Task 10 pass.
