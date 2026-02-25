# Monopoly Catalog Pipeline Runbook

This runbook covers the catalog-first Monopoly ingestion flow.

## Commands

## Offline fixture run

Run from repository root:

```bash
cd server
uv run python scripts/monopoly/build_catalog.py --offline --fixture-dir tests/fixtures/monopoly --output-dir ../tmp/monopoly-catalog-offline
```

## Live crawl run

Run from repository root:

```bash
cd server
uv run python scripts/monopoly/build_catalog.py --output-dir games/monopoly/catalog
```

## Live crawl with manual checksum validation

```bash
cd server
uv run python scripts/monopoly/build_catalog.py --output-dir games/monopoly/catalog --validate-manual-urls
```

## Output Artifacts

The pipeline writes:

1. `monopoly_editions.json` (canonical edition list)
2. `monopoly_manual_variants.json` (manual variants per locale/edition)
3. `catalog_stats.json` (run summary counts)

## Test Commands

```bash
cd server
uv run pytest tests/test_monopoly_catalog_pipeline.py -v
uv run pytest tests/test_monopoly_catalog_integration.py -v
```

## Notes

1. Use the installed `@pdf` skill when you need deeper PDF analysis beyond URL/status/checksum verification.
2. Keep artifact output deterministic so diffs stay reviewable.
3. Preserve missing/unverified manuals as explicit records; do not silently drop them.

