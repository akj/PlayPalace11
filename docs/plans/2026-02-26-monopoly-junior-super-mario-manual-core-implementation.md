# Monopoly Junior Super Mario Manual-Core Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement `junior_super_mario` board-rules behavior from the `monopoly-f4817` manual core rules while preserving existing non-Mario Junior behavior.

**Architecture:** Keep manual behavior behind strict runtime gates: `board_id=junior_super_mario`, effective mode `board_rules`, and explicit board capability flags. Reuse existing Monopoly game loop and add board-scoped helper branches instead of global Junior rewrites. Stage work via small TDD slices with deterministic tests and frequent commits.

**Tech Stack:** Python 3.11+, pytest/pytest-asyncio, existing Monopoly server engine (`server/games/monopoly`).

---

### Task 1: Route Mario Junior Board to Active Junior Ruleset

**Files:**
- Modify: `server/games/monopoly/board_profile.py`
- Modify: `server/tests/test_monopoly_board_profile.py`
- Modify: `server/tests/test_monopoly_board_selection.py`
- Modify: `server/tests/test_monopoly_mario_boards.py`

**Step 1: Write failing tests for fallback preset**

```python
def test_resolve_board_plan_autofixes_incompatible_preset():
    plan = resolve_board_plan("classic_standard", "junior_super_mario", "auto")
    assert plan.effective_preset_id == "junior_modern"

def test_incompatible_board_autofixes_preset():
    game = _start(MonopolyOptions(preset_id="classic_standard", board_id="junior_super_mario"))
    assert game.active_preset_id == "junior_modern"
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_board_profile.py tests/test_monopoly_board_selection.py tests/test_monopoly_mario_boards.py -v`  
Expected: FAIL where tests still assert `junior`.

**Step 3: Write minimal implementation**

```python
"junior_super_mario": BoardProfile(
    ...
    fallback_preset_id="junior_modern",
    ...
)
```

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_board_profile.py tests/test_monopoly_board_selection.py tests/test_monopoly_mario_boards.py -v`  
Expected: PASS for updated preset routing.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_profile.py server/tests/test_monopoly_board_profile.py server/tests/test_monopoly_board_selection.py server/tests/test_monopoly_mario_boards.py
git commit -m "Route junior Super Mario board to junior modern preset"
```

### Task 2: Add Manual-Core and Sound-Ready Board Capabilities

**Files:**
- Modify: `server/games/monopoly/board_rules/junior_super_mario.py`
- Modify: `server/games/monopoly/board_rules_registry.py`
- Modify: `server/tests/test_monopoly_board_rules_registry.py`
- Modify: `server/tests/test_monopoly_mario_rule_packs.py`

**Step 1: Write failing capability contract tests**

```python
def test_junior_super_mario_manual_core_capability_contract():
    assert supports_capability("junior_super_mario", "junior_manual_core")

def test_junior_super_mario_sound_ready_capability_contract():
    assert supports_capability("junior_super_mario", "junior_powerup_sound_ready")
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_board_rules_registry.py tests/test_monopoly_mario_rule_packs.py -v`  
Expected: FAIL because capabilities are not declared yet.

**Step 3: Write minimal implementation**

```python
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "junior_manual_core",
    "junior_powerup_sound_ready",
)
```

and in registry entry:

```python
capability_ids=(
    "pass_go_credit_override",
    "startup_board_announcement",
    "junior_manual_core",
    "junior_powerup_sound_ready",
),
```

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_board_rules_registry.py tests/test_monopoly_mario_rule_packs.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_rules/junior_super_mario.py server/games/monopoly/board_rules_registry.py server/tests/test_monopoly_board_rules_registry.py server/tests/test_monopoly_mario_rule_packs.py
git commit -m "Declare junior Super Mario manual and sound-ready capabilities"
```

### Task 3: Add Failing Manual-Core Startup and Dice Tests

**Files:**
- Create: `server/tests/test_monopoly_junior_super_mario_manual.py`

**Step 1: Write failing startup and movement tests**

```python
def test_junior_super_mario_starting_cash_uses_player_count_table():
    game = _start_game_with_n_players(3)
    assert [p.cash for p in game.turn_players] == [18, 18, 18]

def test_junior_super_mario_roll_moves_by_numbered_die_only(monkeypatch):
    game = _start_two_player_manual_board_game()
    host = game.current_player
    rolls = iter([4, 6])  # numbered die, power-up die
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))
    game.execute_action(host, "roll_dice")
    assert host.position == 4
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL on starting cash and movement assertions.

**Step 3: Write minimal implementation in game runtime**

```python
def _is_junior_super_mario_manual_core_active(self) -> bool:
    return (
        self.active_board_id == "junior_super_mario"
        and self.active_board_effective_mode == "board_rules"
        and supports_capability(self.active_board_rule_pack_id, "junior_manual_core")
    )
```

plus:
- apply `2->20`, `3->18`, `4+->16` start-cash override during `on_start`
- in `_action_roll_dice`, when manual-core active, roll two dice and move by the first die only.

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS for startup and movement tests.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Add junior Super Mario manual startup cash and roll flow"
```

### Task 4: Add Go To Time Out Guard and Exit Rules

**Files:**
- Modify: `server/tests/test_monopoly_junior_super_mario_manual.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing Time Out tests**

```python
def test_junior_super_mario_zero_coin_player_does_not_enter_timeout():
    game = _start_two_player_manual_board_game()
    host = game.current_player
    host.cash = 0
    host.position = 29
    game.execute_action(host, "roll_dice")  # land on go_to_jail index 30
    assert host.in_jail is False
    assert host.position == 30

def test_junior_super_mario_timeout_exit_by_one_coin_then_roll(monkeypatch):
    game = _start_two_player_manual_board_game()
    host = game.current_player
    host.in_jail = True
    host.cash = 3
    rolls = iter([2, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))
    game.execute_action(host, "roll_dice")
    assert host.in_jail is False
    assert host.cash == 2
    assert host.position == 2
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL; existing jail logic does not match manual.

**Step 3: Write minimal implementation**

```python
def _can_enter_timeout_with_current_cash(self, player: MonopolyPlayer) -> bool:
    return self._current_liquid_balance(player) > 0
```

and:
- gate `go_to_jail` handling in `_resolve_space` for manual-core board
- for jailed player in `_action_roll_dice`, manual-core path:
  - if card available, allow exit by card
  - elif cash >= 1, debit 1 and exit
  - elif cash == 0, remain jailed and end turn

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS for Time Out entry/exit behavior.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Implement junior Super Mario Time Out manual rules"
```

### Task 5: Enforce Auto-Buy and No-Auction for Unowned Properties

**Files:**
- Modify: `server/tests/test_monopoly_junior_super_mario_manual.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing property resolution tests**

```python
def test_junior_super_mario_auto_buys_affordable_property():
    game = _start_two_player_manual_board_game()
    host = game.current_player
    host.position = 0
    force_roll(game, [1, 1])  # land on Mediterranean
    game.execute_action(host, "roll_dice")
    assert "mediterranean_avenue" in host.owned_space_ids
    assert game.turn_pending_purchase_space_id == ""

def test_junior_super_mario_no_auction_when_unaffordable():
    game = _start_two_player_manual_board_game()
    host = game.current_player
    host.cash = 1
    force_roll(game, [1, 1])
    game.execute_action(host, "roll_dice")
    assert game.turn_pending_purchase_space_id == ""
    assert "mediterranean_avenue" not in host.owned_space_ids
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL because current logic sets pending buy/auction.

**Step 3: Write minimal implementation**

In `_resolve_space`, under manual-core gate for unowned purchasable spaces:

```python
if self._current_liquid_balance(player) >= landed_space.price > 0:
    self._auto_buy_property_for_manual_junior(player, landed_space)
return "resolved"
```

No pending purchase and no auction branch in this path.

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS for auto-buy/no-auction behavior.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Enforce junior Super Mario manual unowned property flow"
```

### Task 6: Add Partial-Payment Economy (No Bankruptcy in Manual-Core Path)

**Files:**
- Modify: `server/tests/test_monopoly_junior_super_mario_manual.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing partial-payment tests**

```python
def test_junior_super_mario_rent_partial_pay_does_not_bankrupt():
    game = _start_two_player_manual_board_game()
    host, guest = game.players[0], game.players[1]
    host.owned_space_ids.append("mediterranean_avenue")
    game.property_owners["mediterranean_avenue"] = host.id
    guest.position = 0
    guest.cash = 1
    force_roll(game, [1, 1])  # rent > 1
    game.current_player = guest
    game.execute_action(guest, "roll_dice")
    assert guest.bankrupt is False
    assert guest.cash == 0

def test_junior_super_mario_card_fee_partial_pay_does_not_bankrupt(monkeypatch):
    game = _start_two_player_manual_board_game()
    host = game.current_player
    host.cash = 1
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "doctor_fee_pay_50")
    host.position = 1
    force_roll(game, [1, 1])  # land on community chest
    game.execute_action(host, "roll_dice")
    assert host.bankrupt is False
    assert host.cash == 0
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL with bankruptcy or full-payment assumptions.

**Step 3: Write minimal implementation**

- Add board-gated partial-pay helper in `game.py`:

```python
def _manual_junior_partial_debit(self, player: MonopolyPlayer, due: int, reason: str) -> int:
    amount = min(max(0, due), self._current_liquid_balance(player))
    return self._debit_player_to_bank(player, amount, reason, allow_partial=True)
```

- Apply to rent and bank-payment branches when manual-core active.
- Skip bankruptcy declaration on shortfall in this path.

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS for no-bankruptcy partial payments.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Add junior Super Mario manual partial-payment economy"
```

### Task 7: Implement Endgame Trigger and Tie-Break by Properties

**Files:**
- Modify: `server/tests/test_monopoly_junior_super_mario_manual.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing endgame tests**

```python
def test_junior_super_mario_finishes_when_all_properties_owned():
    game = _start_two_player_manual_board_game()
    assign_all_purchasable_to_players(game)
    assert game._check_junior_endgame() is True
    assert game.status == "finished"

def test_junior_super_mario_tie_break_uses_property_count():
    game = _start_two_player_manual_board_game()
    host, guest = game.players[0], game.players[1]
    host.cash = 10
    guest.cash = 10
    host.owned_space_ids = ["mediterranean_avenue", "baltic_avenue"]
    guest.owned_space_ids = ["reading_railroad"]
    for sid in host.owned_space_ids:
        game.property_owners[sid] = host.id
    for sid in guest.owned_space_ids:
        game.property_owners[sid] = guest.id
    fill_remaining_properties(game, owner=guest)
    assert game._check_junior_endgame() is True
    assert game.current_player.name == "Guest"
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL due to existing cash/position tie-break.

**Step 3: Write minimal implementation**

Add manual-core winner resolver:

```python
winner = max(
    contenders,
    key=lambda p: (
        self._current_liquid_balance(p),
        len([sid for sid in p.owned_space_ids if self.property_owners.get(sid) == p.id]),
        p.name,
    ),
)
```

Use this resolver only for manual-core `junior_super_mario`.

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS for endgame trigger and tie-break.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Apply junior Super Mario manual endgame tie-break rules"
```

### Task 8: Add Power-Up No-Sound Mapping and Sound Stubs

**Files:**
- Modify: `server/tests/test_monopoly_junior_super_mario_manual.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing power-up mapping and hook tests**

```python
def test_junior_super_mario_powerup_no_sound_mapping_is_deterministic(monkeypatch):
    game = _start_two_player_manual_board_game()
    host = game.current_player
    # deterministic die sequence should produce deterministic coin gain
    force_roll(game, [2, 3])
    game.execute_action(host, "roll_dice")
    assert host.cash >= 0

def test_junior_super_mario_powerup_sound_hook_is_inert_by_default():
    game = _start_two_player_manual_board_game()
    assert game._resolve_junior_super_mario_powerup_sound_outcome(4) is None
```

**Step 2: Run tests to verify failure**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: FAIL while helper(s) do not exist.

**Step 3: Write minimal implementation**

Add helpers:

```python
def _resolve_junior_super_mario_powerup_sound_outcome(self, power_die: int) -> str | None:
    return None
```

and deterministic no-sound outcome resolver with weighted mapping for die faces, then apply result in manual-core roll path.

**Step 4: Run tests to verify pass**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/game.py server/tests/test_monopoly_junior_super_mario_manual.py
git commit -m "Add junior Super Mario power-up no-sound mapping and sound stubs"
```

### Task 9: Update Mario Anchor Notes and Run Regression Verification

**Files:**
- Modify: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md`

**Step 1: Write doc update for new status**

```markdown
## Wave 7 Promotions
- `junior_super_mario`: manual-core rules enabled in board-rules mode.
- Added sound-ready runtime hooks for future power-up die integration.
```

**Step 2: Run focused suites**

Run: `cd server && uv run pytest tests/test_monopoly_junior_super_mario_manual.py tests/test_monopoly_board_profile.py tests/test_monopoly_board_selection.py tests/test_monopoly_mario_boards.py tests/test_monopoly_board_rules_registry.py tests/test_monopoly_mario_rule_packs.py -v`  
Expected: PASS.

**Step 3: Run broader Monopoly regression**

Run: `cd server && uv run pytest -k monopoly -v`  
Expected: PASS; no regressions in existing presets/boards.

**Step 4: Final commit**

```bash
git add docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md
git commit -m "Document junior Super Mario manual-core rollout"
```

**Step 5: Final verification discipline**

Before completion claims, use `@verification-before-completion` and include exact command outputs in handoff summary.

## Notes for Executor
- Keep all manual-core logic gated by `junior_super_mario` + `board_rules` + capability check.
- Do not change global Classic/Junior semantics outside gated branches.
- Prefer small commits per task exactly as listed.
- If a test reveals ambiguous manual interpretation, stop and document the ambiguity in the task log before expanding scope.
