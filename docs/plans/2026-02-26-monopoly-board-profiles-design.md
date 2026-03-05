# Monopoly Board Profiles Design

Date: 2026-02-26
Branch: `monopoly`
Status: approved

## Goal
Add board-level selection for Monopoly so players can choose themed boards (starting with Mario), with a dual-mode runtime that supports both:
- skin-only board behavior
- board-rules behavior (auto-applied when available)

The design must scale toward eventual coverage of all themed boards while keeping one stable `MonopolyGame` runtime.

## Final Decisions
1. Runtime must support both skin-only and board-rules behavior.
2. Default behavior is auto-apply board rules when a rule-pack exists; otherwise use skin-only.
3. Wave 1 targets Mario boards first.
4. Keep `preset_id` and add separate `board_id` lobby option.
5. On `preset_id`/`board_id` incompatibility, auto-switch to a compatible preset and announce it.
6. For incomplete board rule-packs, apply implemented capabilities and fall back to base preset behavior with explicit simplification notice.
7. Track non-Wave-1 boards in a backlog so full coverage can follow.

## Scope
### In scope
- Board profile abstraction (`board_id` + metadata)
- Resolver for effective runtime plan
- Dual-mode behavior (`auto`/`skin_only`)
- Wave 1 Mario board onboarding path
- Compatibility auto-fix and announcements
- Partial rule-pack fallback contract
- Backlog tracking for all remaining themed boards

### Out of scope
- Full implementation of all non-Mario special boards in Wave 1
- Replacing preset model entirely
- UI redesign beyond needed lobby options/messages

## Architecture
Use a Board Profile Registry + Rule-Pack Resolver.

### Core idea
- Keep `MonopolyGame` as the single runtime entrypoint.
- Introduce board-level configuration as data-first profiles.
- Resolve `{preset_id, board_id, board_rules_mode}` to one normalized runtime decision:
  - effective preset
  - effective board
  - effective mode (`skin_only` vs `board_rules`)
  - simplification/fallback flags

### Why this approach
- Scales to many boards without exploding preset count.
- Preserves current preset architecture and tests.
- Supports gradual rule-pack rollout (partial -> full) per board.

## Components
### 1) Board Profile Module (`board_profile.py`)
Defines board metadata and compatibility:
- `board_id`
- label/localization key
- compatible preset ids
- fallback preset id
- anchor edition id
- optional `rule_pack_id`
- `rule_pack_status` (`none`, `partial`, `full`)

Provides resolver:
- validates selected board
- applies preset auto-fix on incompatibility
- resolves effective mode for `board_rules_mode=auto`

### 2) Board Rules Registry (`board_rules_registry.py`)
Maps `rule_pack_id` to capability handlers and completeness metadata.
Example capabilities:
- pass-go economy modifiers
- deck/card substitutions
- rent/value adjustments
- board-specific events/triggers

### 3) Rule-Pack Modules (Wave 1)
- `board_rules/mario_kart.py`
- `board_rules/mario_celebration.py`
- `board_rules/mario_movie.py`
- `board_rules/junior_super_mario.py`

Each pack advertises supported capabilities and deterministic fallbacks for missing ones.

### 4) `MonopolyGame` Integration
On start:
- resolve effective board plan
- resolve effective preset (may auto-fix)
- resolve effective mode
- initialize board rule context if applicable

During gameplay:
- call board-rule hooks only when effective mode is `board_rules`
- if capability not implemented, route to base preset behavior and mark simplification

## Data Flow
1. Host chooses `preset_id`, `board_id`, and optional `board_rules_mode`.
2. Resolver computes normalized runtime plan.
3. Game start announces effective preset/board/mode and any auto-fix.
4. Runtime executes base preset logic + board hooks (if enabled).
5. Missing capability -> deterministic fallback to base logic.
6. If partial pack is active, emit one explicit simplification notice.

## UX and Contracts
### Lobby options
- keep existing `preset_id`
- add `board_id`
- add `board_rules_mode` with values:
  - `auto` (default)
  - `skin_only`

### Compatibility behavior
- On mismatch, auto-switch preset to board-compatible preset.
- Emit a clear announcement including old preset, new preset, and selected board.

### Incomplete rule-pack behavior
- `auto` + partial pack:
  - apply implemented capabilities
  - fallback missing capabilities to preset base rules
  - announce "simplified board rules active"

## Error Handling
Fallback priority:
1. selected board capability implementation
2. board pack declared fallback
3. preset base behavior

All board hooks must remain deterministic and non-destructive to existing presets.

## Testing Strategy
### Unit
- board profile resolver
  - compatibility success
  - mismatch auto-fix
  - mode resolution
- rules registry
  - capability lookup
  - partial/full status checks

### Integration
- `MonopolyGame` start resolves board plan correctly
- incompatibility auto-fix announcement emitted
- `auto` mode executes available board-rule hooks
- missing capability falls back to preset behavior + simplification notice

### Wave 1 Mario coverage
- at least one anchor-backed behavior test per Mario board
- at least one fallback-path test per Mario board

### Regression
- full Monopoly suite remains green
- City/Cheaters/Voice/Junior remain unchanged unless selected by resolved board plan

### Localization
- new board/mode messages added across required locales

## Wave 1 Board Set
Initial boards:
- Monopoly Gamer Mario Kart (`monopoly-e1870`)
- Monopoly Super Mario Celebration (`monopoly-e9517`)
- Monopoly Super Mario Bros. Movie Edition (`monopoly-f6818`)
- Monopoly Super Mario Bros. Collector's Edition (`monopoly-c4382`)
- Monopoly Junior Super Mario Edition (`monopoly-f4817`)

## Backlog Policy (All Remaining Special Boards)
Maintain a dedicated backlog table for every themed board not yet onboarded with status values:
- `not_started`
- `skin_only_ready`
- `partial_rules`
- `full_rules`

This backlog is required so Wave 1 can expand to full themed-board coverage incrementally.

## Risks and Mitigations
1. Risk: compatibility complexity across presets
   - Mitigation: strict resolver normalization + auto-fix contract
2. Risk: partial rule-packs confuse players
   - Mitigation: explicit simplification announcement and visible mode state
3. Risk: preset regressions
   - Mitigation: feature-gated hooks + full Monopoly regression tests

## Success Criteria
1. Players can select boards independently from presets.
2. `auto` mode applies board rules when available and safely falls back when not.
3. Wave 1 Mario boards are onboarded with deterministic behavior contracts.
4. Compatibility auto-fix works and is announced.
5. Backlog exists for all other themed boards to reach full coverage over time.
