# Monopoly Manual-Core Dual-Lane Throughput Design

Date: 2026-02-27  
Branch: `monopoly`

## Goal

Promote remaining Monopoly special boards from `near_full` to `manual_core` with a dual-lane workflow that preserves manual authenticity while maintaining high throughput.

## Architecture

Use a dual-lane promotion pipeline over the existing 55-board special-board catalog:

1. Lane A (`strict/high-text`): boards with strong extracted text and robust card-candidate coverage move directly to strict card/effect verification and promotion.
2. Lane B (`hybrid/low-text`): boards with low-text/image-heavy manuals require OCR-backed evidence and explicit `not_observed_in_available_manual_sources` notes for unresolved literals.

The promotion unit remains per-board, while execution batching is per-lane to maximize throughput and keep verification deterministic.

## Components and Data Flow

For each board:

1. Refresh extraction artifacts (`manifest`, per-board extracted text metadata, OCR sidecars, and card candidates).
2. Classify board lane using extraction quality signals:
   - preferred text source (`pypdf`, `ocr_sidecar`, `strings_fallback`);
   - candidate density and text character count;
   - known image-heavy/manual-quality flags.
3. Apply board-rule updates:
   - board-specific labels, cards, and effects from manual evidence;
   - Lane B unresolved literals receive explicit evidence-based `text_status` notes.
4. Update citations and `manual_extraction` traceability metadata.
5. Run board/family targeted tests plus global Monopoly regression.
6. Promote board to `manual_core` when gates pass.

No schema expansion is required; existing `mechanics.manual_source`, `mechanics.manual_extraction`, `cards`, and `citations` fields remain the source of truth.

## Error Handling and Promotion Guards

1. Manifest integrity: transient manual download failures must preserve valid cached extraction metadata.
2. Citation gate: boards cannot promote with missing required manual evidence paths.
3. Lane B discipline: unresolved literal effects must be explicit and evidence-backed, never silent placeholders.
4. Runtime compatibility: preserve `legacy_id` bridges while adopting native manual deck ids.

## Testing and Throughput Controls

1. Targeted tests for touched boards/families (payload fidelity, deck mapping, card draw text, registry checks).
2. Global safety net: `pytest -k monopoly -q`.
3. Extraction integrity tests for manifest/seed metadata.
4. Batch promotion size: 5-8 boards per batch with frequent commits and synced plan-status updates.

## Done Definition for This Design

1. Promotions follow dual-lane rules without violating manual evidence requirements.
2. All touched boards retain green targeted tests and full Monopoly regression.
3. Status and planning docs remain synchronized after each batch.
