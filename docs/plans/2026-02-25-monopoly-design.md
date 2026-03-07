# Monopoly Global Catalog-First Design

Date: 2026-02-25  
Status: Approved for planning  
Branch: `monopoly`

## 1. Goal

Add Monopoly to PlayPalace with a single reusable game engine and per-edition presets, but deliver in a catalog-first milestone:

1. Build a verified global catalog of official Monopoly editions.
2. Attach official manuals only.
3. Use that catalog as the source of truth for later gameplay presets.

## 2. Confirmed Scope Decisions

From design discussion, the agreed scope is:

1. Include official editions (not only mechanically distinct variants), including themed/licensed reskins.
2. Use strict official manuals only.
3. Target global releases.
4. Deliver catalog completeness before gameplay implementation.
5. Later gameplay will use one Monopoly engine with preset profiles.

## 3. Approaches Considered

## Approach A (Chosen): Sitemap-Driven Official Catalog

Use Hasbro Instructions as the primary official source:

1. Crawl root sitemap index.
2. Crawl locale sitemaps.
3. Discover Monopoly instruction URLs.
4. Extract edition/manual metadata from instruction pages.
5. Normalize and deduplicate into canonical artifacts.

Why chosen:

1. Deterministic and automatable.
2. Matches strict "official manuals only".
3. Supports global coverage via locale sitemaps.

## Approach B: Multi-Publisher Aggregator

Aggregate across Hasbro and other publishers/licensees.

Tradeoff:

1. Potentially broader.
2. Lower reliability and higher source inconsistency.

## Approach C: Manual Curation

Hand-maintained catalog from official sites.

Tradeoff:

1. Fast initial setup.
2. Weak completeness guarantees and high maintenance cost.

## 4. Source Validation Findings (2026-02-25)

Observed from live source checks:

1. Root sitemap index exists: `https://instructions.hasbro.com/sitemap.xml`.
2. Root index references 39 locale sitemap feeds.
3. Aggregate scale sample from locale sitemaps:
   - ~31,067 instruction URLs total.
   - ~1,352 Monopoly instruction URLs.
   - ~514 unique Monopoly slugs before SKU-level canonicalization.
4. Locale `all-instructions` routes often redirect to `en-us`; locale sitemaps still contain locale-specific instruction URLs.
5. Instruction pages expose structured payload data (via `__NEXT_DATA__`) including edition metadata and official PDF URLs.
6. Some slug pages return multiple records/manual files for the same SKU and must be preserved as variants.

These findings drive a sitemap-first discovery strategy, not `all-instructions` pagination scraping.

## 5. Architecture

Separate catalog ingestion from gameplay runtime.

1. Catalog pipeline runs offline/on-demand and writes versioned data artifacts to the repo.
2. Future Monopoly engine reads curated preset data derived from canonical catalog artifacts.
3. Game runtime does no web scraping.

## 6. Planned Components

1. `scripts/monopoly/fetch_sitemaps.py`
   - Fetch root sitemap + locale sitemaps.
   - Save raw XML snapshots.

2. `scripts/monopoly/discover_monopoly_urls.py`
   - Extract Monopoly-related instruction URLs from locale sitemap URLs.
   - Emit URL inventory and locale coverage report.

3. `scripts/monopoly/extract_instruction_records.py`
   - Fetch each instruction URL.
   - Parse page payload and extract SKU/name/brand/slug/manual metadata.
   - Preserve multi-record responses.

4. `scripts/monopoly/normalize_catalog.py`
   - Canonicalize and dedupe records by SKU + slug/name heuristics.
   - Build stable edition identifiers.

5. `scripts/monopoly/validate_manuals.py`
   - Validate official PDF URLs (status, filename, size).
   - Compute checksum for version tracking.
   - Use installed PDF skill workflows if deeper PDF checks are needed.

## 7. Data Artifacts

## Raw Snapshots

`server/games/monopoly/catalog/raw/<timestamp>/...`

Contains:

1. Root and locale sitemap XML.
2. Extracted URL lists.
3. Instruction extraction rows.
4. Error/audit logs.

## Canonical Artifacts

1. `server/games/monopoly/catalog/monopoly_editions.json`
2. `server/games/monopoly/catalog/monopoly_manual_variants.json`
3. `server/games/monopoly/catalog/catalog_stats.json`

## Canonical Record Shape (High-Level)

1. `edition_id`
2. `sku`
3. `canonical_slug`
4. `display_name`
5. `brand`
6. `categories` (e.g., junior, cheaters, electronic, themed)
7. `locales[]` with `locale`, `instruction_url`, `manuals[]`
8. `manuals[]` fields:
   - `pdf_url`
   - `filename`
   - `size_bytes`
   - `sha256`
   - `http_status`
   - `verified_at`
9. `first_seen_at`, `last_seen_at`, `source_lastmod`

## 8. Data Flow

1. Crawl sitemap index and locale sitemaps.
2. Discover Monopoly instruction URLs per locale.
3. Extract instruction page payload records.
4. Normalize and dedupe to canonical editions.
5. Validate manuals and fingerprint files.
6. Emit stable, sorted artifacts plus stats.

Incremental runs:

1. Reuse cached URL/manual validation metadata.
2. Revalidate changed/new records first.
3. Support full revalidation mode when needed.

## 9. Error Handling and Quality Gates

1. Retry transient network failures with backoff.
2. Record hard failures by URL and reason; do not silently discard.
3. Keep records even when manuals are unavailable/unverified.
4. Use schema validation and fail fast on structural drift.
5. Use atomic writes for canonical files.
6. Support dry-run mode for safe auditing.

## 10. Testing Strategy

1. Unit tests:
   - Sitemap URL extraction.
   - Payload parsing with variant HTML/script formatting.
   - Dedup/canonicalization logic.
2. Fixture-based parser tests for stability.
3. Integration test over offline fixture bundle to assert deterministic output.
4. Manual validation tests with mocked HTTP status/checksum paths.
5. Optional live smoke command for small real-url samples.

## 11. Milestones

## M0: Catalog Pipeline (Current Target)

1. End-to-end ingestion scripts.
2. Canonical artifacts generated.
3. Stats and audit outputs.
4. Tests for parser/normalizer.

## M1: Catalog Review and Curation

1. Manual verification spot checks.
2. Category tagging refinement.
3. Preset candidate extraction for gameplay phase.

## M2: Gameplay Planning Input

1. Produce curated preset source from catalog.
2. Hand off to Monopoly engine implementation plan.

## 12. Acceptance Criteria for Catalog-Complete v1

Catalog v1 is complete when:

1. Every Monopoly instruction URL discoverable from current locale sitemaps is represented in raw/canonical outputs.
2. Canonical dedupe is deterministic and test-covered.
3. Official manual URLs are attached where present and validation status is recorded.
4. Missing/unverified manuals are explicitly flagged, not omitted.
5. Pipeline reruns produce stable diffs on unchanged source data.

## 13. Out of Scope for This Milestone

1. Monopoly gameplay logic.
2. Bot AI for Monopoly.
3. Client gameplay UI/menu flow changes.
4. Full localization strings for gameplay actions.

Those are explicitly deferred until after catalog completion and implementation planning.

## 14. Risks and Mitigations

1. Source structure drift:
   - Mitigation: fixture tests + parser schema guards + raw snapshot retention.
2. Locale inconsistencies:
   - Mitigation: sitemap-driven discovery per locale, not locale listing endpoints.
3. Duplicate/ambiguous entries:
   - Mitigation: SKU-first canonicalization and explicit review flags.
4. Manual URL churn:
   - Mitigation: checksum tracking and historical seen-state in raw artifacts.

## 15. Handoff

Next step after this approved design document is to invoke the `writing-plans` skill and produce the detailed implementation task plan for M0.
