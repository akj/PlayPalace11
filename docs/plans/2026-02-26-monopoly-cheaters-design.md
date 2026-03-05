# Monopoly Cheaters Design (2026-02-26)

## Goal

Implement a full-fidelity `cheaters` preset with deterministic cheat detection/resolution driven by anchor-first rules from `monopoly-e4888`.

## Confirmed Decisions

1. Next preset target: `cheaters`.
2. Fidelity target: full.
3. Implementation style: event-driven plugin layer.
4. Source policy: `anchor-first`.
5. Chosen approach: modular cheater engine with detector hooks invoked by `MonopolyGame`.

## Anchor Context

- Preset id: `cheaters`
- Anchor edition id: `monopoly-e4888`
- Policy: `anchor-first`

## Architecture

### High-Level Split

- Add `cheaters_profile.py` for anchor-driven config and detector policy.
- Add `cheaters_engine.py` for deterministic event evaluation and outcomes.
- Keep `MonopolyGame` as orchestration layer; it emits events and applies outcomes.

### Preset Routing

- `cheaters`:
  - initializes cheaters profile + engine
  - applies engine checks at key action boundaries
- all other presets:
  - no cheaters engine active
  - no behavior changes

### Design Constraint

Only implement anchor-backed mechanics detectable from existing game state/events (YAGNI for v1).

## Components and Data Flow

### CheatersProfile

Fields:

- `preset_id`
- `anchor_edition_id`
- `source_policy`
- `enabled_rules`
- `reward_amounts`
- `penalty_amounts`
- `escalation_thresholds`
- `provenance_notes`

Resolver:

- `resolve_cheaters_profile("cheaters")` returning anchor-first defaults for `monopoly-e4888`.

### CheatersEngine

Deterministic evaluator with limited runtime state:

- per-turn strike counters
- required-step flags (rolled/payment-required markers)
- optional reward/claim cooldown flags

Core API shape:

- `on_turn_start(player_id, turn_index)`
- `on_action_attempt(player_id, action_id, context)`
- `on_payment_required(player_id, reason, amount, context)`
- `on_payment_result(player_id, paid, required, context)`
- `on_turn_end_attempt(player_id, context)`

Return model:

- `CheaterOutcome`
  - `status` (`allow`, `block`, `penalty`, `reward`)
  - `cash_delta`
  - `message_key`
  - `reason_code`

### MonopolyGame Bridge

- Emits engine events before/after relevant actions.
- Applies outcomes through existing helpers for cash/debt/bankruptcy and messaging.
- Base action executes only when engine does not block.

## Runtime Rules and UX

### Rule Categories (v1)

- Turn-order cheating:
  - ending turn before required steps -> block + penalty.
- Payment cheating:
  - attempts that bypass required rent/tax flow -> block; repeated attempts escalate.
- Movement/sequence cheating:
  - invalid sequencing attempts -> block + strike.
- Reward windows:
  - deterministic reward events if anchor behavior allows it.

### Outcome Handling

- `allow`: continue normal action flow.
- `block`: cancel action, announce reason.
- `penalty`: debit via existing economy/debt path.
- `reward`: credit via existing bank helper and announce.

### Escalation

- per-turn strike count tracked by engine
- threshold-based higher penalty from profile
- reset at turn start

### UX

- Normal action menu remains primary interface.
- No extra command syntax required.
- Clear localized messaging for blocked cheat attempts, penalties, rewards, escalation.

## Error Handling and Determinism

- Fail-safe behavior:
  - if detector cannot evaluate context, return `allow` with no mutation.
- Atomic outcome application:
  - apply one `cash_delta`, sync scores, then message.
- Bankruptcy safety:
  - penalties go through existing bankruptcy/debt logic.
- Deterministic engine:
  - no random detector decisions.
  - same event sequence yields same outcomes.

## Testing Strategy

### Unit Tests (`cheaters_engine`)

- detector outcome matrix (allow/block/penalty/reward)
- escalation thresholds
- deterministic replay assertions

### Integration Tests (`MonopolyGame` + `cheaters`)

- startup initializes profile/engine
- blocked early end-turn + penalty
- blocked payment-bypass attempts
- reward path behavior (if anchor-backed)
- non-cheaters presets unaffected

### Regression

- full Monopoly suite remains green (`pytest -k monopoly -v`)
- integration smoke checks remain green

## Acceptance Criteria

1. `cheaters` preset initializes anchor-driven profile and engine.
2. Anchor-backed cheat rules enforce deterministic block/penalty/reward outcomes.
3. Penalties/rewards use core economy helpers with safe bankruptcy behavior.
4. Localized feedback clearly communicates detector results.
5. All existing Monopoly regression tests remain green.

## Out of Scope

- Non-anchor speculative cheat mechanics.
- Non-deterministic or AI/NLP detector behavior.
- Cross-preset cheat engine behavior changes outside `cheaters`.
