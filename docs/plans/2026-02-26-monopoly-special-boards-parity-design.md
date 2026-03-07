# Monopoly Special Boards Parity Design

Date: 2026-02-26  
Branch: `monopoly`  
Status: approved

## Goal
Advance all non-classic Monopoly special boards from broad partial support toward manual-accurate behavior, including board-correct card decks and a global sound-emulation framework for hardware-driven editions (excluding Pac-Man game-unit behavior).

## Final Decisions
1. Delivery model: wave-based parity rollout by franchise/family, not one giant all-at-once push.
2. Card/manual policy: one canonical anchor manual per board (`anchor-first`, typically `en-us`).
3. Sound strategy: build one global sound-emulation framework now; activate per board only when manuals explicitly require hardware/audio behavior.
4. Pac-Man game-unit behavior remains explicitly out of scope.

## Scope
### In scope
- System-wide parity framework for:
  - board-specific deck content and card effects
  - capability-gated special mechanics
  - hardware/audio emulation hooks (`sound_mode=none|emulated`)
- Wave-by-wave board promotions from `partial` to deeper fidelity tiers.
- Parity tracking matrix with per-board progress and anchor source provenance.

### Out of scope
- Full Pac-Man game-unit gameplay emulation.
- UI redesigns unrelated to rule/mechanic parity.

## Current Baseline
- All special boards are onboarded and selectable.
- Most boards remain `partial` with pass-GO/startup behavior.
- Deeper deterministic card/manual behavior currently exists mainly in Mario boards.

## Architecture
### 1) Board parity manifest
Add a board parity profile layer keyed by `rule_pack_id` containing:
- canonical anchor edition/manual identifiers
- deck source mode (`classic`, `board_specific`, mixed)
- mechanic capability flags
- hardware/audio capability flags
- fidelity status (`partial`, `partial_plus`, `manual_core`, `near_full`)

This manifest becomes the central source for rollout state and runtime dispatch.

### 2) Deck framework
Extend existing card runtime to support:
- full board-specific deck definitions (not only remaps/amount overrides)
- deterministic card effect mapping per anchor manual
- compatibility fallback to classic behavior where deck coverage is incomplete

Existing hooks (`card_id_remap`, `card_cash_override`) remain supported as low-risk capability channels.

### 3) Mechanics capability framework
Keep behavior isolated through capability gates. Organize special mechanics into reusable buckets:
- movement/position routing overrides
- purchase/rent/economy overrides
- endgame/winner resolution overrides
- token/item/board-unit interactions

Only active capabilities for the current board+mode can affect runtime.

### 4) Global sound-emulation framework
Introduce a shared hardware event abstraction:
- board mechanics emit normalized hardware events
- runtime resolves events through `sound_mode`:
  - `none` (default safe fallback)
  - `emulated` (manual-mapped audio behavior)

Boards opt in via manifest capability flags; unsupported/unknown hardware paths stay inert.
Pac-Man game-unit is explicitly excluded.

## Source Policy
- Anchor-first: one canonical manual per board.
- Conflict handling:
  - document variant differences for later backlog
  - do not block canonical runtime implementation on cross-locale consensus

## Rollout Strategy
### Wave 1
- ship parity manifest scaffolding
- ship global deck framework support
- ship global sound-emulation framework
- promote first non-Mario family (recommended: Star Wars due breadth)

### Wave 2
- promote Marvel + Disney core boards with anchor-accurate decks and key mechanics
- wire hardware/audio flags where manuals require them

### Wave 3+
- complete long-tail boards and collector variants
- promote remaining boards to `manual_core`/`near_full`

## Per-Board Definition of Done
1. Canonical manual anchor recorded.
2. Board deck contents and card outcomes match anchor manual.
3. Board mechanics mapped through capability gates.
4. Sound-emulation path present when manual includes hardware/audio rules.
5. Focused tests and Monopoly regression pass.

## Data Flow (Promoted Board)
1. Resolve board selection, mode, and rule pack.
2. Load board parity manifest entry.
3. Select deck provider (`classic` or board-specific).
4. Apply capability-gated mechanics in turn resolution.
5. Emit hardware events when supported.
6. Resolve audio through `sound_mode` (`none` or `emulated`).

## Quality Gates
- No board rule promotion without:
  - anchor manual citation
  - deterministic failing-then-passing tests
  - `skin_only` fallback verification
- Each wave must include:
  - focused board suite
  - `-k monopoly` regression
  - parity matrix/status update

## Testing Strategy
- Contract tests: manifest/schema integrity and capability declarations.
- Integration tests: startup routing, deck draws, board mechanic deltas.
- Regression tests: unaffected boards/presets stay stable.
- Sound tests: hardware event emission and inert fallback when emulation is disabled.

## Tracking and Documentation
Maintain a parity matrix covering all special boards with:
- board id and anchor manual
- deck completeness status
- mechanics completeness status
- audio completeness status
- current rollout wave target

## Risks and Mitigations
1. Risk: broad cross-board changes cause regressions.
   - Mitigation: strict capability gating + wave-scoped rollout + regression runs each wave.
2. Risk: manual ambiguity across print variants.
   - Mitigation: canonical anchor-first policy and explicit variant backlog records.
3. Risk: sound framework complexity expands scope too early.
   - Mitigation: default inert mode (`none`), activate only for promoted boards with explicit manual support.

## Success Criteria
1. System can represent board-specific deck content and special mechanics for all special boards.
2. Wave rollout predictably increases board fidelity toward manual parity.
3. Hardware/audio support is framework-ready and safely disabled by default unless opted in.
4. Pac-Man game-unit remains excluded without blocking broader parity progress.
