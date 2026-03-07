# Monopoly Special Boards Parity Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a wave-driven parity framework that upgrades all special Monopoly boards toward anchor-manual fidelity, including board-correct card decks and global sound-emulation hooks (excluding Pac-Man game-unit behavior).

**Architecture:** Add a central board parity manifest, then route deck/mechanic/audio behavior through capability-gated runtime branches. Deliver framework first, then promote board families in waves using deterministic tests and strict fallback safety (`skin_only` and missing-capability paths remain stable). Keep manual source policy anchor-first with explicit variant backlog notes.

**Tech Stack:** Python 3.11+, pytest/pytest-asyncio, existing Monopoly server runtime (`server/games/monopoly`), curated manual catalog artifacts.

---

### Task 1: Add Parity Manifest Scaffolding

**Files:**
- Create: `server/games/monopoly/board_parity.py`
- Create: `server/tests/test_monopoly_board_parity_manifest.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write the failing manifest contract tests**

```python
from server.games.monopoly.board_parity import (
    get_board_parity_profile,
    get_parity_board_ids,
)


def test_parity_manifest_contains_all_special_boards():
    ids = set(get_parity_board_ids())
    assert "mario_kart" in ids
    assert "junior_super_mario" in ids
    assert "star_wars_mandalorian" in ids


def test_parity_manifest_has_anchor_and_fidelity_fields():
    profile = get_board_parity_profile("mario_kart")
    assert profile.anchor_edition_id.startswith("monopoly-")
    assert profile.fidelity_status in {"partial", "partial_plus", "manual_core", "near_full"}
```

**Step 2: Run test to verify it fails**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_parity_manifest.py -v`  
Expected: FAIL because `board_parity.py` does not exist.

**Step 3: Write minimal implementation**

```python
@dataclass(frozen=True)
class BoardParityProfile:
    board_id: str
    rule_pack_id: str
    anchor_edition_id: str
    canonical_manual_edition_id: str
    fidelity_status: str
    deck_mode: str
    capability_ids: tuple[str, ...]
    hardware_capability_ids: tuple[str, ...]
```

Add an initial profile map for all currently onboarded special boards.

**Step 4: Run test to verify it passes**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_board_parity_manifest.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/board_parity.py server/tests/test_monopoly_board_parity_manifest.py server/games/monopoly/game.py
git commit -m "Add special-board parity manifest scaffold"
```

### Task 2: Add Deck Provider Framework (Classic + Board-Specific)

**Files:**
- Create: `server/games/monopoly/deck_provider.py`
- Create: `server/tests/test_monopoly_deck_provider.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing deck provider tests**

```python
from server.games.monopoly.deck_provider import resolve_deck_provider


def test_resolve_deck_provider_uses_classic_by_default():
    provider = resolve_deck_provider("mario_kart", deck_mode="classic")
    assert provider.mode == "classic"


def test_resolve_deck_provider_supports_board_specific_mode():
    provider = resolve_deck_provider("star_wars_mandalorian", deck_mode="board_specific")
    assert provider.mode == "board_specific"
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_deck_provider.py -v`  
Expected: FAIL (module missing).

**Step 3: Write minimal implementation**

Add provider interface:

```python
@dataclass(frozen=True)
class DeckProvider:
    board_id: str
    mode: str

def resolve_deck_provider(board_id: str, deck_mode: str) -> DeckProvider:
    return DeckProvider(board_id=board_id, mode=deck_mode if deck_mode in {"classic", "board_specific"} else "classic")
```

Wire `MonopolyGame` card draw path to query provider but keep functional behavior unchanged for now.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_deck_provider.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/deck_provider.py server/tests/test_monopoly_deck_provider.py server/games/monopoly/game.py
git commit -m "Add deck provider framework for board parity"
```

### Task 3: Add Global Hardware/Sound Emulation Framework

**Files:**
- Create: `server/games/monopoly/hardware_emulation.py`
- Create: `server/tests/test_monopoly_hardware_emulation.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing sound framework tests**

```python
from server.games.monopoly.hardware_emulation import (
    HardwareEvent,
    resolve_hardware_event,
)


def test_hardware_event_is_inert_when_sound_mode_none():
    event = HardwareEvent(board_id="star_wars_mandalorian", event_id="play_theme", payload={})
    result = resolve_hardware_event(event, sound_mode="none")
    assert result.status == "ignored"


def test_hardware_event_is_emulatable_when_sound_mode_emulated():
    event = HardwareEvent(board_id="star_wars_mandalorian", event_id="play_theme", payload={})
    result = resolve_hardware_event(event, sound_mode="emulated")
    assert result.status in {"emulated", "ignored"}
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_hardware_emulation.py -v`  
Expected: FAIL (module missing).

**Step 3: Write minimal implementation**

```python
@dataclass(frozen=True)
class HardwareEvent:
    board_id: str
    event_id: str
    payload: dict[str, object]

def resolve_hardware_event(event: HardwareEvent, sound_mode: str) -> HardwareResult:
    if sound_mode != "emulated":
        return HardwareResult(status="ignored")
    return HardwareResult(status="emulated")
```

Also add a Pac-Man guard comment and test ensuring Pac-Man game-unit behavior is not introduced here.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_hardware_emulation.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/hardware_emulation.py server/tests/test_monopoly_hardware_emulation.py server/games/monopoly/game.py
git commit -m "Add global hardware sound-emulation framework"
```

### Task 4: Add Parity Matrix Artifacts and Source Index

**Files:**
- Create: `docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md`
- Create: `server/games/monopoly/catalog/special_board_anchor_index.json`
- Create: `server/tests/test_monopoly_special_board_anchor_index.py`

**Step 1: Write failing index integrity tests**

```python
import json
from pathlib import Path


def test_anchor_index_has_unique_board_ids():
    data = json.loads(Path("games/monopoly/catalog/special_board_anchor_index.json").read_text())
    ids = [row["board_id"] for row in data]
    assert len(ids) == len(set(ids))


def test_anchor_index_excludes_pacman_game_unit():
    data = json.loads(Path("games/monopoly/catalog/special_board_anchor_index.json").read_text())
    assert all(row["board_id"] != "pacman" for row in data)
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_special_board_anchor_index.py -v`  
Expected: FAIL (missing files).

**Step 3: Write minimal implementation**

Create initial JSON rows for all current special boards with:
- `board_id`
- `anchor_edition_id`
- `canonical_manual_edition_id`
- `family`
- `fidelity_status`

Create human-readable matrix markdown reflecting the same data.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_special_board_anchor_index.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md server/games/monopoly/catalog/special_board_anchor_index.json server/tests/test_monopoly_special_board_anchor_index.py
git commit -m "Add special-board parity matrix and anchor index"
```

### Task 5: Wave 1 Board Promotion Framework (Star Wars Family Slice)

**Files:**
- Create: `server/tests/test_monopoly_wave_special_cards_star_wars.py`
- Modify: `server/games/monopoly/board_rules/star_wars_*.py` (targeted subset for first wave)
- Modify: `server/games/monopoly/board_rules_registry.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing Star Wars wave tests**

```python
def test_star_wars_wave_board_specific_deck_draw_changes_card_effect(monkeypatch):
    game = _start_board("star_wars_mandalorian")
    host = game.current_player
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    _force_roll_to_chance(game, host)
    game.execute_action(host, "roll_dice")
    assert host.cash != 50 + game.rule_profile.starting_cash
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_star_wars.py -v`  
Expected: FAIL (board-specific deck behavior not present).

**Step 3: Write minimal implementation**

- Add board-specific card maps for selected Star Wars boards.
- Register capability ids and deck mode in parity manifest.
- Route runtime through deck provider + capability gates.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_star_wars.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_wave_special_cards_star_wars.py server/games/monopoly/board_rules_registry.py server/games/monopoly/board_rules/star_wars_*.py server/games/monopoly/game.py
git commit -m "Promote first Star Wars special boards to board-specific card behavior"
```

### Task 6: Wave 1 Audio Event Wiring for Hardware-Enabled Boards

**Files:**
- Create: `server/tests/test_monopoly_wave_special_audio_star_wars.py`
- Modify: `server/games/monopoly/game.py`
- Modify: `server/games/monopoly/board_parity.py`
- Modify: `server/games/monopoly/hardware_emulation.py`

**Step 1: Write failing audio event tests**

```python
def test_star_wars_board_emits_hardware_event_in_emulated_sound_mode():
    game = _start_board("star_wars_mandalorian", sound_mode="emulated")
    host = game.current_player
    _force_board_event_turn(game, host)
    assert game._last_hardware_event_id == "star_wars_theme"
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_audio_star_wars.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

Emit normalized hardware events from board-gated runtime points and resolve via hardware framework.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_audio_star_wars.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_wave_special_audio_star_wars.py server/games/monopoly/game.py server/games/monopoly/board_parity.py server/games/monopoly/hardware_emulation.py
git commit -m "Wire wave-1 hardware audio events for special boards"
```

### Task 7: Wave 2 Promotion (Marvel + Disney Core Boards)

**Files:**
- Create: `server/tests/test_monopoly_wave_special_cards_marvel_disney.py`
- Modify: `server/games/monopoly/board_rules/marvel_*.py`
- Modify: `server/games/monopoly/board_rules/disney_*.py`
- Modify: `server/games/monopoly/board_parity.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing wave-2 behavior tests**

```python
def test_marvel_disney_wave_boards_use_anchor_card_content():
    ...
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_marvel_disney.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

Add board-specific card mappings and mechanical capability flags for selected Marvel/Disney boards.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_marvel_disney.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_wave_special_cards_marvel_disney.py server/games/monopoly/board_rules/marvel_*.py server/games/monopoly/board_rules/disney_*.py server/games/monopoly/board_parity.py server/games/monopoly/game.py
git commit -m "Promote wave-2 Marvel and Disney special board parity"
```

### Task 8: Long-Tail Board Family Promotions and Consistency Gates

**Files:**
- Create: `server/tests/test_monopoly_wave_special_cards_long_tail.py`
- Modify: `server/games/monopoly/board_rules/*.py` (long-tail targeted boards)
- Modify: `server/games/monopoly/board_parity.py`
- Modify: `docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md`

**Step 1: Write failing long-tail parity tests**

```python
def test_long_tail_special_boards_have_non_empty_parity_capabilities():
    ...
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_long_tail.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

Populate remaining board parity profiles and minimum anchor-accurate card capability mappings.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_wave_special_cards_long_tail.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_wave_special_cards_long_tail.py server/games/monopoly/board_rules/*.py server/games/monopoly/board_parity.py docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md
git commit -m "Promote long-tail special boards toward anchor parity"
```

### Task 9: Fallback Safety and Skin-Only Invariance

**Files:**
- Create: `server/tests/test_monopoly_special_board_fallback_safety.py`
- Modify: `server/games/monopoly/game.py`

**Step 1: Write failing safety tests**

```python
def test_skin_only_mode_bypasses_special_deck_and_audio_paths():
    ...

def test_missing_capability_falls_back_without_crash():
    ...
```

**Step 2: Run test to verify failure**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_special_board_fallback_safety.py -v`  
Expected: FAIL.

**Step 3: Write minimal implementation**

Harden runtime guards and defaults for missing profile/capability/deck/audio paths.

**Step 4: Run test to verify pass**

Run: `cd server && ../.venv/bin/pytest tests/test_monopoly_special_board_fallback_safety.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/tests/test_monopoly_special_board_fallback_safety.py server/games/monopoly/game.py
git commit -m "Harden special board fallback and skin-only safety"
```

### Task 10: Final Verification and Documentation Sync

**Files:**
- Modify: `docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md`
- Modify: `docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md` (if cross-wave notes need updates)

**Step 1: Run focused parity suites**

Run:

```bash
cd server && ../.venv/bin/pytest \
  tests/test_monopoly_board_parity_manifest.py \
  tests/test_monopoly_deck_provider.py \
  tests/test_monopoly_hardware_emulation.py \
  tests/test_monopoly_wave_special_cards_star_wars.py \
  tests/test_monopoly_wave_special_audio_star_wars.py \
  tests/test_monopoly_wave_special_cards_marvel_disney.py \
  tests/test_monopoly_wave_special_cards_long_tail.py \
  tests/test_monopoly_special_board_fallback_safety.py -v
```

Expected: PASS.

**Step 2: Run full Monopoly regression**

Run: `cd server && ../.venv/bin/pytest -k monopoly -v`  
Expected: PASS with no regressions.

**Step 3: Sync parity matrix statuses**

Update final per-board status columns and remaining backlog markers.

**Step 4: Commit**

```bash
git add docs/plans/2026-02-26-monopoly-special-boards-parity-matrix.md docs/plans/2026-02-26-monopoly-mario-board-anchor-notes.md
git commit -m "Finalize special board parity wave rollout status"
```

**Step 5: Verification-before-completion**

Apply `@verification-before-completion` discipline before completion claims and include test command summaries in handoff.

## Notes for Executor
- Keep all promoted behavior capability-gated and board-scoped.
- Preserve `skin_only` semantics as strict fallback behavior.
- Enforce anchor-first policy and record manual variant differences in docs, not runtime branching.
- Do not add Pac-Man game-unit emulation logic in this plan.
