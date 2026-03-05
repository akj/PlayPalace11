# Monopoly Junior Super Mario Manual-Core Design

Date: 2026-02-26  
Branch: `monopoly`  
Status: approved

## Goal
Implement the `junior_super_mario` board in `board_rules` mode using the official `monopoly-f4817` manual core rules, while keeping existing non-Mario Junior behavior stable.

## Source of Truth
- Anchor edition: `monopoly-f4817`
- Manual: `F48170000_INST_MN_Jr_SuperMario_I.pdf`
- Policy: anchor-first, manual-literal for implemented behavior.

## Scope
### In scope
- Manual-core runtime behavior for `junior_super_mario` in `board_rules` mode.
- Preset routing so Mario Junior board always activates Junior ruleset runtime.
- Deterministic Power-Up die behavior for digital no-sound path.
- Lightweight sound-ready hooks for later sound-enabled expansion.
- Integration and regression coverage.

### Out of scope
- Full bespoke sound-enabled power die implementation in this wave.
- Full custom Power-Up card deck beyond manual-core actions needed for Time Out exit.
- UI redesign.

## Final Decisions
1. `junior_super_mario` manual behavior only applies when:
   - board is `junior_super_mario`
   - effective board mode is `board_rules`
   - board rule pack advertises a Junior manual capability gate.
2. Board fallback preset for `junior_super_mario` is `junior_modern` (not `junior`) to ensure Junior ruleset activation.
3. Existing `junior` behavior for non-Mario-junior gameplay remains unchanged.
4. Sound integration is deferred, but extension hooks are added now.

## Manual-Core Runtime Contract
Under the `junior_super_mario` manual gate:
- Roll both dice each turn.
- Move by the numbered die only.
- Resolve Power-Up die through a deterministic digital no-sound mapping.
- If player lands on Go To Time Out and has no coins, do not move to Time Out.
- If in Time Out, player may exit by:
  - spending one coin, or
  - using one eligible card,
  then rolling both dice and taking the turn.
- Unowned properties:
  - if affordable: buy immediately
  - if not affordable: no purchase, no auction
- Payment pressure:
  - rent/card/tax can partial-pay without forcing bankruptcy in this board path
- Endgame:
  - when all properties are owned
  - winner by highest coins
  - tie-break by most owned properties

## Architecture
### Board and rule-pack metadata
- `server/games/monopoly/board_profile.py`
  - change `junior_super_mario.fallback_preset_id` to `junior_modern`
- `server/games/monopoly/board_rules/junior_super_mario.py`
  - add capability constants for manual-core gate and sound-ready hook
- `server/games/monopoly/board_rules_registry.py`
  - advertise `junior_manual_core`
  - advertise sound-ready capability placeholder

### Runtime integration
Add Mario-Junior-specific helpers in `server/games/monopoly/game.py`:
- capability checks:
  - `_is_junior_super_mario_manual_core_active()`
- economy and flow:
  - `_apply_junior_super_mario_starting_cash_by_player_count()`
  - `_resolve_junior_super_mario_powerup_outcome(...)`
  - `_resolve_junior_super_mario_powerup_sound_outcome(...)` (stub for future)
  - `_can_enter_timeout_with_current_cash(...)`
  - `_resolve_junior_super_mario_timeout_turn_start(...)`
  - `_resolve_junior_super_mario_unowned_property(...)`
  - `_apply_junior_super_mario_partial_payment(...)`
  - `_finish_junior_super_mario_endgame(...)`

Manual-core branches are isolated to this board + mode + capability gate so other presets remain unaffected.

## Data Flow
1. Game start:
   - resolve board plan
   - apply board preset autofix to `junior_modern` when needed
   - initialize player coins via Mario Junior player-count table (`2->20`, `3->18`, `4+->16`)
2. Turn start:
   - if player is in Time Out, resolve card-or-coin exit rule
3. Roll:
   - roll numbered + power-up die
   - move by numbered die value
4. Space resolution:
   - unowned purchasable -> auto-buy if affordable, else no-op
   - payments -> partial-pay handling for this board path
   - Go To Time Out -> blocked when cash is zero
5. Post-move power-up:
   - apply deterministic no-sound mapping outcome
6. Endgame:
   - if all properties owned, determine winner by coins then property-count tie-break.

## Power-Up Die (No-Sound Digital Mapping)
Default mapping for this phase:
- `roll_numbered_die_again`: weight 1
- `collect_1`: weight 2
- `collect_2`: weight 2
- `collect_3`: weight 2
- `nothing`: weight 1

This reflects manual no-sound style behavior and remains deterministic and testable.

## Sound-Ready Hooks (Phase 2)
Add now, not enabled yet:
- capability placeholder in rule-pack metadata (e.g., `junior_powerup_sound_ready`)
- runtime stub method:
  - returns `None` unless future sound mode is active
  - no behavior change in this phase

Future phase can switch Power-Up resolution source from no-sound mapping to sound outcome mapping without rewriting turn loop.

## Error Handling and Fallbacks
- If board mode is `skin_only`, skip all Mario manual behavior.
- If capability gate missing, use existing junior/default runtime behavior.
- If helper returns invalid outcome, default to no-op and continue turn safely.
- Preserve menu rebuild and score sync patterns after each state mutation.

## Testing Strategy
### Unit/contract tests
- registry capabilities for `junior_super_mario` include manual-core and sound-ready flags.
- board profile fallback for `junior_super_mario` resolves to `junior_modern`.

### Integration tests
- startup coins follow `20/18/16` table by player count.
- roll uses two dice but movement uses numbered die.
- Go To Time Out blocked at zero coins.
- Time Out exit by one coin and by card path.
- unowned property auto-buy if affordable; no auction if not affordable.
- partial-pay path does not bankrupt under manual-core board mode.
- all properties owned triggers endgame and tie-break by properties.

### Regression tests
- existing `junior_modern` and `junior_legacy` suites stay green.
- existing Mario board suites stay green.
- Monopoly regression suite stays green.

## Risks and Mitigations
1. Risk: touching generic Junior logic could regress non-Mario junior.
   - Mitigation: strict board+mode+capability gating and focused regression tests.
2. Risk: turn-state deadlocks from replacing pending purchase with auto-buy.
   - Mitigation: explicit turn-state reset checks in tests after purchase/no-purchase branches.
3. Risk: ambiguous manual wording around power-up outcomes.
   - Mitigation: keep deterministic no-sound mapping documented and isolated; phase-2 hooks for future refinements.

## Success Criteria
1. `junior_super_mario` board in `board_rules` follows manual-core contract above.
2. Non-Mario presets and non-board-rules mode behavior remain unchanged.
3. Sound-ready extension hooks exist with zero runtime behavior change today.
4. Targeted and regression test suites pass.
