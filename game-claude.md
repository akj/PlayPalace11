# PlayPalace Monopoly Handoff (for Claude)

## Session Goal
Continue Monopoly special-board parity/hardware audio work without losing context.

## Current Git State
- Repo: `/home/alek/git/PlayPalace`
- Branch: `monopoly`
- Worktree: clean
- Latest commit: `a7b80e2` (`Refine themed card text on 19 boards for currency consistency`)

## Recent Commit Chain (newest first)
- *(pending)* Add Disney Lion King Pride Rock pass-GO hardware celebration event
- `a7b80e2` Refine themed card text on 19 boards for currency consistency
- `cdff1f9` Seed universal card text, add cash override evidence, and fix merge import breakage
- `8da4b3f` Merge branch 'main' into monopoly

## What Is Done
- All 55 special boards are `manual_core`.
- Hardware audio framework is in place with original/placeholder fallback.
- Legal-source stand-in assets are installed and documented.
- Deterministic Mario Celebration Question Block mechanic (4 outcomes, hardware events).
- Jurassic Park Electronic Gate mechanic (theme/roar pass-GO payout).
- Full card text coverage: all 10 cards per board (550 total) now have `text` fields.
  - Universal cards: advance_to_go, go_to_jail, get_out_of_jail_free (seeded earlier).
  - Non-universal cards: bank_dividend_50, go_back_three, poor_tax_15, bank_error_collect_200, doctor_fee_pay_50, income_tax_refund_20 (329 new text fields).
- Themed card text refinement: 19 boards have themed non-universal card text matching their universal text style.
  - Star Wars (12): `$X` → `X Credits`
  - Mario (4) / Pokemon (1) / Transformers (1): `$` dropped
  - Disney Princesses (1): Portuguese translation with `A` prefix notation
- Full `text_note` evidence coverage: every card across all boards has evidence annotations.
- Cash override evidence metadata on all 29 boards with `CARD_CASH_OVERRIDES`.
- OCR quality grades documented for all 5 OCR sidecar boards.
- Added/updated tests for registry, parity, hardware resolver, card text coverage, and wave audio behavior.

## Current Hardware Events
- `play_theme`
- `star_wars_theme`
- `junior_coin_sound_powerup`
- `mario_question_block_coin_ping`
- `mario_question_block_bowser`
- `mario_question_block_power_up`
- `mario_question_block_game_over`
- `jurassic_park_gate_theme`
- `jurassic_park_gate_roar`
- `pride_rock_celebration`

## Key Files To Start From
- `server/games/monopoly/game.py`
- `server/games/monopoly/hardware_emulation.py`
- `server/games/monopoly/board_rules_registry.py`
- `server/games/monopoly/board_rules/mario_celebration.py`
- `server/tests/test_monopoly_card_text_coverage.py`
- `client/sounds/game_monopoly_hardware/README.md`
- `docs/plans/2026-02-26-monopoly-special-boards-final-part-status.md`
- `docs/plans/2026-02-28-monopoly-hardware-audio-legal-shortlist.md`

## Last Verification Results
- Hardware audio tests: `37 passed`
- Full monopoly suite: `1548 passed, 99 skipped`
- Card text coverage tests: `231 passed, 99 skipped`
- Extraction artifact tests: `3 passed`

## Resume Commands
- Card text coverage:
  - `cd server && nix shell nixpkgs#uv -c uv run --extra dev pytest tests/test_monopoly_card_text_coverage.py -q`
- Targeted hardware/audio:
  - `cd server && nix shell nixpkgs#uv -c uv run --extra dev pytest tests/test_monopoly_hardware_emulation.py tests/test_monopoly_wave_special_audio_star_wars.py tests/test_monopoly_wave_special_audio_junior.py tests/test_monopoly_wave_special_audio_mario_celebration.py tests/test_monopoly_wave_special_audio_jurassic_park.py tests/test_monopoly_wave_special_audio_lion_king.py -q`
- Full Monopoly:
  - `cd server && nix shell nixpkgs#uv -c uv run --extra dev pytest -k monopoly -q`

## Recommended Next Work
- Hardware/audio mapping is complete (2026-03-01): all 55 boards reviewed, 5 implemented, no further candidates.
- Keep parity matrix and plan docs synchronized with any future board-rule revisions.
- OCR quality re-extraction at 600 DPI completed; disney_the_edition remains unusable grade.

## Important Constraints
- Pac-Man game-unit behavior remains intentionally out of scope.
- Use manual evidence before enabling board hardware/audio capability flags.
- Keep old behavior safe: non-hardware boards should not emit hardware events.
