# Monopoly Wave 5 Mario Collectors Promotion Design

Date: 2026-02-26
Branch: `monopoly`
Status: approved

## Goal
Promote `mario_collectors` from pass-go-only partial behavior to a richer partial profile by enabling both card remap and card cash override capabilities.

## Scope
### In scope
- `mario_collectors` capability additions:
  - `card_id_remap`
  - `card_cash_override`
- Deterministic mappings:
  - `("chance", "go_back_three") -> "bank_dividend_50"`
  - `"bank_error_collect_200" -> 250`
- Unit and integration coverage for board-rules vs skin-only behavior.

### Out of scope
- `mario_celebration` promotion in this wave.
- New capability types in runtime/registry.

## Architecture
Wave 4 introduced generic runtime hooks for card remap and card cash override. Wave 5 only supplies data in the `mario_collectors` rule-pack module and verifies end-to-end behavior through tests.

## Data Flow
1. Drawn card goes through `card_id_remap` when `board_rules` mode is active.
2. Resolved card cash effects go through `card_cash_override` when supported.
3. `skin_only` path bypasses both capabilities.

## Success Criteria
1. Collectors remap changes Chance behavior in `board_rules` mode only.
2. Collectors cash override changes Community Chest amount in `board_rules` mode only.
3. Monopoly regression remains green.
