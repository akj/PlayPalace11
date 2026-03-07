# Monopoly Core Cleanliness Action-Layer Design

Date: 2026-03-02
Branch: `monopoly`
Status: approved

## Goal
Refactor Monopoly action-layer code to match the core cleanliness patterns used by other games, while preserving gameplay, save/load behavior, action wiring, and tests.

## Scope
### In scope
- Low-risk modular split of Monopoly action logic.
- Keep all existing action ids and public handler/guard method names in `MonopolyGame`.
- Move internals behind delegation into `server/games/monopoly/actions/`.
- No behavior changes.

### Out of scope
- Rules or gameplay changes.
- Save payload shape changes.
- Large architecture shifts (mixins, declarative action generation, stateful service rewrite) in this phase.

## Constraints
- Compatibility target is strict:
  - Gameplay behavior unchanged.
  - Save/load shape unchanged.
  - Existing tests continue passing.
- Preserve:
  - action ids
  - handler method names
  - keybind mappings
  - menu/input wiring
  - guard error keys and visibility behavior

## Approaches Considered
1. Facade extraction (selected):
   - Keep `MonopolyGame` public surface as-is.
   - Add focused action modules and delegate.
   - Lowest regression risk.
2. Table-driven action generation:
   - Cleaner long-term metadata model.
   - Higher immediate migration risk.
3. Stateful action service object:
   - Strong encapsulation.
   - Larger integration blast radius.

## Selected Architecture
Add `server/games/monopoly/actions/` with focused modules:
- `handlers.py`: `_action_*` behavior
- `guards.py`: `_is_*_enabled` and `_is_*_hidden`
- `options.py`: menu option providers and bot-select helpers used by action inputs
- `labels.py`: dynamic labels where needed

`MonopolyGame` remains the source of truth for game state and continues exposing the same public action methods. Each method becomes a thin delegate to module functions that receive `game: MonopolyGame` and existing args.

## Data Flow
- State ownership remains on `MonopolyGame` dataclass fields.
- New modules are stateless helper layers only.
- Delegates read/write existing fields directly through `game`.

## Error Handling
- Preserve current guard-return error codes and visibility outputs exactly.
- Preserve early-return behavior inside handlers.
- No exception-handling behavior changes in this phase.

## Verification Strategy
For each extraction slice:
1. Run Monopoly-focused tests.
2. Run representative cross-game tests to validate shared framework stability.
3. Validate guard/menu behavior equivalence for touched actions.
4. Revert or fix immediately if any behavior delta appears.

## Execution Order
1. Extract `banking_*` and `voice_command` action family.
2. Extract `auction_*` action family.
3. Extract property-management family (`mortgage`, `unmortgage`, `build_house`, `sell_house`).
4. Extract trade/jail/end-turn family.
5. Extract `roll_dice` last due to highest branching complexity.
6. Commit incrementally after each verified slice.

## Success Criteria
1. Monopoly action-layer code is split into focused modules under `actions/`.
2. No gameplay/save-load/user-visible behavior regressions.
3. Existing tests remain green for Monopoly and selected cross-game checks.
4. `monopoly/game.py` becomes materially easier to navigate due to delegation boundaries.
