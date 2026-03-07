# Monopoly Electronic Banking Design (2026-02-26)

## Goal

Implement a maximum-fidelity `electronic_banking` Monopoly preset using a deterministic in-game simulator and anchor-first manual policy.

## Confirmed Decisions

1. Next preset target: `electronic_banking`.
2. Fidelity target: maximum.
3. Banking layer approach: deterministic in-game simulator (no external integrations).
4. Source policy: anchor-first.
5. Architecture preference: dedicated banking simulator module with Monopoly bridge.

## Architecture

### High-Level Split

- `MonopolyGame` remains the board/turn orchestrator.
- New simulator module (`banking_sim.py`) becomes source of truth for money/account operations in this preset.
- Preset dispatch:
  - `electronic_banking`: economy routes through simulator.
  - all other presets: unchanged existing economy flow.

### Responsibilities

Simulator:

- account lifecycle and balances
- transfer/debit/credit validation
- transaction journaling
- deterministic state snapshots

Monopoly game:

- action/menu orchestration
- rent/tax/card/jail event routing into simulator
- localization/broadcast of operation outcomes
- score/winner checks using simulator balances

## Data Model

### Simulator Entities

- `BankAccount`
  - `player_id`, `card_id`, `balance`, `is_active`
- `BankTransaction`
  - `tx_id`, `kind`, `from_id`, `to_id`, `amount`, `reason`, `round`, `status`
- `BankingState`
  - account map, ordered transaction ledger, policy config, validation counters

### Preset Profile

Add `ElectronicBankingProfile` (anchor-driven), including:

- `anchor_edition_id`
- `starting_balance`
- `pass_go_credit_mode`
- `jail_payment_mode`
- `overdraft_or_shortfall_policy`
- transfer constraints and optional fees

### API Surface

Deterministic simulator operations:

- `init_accounts(players, profile)`
- `credit(player_id, amount, reason)`
- `debit(player_id, amount, reason)`
- `transfer(from_id, to_id, amount, reason)`
- `can_pay(player_id, amount)`
- `get_balance(player_id)`
- `snapshot()`

All failures return explicit typed reasons; no silent mutation failures.

## Runtime Flow

1. `on_start` (electronic banking):
   - resolve anchor profile
   - initialize banking accounts/cards
   - announce mode and initial balances
2. Turn/economy events:
   - rent/tax/fees -> `debit` or `transfer`
   - GO/card rewards -> `credit`
   - insolvency decisions based on simulator validations/policy
3. Banking actions:
   - balance check
   - allowed manual transfer flows
   - transaction history/ledger readout
4. Bot path:
   - decision heuristics read simulator balances, not raw cash
5. Endgame:
   - winner and tie-break computations use simulator balances and anchor policy

## Error Handling And Determinism

- Invalid operations return stable reason codes (e.g. insufficient funds, invalid target).
- Failed operations do not mutate balances or ledger state except explicit failed-attempt records.
- No external I/O or service dependencies in simulation path.
- Transaction IDs and ordering are deterministic in one game replay.
- Simulator state is fully serializable for save/load compatibility.

## Testing Strategy

### Unit

- simulator operation success/failure paths
- policy-boundary behavior (min/max, overdraft, transfer permissions)
- deterministic transaction sequencing

### Integration

- Monopoly rent/tax/pass-go/card/jail flows under `electronic_banking`
- action visibility/enabled gating for banking-only UI actions
- score sync and winner resolution from simulator balances

### Regression

- existing Monopoly preset suites (`classic`, `speed`, `builder`, `junior_*`, etc.) unchanged
- serialization compatibility for games started before banking state existed

## Acceptance Criteria

1. `electronic_banking` is fully playable with simulator-backed economy.
2. All economy mutations in this preset flow through simulator APIs.
3. Deterministic scripted runs reproduce identical balances and ledgers.
4. Localization covers success/failure banking events.
5. Existing Monopoly tests remain green.

## Out Of Scope

- Real external device/app integration.
- Locale-specific behavioral forks in this phase (anchor-first normalization applies).
- Non-electronic preset feature work.

## Next Step

Create a detailed task-by-task implementation plan with TDD sequencing via `writing-plans`.
