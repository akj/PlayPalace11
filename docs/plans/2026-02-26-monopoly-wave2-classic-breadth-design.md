# Monopoly Wave 2 Classic Breadth Design

Date: 2026-02-26
Branch: `monopoly`
Status: approved

## Goal
Expand board-profile coverage beyond Mario by onboarding a high-demand Wave 2 set of 25 classic-themed boards with stable fallback behavior.

## Final Decisions
1. Strategy: breadth-first expansion.
2. Batch size: Top 25 boards.
3. Selection policy: popularity + franchise priority.
4. Scope: classic boards only in Wave 2.
5. Runtime mode: new Wave 2 boards are marked `partial` so `auto` engages board-rules path and explicit fallback notice is emitted.

## Scope
### In scope
- Add 25 classic-themed board profiles.
- Add matching rule-pack stubs and registry entries.
- Keep runtime behavior deterministic via existing fallback contract.
- Update backlog status for these 25 boards.
- Add matrix and regression tests.

### Out of scope
- Junior wave expansion in this batch.
- Deep board-specific mechanics per board.
- Large gameplay rewrites.

## Architecture
Build on existing `board_profile` + `board_rules_registry` + `MonopolyGame` board resolver architecture.

### Wave 2 contract
- Each new board profile:
  - `compatible_preset_ids = ("classic_standard",)`
  - `fallback_preset_id = "classic_standard"`
  - `rule_pack_status = "partial"`
- Each rule-pack is minimal and deterministic in this wave.
- Runtime fallback priority remains:
  1. implemented board capability
  2. board-pack fallback behavior
  3. base classic behavior

## Components and Data Flow
1. Curate Top 25 list into a source file for wave tracking.
2. Extend `board_profile.py` with 25 entries.
3. Extend `board_rules_registry.py` and add 25 rule-pack modules.
4. Reuse existing startup resolution and announcement paths.
5. Update themed backlog statuses from `not_started` to `partial_rules` for selected rows.

No new gameplay branch is required if existing capability gates and fallback semantics already cover the batch.

## Error Handling and UX Contracts
- Incompatibility auto-fix remains active: non-classic preset + Wave 2 board -> switch to `classic_standard` with announcement.
- In `auto` mode, Wave 2 boards resolve to `board_rules` and emit simplification notice when mechanics are not deeply implemented.
- Board selector behavior remains unchanged except for expanded options.

## Testing Strategy
### Unit
- `board_profile` resolution for Wave 2 boards.
- `board_rules_registry` pack and capability lookups.

### Integration
- Parametrized startup matrix for all 25 board IDs.
- One incompatibility auto-fix sample test for Wave 2 boards.
- One `skin_only` override test remains in place as guardrail.

### Regression
- Focused board tests pass.
- `pytest -k monopoly -v` passes.
- Integration smoke tests pass.

## Wave 2 Top 25 (Classic)
| board_id | edition_id | franchise bucket |
|---|---|---|
| `disney_princesses` | `monopoly-b4644` | Disney |
| `disney_animation` | `monopoly-c2116` | Disney |
| `disney_lion_king` | `monopoly-e6707` | Disney |
| `disney_mickey_friends` | `monopoly-f5267` | Disney |
| `disney_villains` | `monopoly-f0091` | Disney |
| `disney_lightyear` | `monopoly-f8046` | Disney/Pixar |
| `marvel_80_years` | `monopoly-e7866` | Marvel |
| `marvel_avengers` | `monopoly-e6504` | Marvel |
| `marvel_spider_man` | `monopoly-f3968` | Marvel |
| `marvel_black_panther_wf` | `monopoly-f5405` | Marvel |
| `marvel_super_villains` | `monopoly-f5270` | Marvel |
| `marvel_deadpool` | `monopoly-e2033` | Marvel |
| `star_wars_40th` | `monopoly-c1990` | Star Wars |
| `star_wars_boba_fett` | `monopoly-f5394` | Star Wars |
| `star_wars_light_side` | `monopoly-f8383` | Star Wars |
| `star_wars_the_child` | `monopoly-f2013` | Star Wars |
| `star_wars_mandalorian` | `monopoly-f1276` | Star Wars |
| `star_wars_complete_saga` | `monopoly-e8066` | Star Wars |
| `harry_potter` | `monopoly-f9422` | Wizarding World |
| `fortnite` | `monopoly-e6603` | Fortnite |
| `stranger_things` | `monopoly-c4550` | Stranger Things |
| `jurassic_park` | `monopoly-f1662` | Jurassic |
| `lord_of_the_rings` | `monopoly-f1663` | LOTR |
| `animal_crossing` | `monopoly-f1661` | Nintendo |
| `barbie` | `monopoly-g0038` | Barbie |

## Backlog Policy
- For these 25 rows: status becomes `partial_rules`.
- Remaining rows stay as-is.
- Future waves can promote each board to `full_rules` with anchor-backed mechanics incrementally.

## Risks and Mitigations
1. Risk: large board list introduces mapping mistakes.
   - Mitigation: strict table-driven generation + matrix tests.
2. Risk: users expect unique mechanics immediately.
   - Mitigation: explicit simplification notice and clear wave contract.
3. Risk: regressions across existing presets.
   - Mitigation: feature-gated board hooks and full monopoly regression run.

## Success Criteria
1. 25 additional classic boards are selectable.
2. All 25 resolve deterministically in `auto` mode with fallback semantics.
3. Compatibility auto-fix and announcements remain correct.
4. Backlog statuses updated for selected 25.
5. Full Monopoly regression remains green.
