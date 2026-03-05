# Monopoly Junior Anchor Notes (2026-02-26)

## Canonical Anchors

- `junior_modern`: `monopoly-f8562`
- `junior_legacy`: `monopoly-00441`

## Source Policy

- Rule resolution policy: `anchor-first`
- Conflict fallback: anchor family evidence -> Junior consensus -> deterministic safe default

## Implemented Decisions

1. Junior presets are modeled as explicit aliases (`junior_modern`, `junior_legacy`) instead of overloading `junior`.
2. Shared Junior engine with profile dispatch is used to avoid duplicate game loops.
3. Junior actions disable classic-only systems (buildings, mortgages, private trades).
4. One-die movement is enforced for both anchored Junior presets.
5. Endgame policies diverge by anchor:
   - modern: property pool exhaustion (or max rounds) then highest-cash winner
   - legacy: bankruptcy-driven elimination path
