# Monopoly Wave 4 Mario Hybrid Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add deterministic Mario board-rule depth for `mario_kart` and `mario_movie` using card remap and card cash override capabilities while preserving safe fallbacks for all other boards.

**Architecture:** Extend the board rules capability contract in `board_rules_registry.py`, then consume those capabilities inside `MonopolyGame._resolve_card_effect`. Keep hooks strictly gated by `board_rules` mode and `supports_capability(...)` checks so `skin_only` and non-Mario boards remain unchanged. Promote only two strict Mario packs this wave; leave the rest on partial safe fallback.

**Tech Stack:** Python 3.13, dataclasses, existing Monopoly engine in `server/games/monopoly/game.py`, pytest, localized message system.

---

### Task 1: Add failing registry tests for new card capabilities

**Files:**
- Modify: `server/tests/test_monopoly_board_rules_registry.py`

**Step 1: Write the failing tests**

```python
from server.games.monopoly.board_rules_registry import (
    get_card_cash_override,
    get_card_id_remap,
    get_rule_pack,
    supports_capability,
)


def test_mario_kart_card_id_remap_contract():
    assert get_card_id_remap("mario_kart", "chance", "bank_dividend_50") == "advance_to_go"


def test_card_id_remap_falls_back_to_original_card():
    assert get_card_id_remap("mario_kart", "chance", "does_not_exist") == "does_not_exist"


def test_mario_movie_card_cash_override_contract():
    assert get_card_cash_override("mario_movie", "bank_dividend_50") == 120


def test_card_cash_override_returns_none_when_missing():
    assert get_card_cash_override("mario_movie", "advance_to_go") is None
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`
Expected: FAIL with import errors for `get_card_id_remap` / `get_card_cash_override`.

**Step 3: Keep tests only (no implementation yet)**

No code implementation in this task.

**Step 4: Re-run to confirm failure state is stable**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`
Expected: FAIL for missing registry helpers.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_board_rules_registry.py
git commit -m "Add failing tests for board card capabilities"
```

### Task 2: Implement registry helpers and advertise capabilities

**Files:**
- Modify: `server/games/monopoly/board_rules_registry.py`

**Step 1: Implement minimal helper functions + capability ads**

```python
# For mario_kart capability_ids add:
"card_id_remap",

# For mario_movie capability_ids add:
"card_cash_override",


def get_card_id_remap(rule_pack_id: str, deck_type: str, card_id: str) -> str:
    module = RULE_PACK_MODULES.get(rule_pack_id)
    if module is None:
        return card_id
    remaps = getattr(module, "CARD_ID_REMAPS", None)
    if not isinstance(remaps, dict):
        return card_id
    value = remaps.get((deck_type, card_id))
    if isinstance(value, str) and value:
        return value
    return card_id


def get_card_cash_override(rule_pack_id: str, card_id: str) -> int | None:
    module = RULE_PACK_MODULES.get(rule_pack_id)
    if module is None:
        return None
    overrides = getattr(module, "CARD_CASH_OVERRIDES", None)
    if not isinstance(overrides, dict):
        return None
    value = overrides.get(card_id)
    if isinstance(value, int):
        return max(0, value)
    return None
```

**Step 2: Run tests to verify expected assertion failures now point to missing module constants**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`
Expected: FAIL on assertion values (helpers exist, data still missing in Mario modules).

**Step 3: Keep implementation minimal and deterministic**

Do not add runtime hooks yet.

**Step 4: Re-run tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_rules_registry.py -v`
Expected: same FAIL points.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules_registry.py
git commit -m "Add board card capability lookup helpers"
```

### Task 3: Add failing Mario rule-pack contract tests

**Files:**
- Modify: `server/tests/test_monopoly_mario_rule_packs.py`

**Step 1: Write failing tests for module-level mappings**

```python
from server.games.monopoly.board_rules import mario_kart, mario_movie


def test_mario_kart_exports_card_id_remap_mapping():
    assert mario_kart.CARD_ID_REMAPS[("chance", "bank_dividend_50")] == "advance_to_go"


def test_mario_movie_exports_card_cash_override_mapping():
    assert mario_movie.CARD_CASH_OVERRIDES["bank_dividend_50"] == 120
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py -v`
Expected: FAIL with missing `CARD_ID_REMAPS` / `CARD_CASH_OVERRIDES`.

**Step 3: Keep failing tests only**

No implementation changes in this task.

**Step 4: Re-run failing tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py -v`
Expected: same FAIL.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_mario_rule_packs.py
git commit -m "Add failing Mario module card capability tests"
```

### Task 4: Implement Mario module mappings

**Files:**
- Modify: `server/games/monopoly/board_rules/mario_kart.py`
- Modify: `server/games/monopoly/board_rules/mario_movie.py`

**Step 1: Add deterministic capability data to Mario modules**

```python
# mario_kart.py
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
)
CARD_ID_REMAPS = {
    ("chance", "bank_dividend_50"): "advance_to_go",
}
CARD_CASH_OVERRIDES = {}

# mario_movie.py
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_cash_override",
)
CARD_ID_REMAPS = {}
CARD_CASH_OVERRIDES = {
    "bank_dividend_50": 120,
}
```

**Step 2: Run module + registry tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py tests/test_monopoly_board_rules_registry.py -v`
Expected: PASS.

**Step 3: Keep scope tight**

Do not alter `mario_collectors`, `mario_celebration`, or `junior_super_mario` in this task.

**Step 4: Re-run tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py tests/test_monopoly_board_rules_registry.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules/mario_kart.py server/games/monopoly/board_rules/mario_movie.py
git commit -m "Add Mario card capability mappings"
```

### Task 5: Add failing integration tests for Mario Kart card remap

**Files:**
- Modify: `server/tests/test_monopoly_mario_boards.py`

**Step 1: Add two integration tests for remap vs skin-only**

```python
def test_mario_kart_board_rules_remaps_card_to_advance_to_go(monkeypatch):
    game = _start_two_player_game(
        MonopolyOptions(
            preset_id="classic_standard",
            board_id="mario_kart",
            board_rules_mode="auto",
        )
    )
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))

    game.execute_action(host, "roll_dice")

    assert host.position == 0
    assert host.cash == 1700


def test_mario_kart_skin_only_keeps_original_card(monkeypatch):
    game = _start_two_player_game(
        MonopolyOptions(
            preset_id="classic_standard",
            board_id="mario_kart",
            board_rules_mode="skin_only",
        )
    )
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))

    game.execute_action(host, "roll_dice")

    assert host.position == 7
    assert host.cash == 1550
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`
Expected: FAIL because runtime does not yet apply card remap capability.

**Step 3: Keep tests only in this task**

No runtime changes yet.

**Step 4: Re-run and confirm same failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`
Expected: same remap assertion failures.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_mario_boards.py
git commit -m "Add failing Mario Kart card remap integration tests"
```

### Task 6: Implement runtime hook for card ID remap

**Files:**
- Modify: `server/games/monopoly/game.py`

**Step 1: Add remap helper and integrate in card effect flow**

```python
from .board_rules_registry import (
    get_card_cash_override,
    get_card_id_remap,
    get_pass_go_credit_override,
    supports_capability,
)


def _resolve_board_card_id(self, deck_type: str, card_id: str) -> str:
    if self.active_board_effective_mode != "board_rules":
        return card_id
    rule_pack_id = self.active_board_rule_pack_id
    if not rule_pack_id:
        return card_id
    if not supports_capability(rule_pack_id, "card_id_remap"):
        return card_id
    return get_card_id_remap(rule_pack_id, deck_type, card_id)
```

Use it at start of `_resolve_card_effect`:

```python
card_id = self._resolve_board_card_id(deck_type, card_id)
```

**Step 2: Run remap integration tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py::test_mario_kart_board_rules_remaps_card_to_advance_to_go tests/test_monopoly_mario_boards.py::test_mario_kart_skin_only_keeps_original_card -v`
Expected: PASS.

**Step 3: Ensure unrelated tests remain green for touched areas**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_rule_packs.py tests/test_monopoly_board_rules_registry.py -v`
Expected: PASS.

**Step 4: Re-run full Mario board integration file**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py -v`
Expected: PASS except upcoming cash-override tests not yet added.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py
git commit -m "Apply board card remap capability in Monopoly runtime"
```

### Task 7: Add failing integration tests for Mario Movie cash override

**Files:**
- Modify: `server/tests/test_monopoly_mario_boards.py`

**Step 1: Add cash override behavior tests**

```python
def test_mario_movie_board_rules_applies_card_cash_override(monkeypatch):
    game = _start_two_player_game(
        MonopolyOptions(
            preset_id="classic_standard",
            board_id="mario_movie",
            board_rules_mode="auto",
        )
    )
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))

    game.execute_action(host, "roll_dice")

    assert host.cash == 1620


def test_mario_movie_skin_only_uses_default_card_cash(monkeypatch):
    game = _start_two_player_game(
        MonopolyOptions(
            preset_id="classic_standard",
            board_id="mario_movie",
            board_rules_mode="skin_only",
        )
    )
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))

    game.execute_action(host, "roll_dice")

    assert host.cash == 1550
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py::test_mario_movie_board_rules_applies_card_cash_override tests/test_monopoly_mario_boards.py::test_mario_movie_skin_only_uses_default_card_cash -v`
Expected: FAIL for board-rules override assertion.

**Step 3: Keep failing tests only**

No runtime code changes in this task.

**Step 4: Re-run to confirm stable failure**

Run: same as Step 2.
Expected: same FAIL.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_mario_boards.py
git commit -m "Add failing Mario Movie cash override integration tests"
```

### Task 8: Implement runtime hook for card cash overrides

**Files:**
- Modify: `server/games/monopoly/game.py`

**Step 1: Add cash override helper and apply on fixed-cash card branches**

```python
def _resolve_board_card_cash(self, card_id: str, default_amount: int) -> int:
    amount = max(0, default_amount)
    if self.active_board_effective_mode != "board_rules":
        return amount
    rule_pack_id = self.active_board_rule_pack_id
    if not rule_pack_id:
        return amount
    if not supports_capability(rule_pack_id, "card_cash_override"):
        return amount
    override = get_card_cash_override(rule_pack_id, card_id)
    if override is None:
        return amount
    return max(0, override)
```

Apply helper in `_resolve_card_effect` at least for:
- `bank_dividend_50`
- `poor_tax_15`
- `bank_error_collect_200`
- `doctor_fee_pay_50`
- `income_tax_refund_20`

**Step 2: Run targeted cash override tests**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py::test_mario_movie_board_rules_applies_card_cash_override tests/test_monopoly_mario_boards.py::test_mario_movie_skin_only_uses_default_card_cash -v`
Expected: PASS.

**Step 3: Run combined Mario coverage for touched behavior**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_mario_boards.py tests/test_monopoly_mario_rule_packs.py tests/test_monopoly_board_rules_registry.py -v`
Expected: PASS.

**Step 4: Re-run board profile/rules smoke around selected boards**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_profile.py tests/test_monopoly_board_selection.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py
git commit -m "Apply board card cash override capability in Monopoly runtime"
```

### Task 9: Update Mario notes with Wave 4 promotion status and next targets

**Files:**
- Modify: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`

**Step 1: Add Wave 4 note section**

Add a section:

```markdown
## Wave 4 Promotions
- `mario_kart`: added `card_id_remap` behavior (partial_rules+)
- `mario_movie`: added `card_cash_override` behavior (partial_rules+)

## Next Mario Targets
1. Promote `mario_collectors` with one card capability.
2. Promote `mario_celebration` with one card capability.
3. Define Junior-safe mechanic plan for `junior_super_mario`.
```

**Step 2: Run quick docs sanity check**

Run: `rg -n "Wave 4 Promotions|Next Mario Targets|card_id_remap|card_cash_override" docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`
Expected: PASS with line matches.

**Step 3: Keep docs update scoped**

Do not alter unrelated backlog statuses in this task.

**Step 4: Re-run sanity check**

Run: same `rg` command as Step 2.
Expected: PASS.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md
git commit -m "Document Wave 4 Mario capability promotions"
```

### Task 10: Full verification and final Wave 4 commit hygiene

**Files:**
- Verify touched files from Tasks 1-9

**Step 1: Run focused Wave 4 verification suite**

Run:

```bash
cd server && ../.venv/bin/pytest \
  tests/test_monopoly_board_rules_registry.py \
  tests/test_monopoly_mario_rule_packs.py \
  tests/test_monopoly_mario_boards.py -v
```

Expected: PASS.

**Step 2: Run Monopoly regression sweep**

Run: `cd server && ../.venv/bin/pytest -k monopoly -v`
Expected: PASS (or existing known skips/deselects only).

**Step 3: Use @verification-before-completion checklist**

- Confirm test command outputs are captured in terminal.
- Confirm `git status --short --branch` is clean.
- Confirm no uncommitted generated artifacts.

**Step 4: Final evidence check**

Run:

```bash
git status --short --branch
git log --oneline -12
```

Expected: clean branch and ordered Wave 4 commits.

**Step 5: Final commit only if needed**

If any remaining staged changes:

```bash
git add <remaining-files>
git commit -m "Finalize Wave 4 Mario hybrid integration"
```

If branch is already clean: no-op.
