# Monopoly Catalog Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a deterministic, test-covered pipeline that discovers global official Monopoly instruction pages from Hasbro sitemaps and emits canonical edition/manual catalog artifacts for PlayPalace.

**Architecture:** Implement a pure-Python offline pipeline in `server/scripts/monopoly` backed by parser/normalizer modules in `server/games/monopoly/catalog`. The pipeline uses sitemap XML for discovery, parses `__NEXT_DATA__` JSON from instruction HTML pages, normalizes records by SKU/slug/name, and writes stable JSON artifacts. Runtime game code will consume artifacts later; no gameplay logic is included in this milestone.

**Tech Stack:** Python 3.11, stdlib (`xml.etree`, `json`, `re`, `hashlib`, `urllib`, `pathlib`), pytest, uv.

---

### Task 1: Create Catalog Package Skeleton and Model Contracts

**Files:**
- Create: `server/games/monopoly/__init__.py`
- Create: `server/games/monopoly/catalog/__init__.py`
- Create: `server/games/monopoly/catalog/models.py`
- Test: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.models import RawInstructionRecord, CanonicalEdition

def test_model_defaults_are_serializable():
    raw = RawInstructionRecord(
        locale="en-us",
        instruction_url="https://instructions.hasbro.com/en-us/instruction/monopoly-game-cheaters-edition",
        sku="E1871",
        slug="monopoly-game-cheaters-edition",
        name="Monopoly Game: Cheaters Edition",
        brand="Monopoly",
        manuals=[],
    )
    edition = CanonicalEdition.from_raw(raw)
    assert edition.sku == "E1871"
    assert edition.edition_id.startswith("monopoly-")
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_model_defaults_are_serializable -v`  
Expected: FAIL with `ModuleNotFoundError` or missing class definitions.

**Step 3: Write minimal implementation**

```python
# server/games/monopoly/catalog/models.py
from dataclasses import dataclass, field

@dataclass
class RawManual:
    pdf_url: str
    filename: str
    size_bytes: int | None = None

@dataclass
class RawInstructionRecord:
    locale: str
    instruction_url: str
    sku: str
    slug: str
    name: str
    brand: str
    manuals: list[RawManual] = field(default_factory=list)

@dataclass
class CanonicalEdition:
    edition_id: str
    sku: str
    canonical_slug: str
    display_name: str
    brand: str

    @classmethod
    def from_raw(cls, raw: RawInstructionRecord) -> "CanonicalEdition":
        edition_id = f"monopoly-{raw.sku.lower()}"
        return cls(edition_id, raw.sku, raw.slug, raw.name, raw.brand)
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_model_defaults_are_serializable -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/__init__.py server/games/monopoly/catalog/__init__.py server/games/monopoly/catalog/models.py server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add Monopoly catalog model skeleton"
```

### Task 2: Parse Root Sitemap Index

**Files:**
- Create: `server/games/monopoly/catalog/sitemap_parser.py`
- Create: `server/tests/fixtures/monopoly/sitemap_index.xml`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.sitemap_parser import parse_sitemap_index

def test_parse_sitemap_index_returns_locale_sitemap_urls(fixture_text):
    urls = parse_sitemap_index(fixture_text("monopoly/sitemap_index.xml"))
    assert "https://instructions.hasbro.com/en-gb/sitemap.xml" in urls
    assert len(urls) >= 30
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_parse_sitemap_index_returns_locale_sitemap_urls -v`  
Expected: FAIL with missing function/module.

**Step 3: Write minimal implementation**

```python
import xml.etree.ElementTree as ET

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def parse_sitemap_index(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for loc in root.findall(".//sm:sitemap/sm:loc", NS):
        if loc.text:
            urls.append(loc.text.strip())
    return urls
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_parse_sitemap_index_returns_locale_sitemap_urls -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/sitemap_parser.py server/tests/fixtures/monopoly/sitemap_index.xml server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add root sitemap index parser"
```

### Task 3: Extract Monopoly Instruction URLs from Locale Sitemap

**Files:**
- Create: `server/tests/fixtures/monopoly/en_gb_sitemap.xml`
- Modify: `server/games/monopoly/catalog/sitemap_parser.py`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.sitemap_parser import parse_monopoly_instruction_urls

def test_extract_monopoly_instruction_urls_from_locale_sitemap(fixture_text):
    urls = parse_monopoly_instruction_urls(fixture_text("monopoly/en_gb_sitemap.xml"))
    assert any("/instruction/monopoly-game-cheaters-edition" in u for u in urls)
    assert all("/instruction/" in u for u in urls)
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_monopoly_instruction_urls_from_locale_sitemap -v`  
Expected: FAIL with missing function.

**Step 3: Write minimal implementation**

```python
def parse_monopoly_instruction_urls(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for loc in root.findall(".//sm:url/sm:loc", NS):
        if not loc.text:
            continue
        url = loc.text.strip()
        if "/instruction/" in url and "monopoly" in url.lower():
            urls.append(url)
    return sorted(set(urls))
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_monopoly_instruction_urls_from_locale_sitemap -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/sitemap_parser.py server/tests/fixtures/monopoly/en_gb_sitemap.xml server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add monopoly URL extraction from locale sitemaps"
```

### Task 4: Parse `__NEXT_DATA__` Safely from Instruction HTML

**Files:**
- Create: `server/games/monopoly/catalog/instruction_parser.py`
- Create: `server/tests/fixtures/monopoly/instruction_en_gb_cheaters.html`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.instruction_parser import extract_next_data_json

def test_extract_next_data_json_handles_unquoted_script_attributes(fixture_text):
    html = fixture_text("monopoly/instruction_en_gb_cheaters.html")
    payload = extract_next_data_json(html)
    assert payload["page"] == "/instruction/[instruction]"
    assert payload["query"]["instruction"] == "monopoly-game-cheaters-edition"
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_next_data_json_handles_unquoted_script_attributes -v`  
Expected: FAIL with missing parser.

**Step 3: Write minimal implementation**

```python
import json
import re

NEXT_DATA_RE = re.compile(
    r'<script id=?"?__NEXT_DATA__"? type=?"application/json"?>(.*?)</script>',
    re.DOTALL,
)

def extract_next_data_json(html: str) -> dict:
    match = NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("No __NEXT_DATA__ script found")
    return json.loads(match.group(1))
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_next_data_json_handles_unquoted_script_attributes -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/instruction_parser.py server/tests/fixtures/monopoly/instruction_en_gb_cheaters.html server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add instruction page payload parser"
```

### Task 5: Extract Raw Instruction Records from Page Payload

**Files:**
- Modify: `server/games/monopoly/catalog/instruction_parser.py`
- Modify: `server/games/monopoly/catalog/models.py`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.instruction_parser import extract_raw_records

def test_extract_raw_records_preserves_multiple_entries(payload_fixture):
    payload = payload_fixture("instruction_en_gb_cheaters")
    records = extract_raw_records(payload, "https://instructions.hasbro.com/en-gb/instruction/monopoly-game-cheaters-edition")
    assert len(records) == 2
    assert all(r.sku == "E1871" for r in records)
    assert all(r.manuals for r in records)
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_raw_records_preserves_multiple_entries -v`  
Expected: FAIL with missing function.

**Step 3: Write minimal implementation**

```python
def extract_raw_records(payload: dict, instruction_url: str) -> list[RawInstructionRecord]:
    page_props = payload["props"]["pageProps"]
    locale = page_props.get("locale", "")
    rows = page_props.get("instructions", {}).get("filtered_instructions", [])
    records: list[RawInstructionRecord] = []
    for row in rows:
        if not row:
            continue
        item = row[0]
        manuals = [
            RawManual(
                pdf_url=pdf.get("url", ""),
                filename=pdf.get("url", "").rsplit("/", 1)[-1],
                size_bytes=pdf.get("size"),
            )
            for pdf in item.get("pdf", [])
            if pdf.get("url")
        ]
        records.append(
            RawInstructionRecord(
                locale=locale,
                instruction_url=instruction_url,
                sku=item.get("sku", ""),
                slug=item.get("slug", ""),
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                manuals=manuals,
            )
        )
    return records
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_extract_raw_records_preserves_multiple_entries -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/instruction_parser.py server/games/monopoly/catalog/models.py server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Extract raw monopoly records from instruction payloads"
```

### Task 6: Canonicalize and Dedupe Editions

**Files:**
- Create: `server/games/monopoly/catalog/normalize.py`
- Modify: `server/games/monopoly/catalog/models.py`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.normalize import build_canonical_catalog

def test_build_canonical_catalog_groups_by_sku_and_keeps_locale_variants(raw_record_factory):
    records = [
        raw_record_factory(locale="en-gb", sku="E1871", slug="monopoly-game-cheaters-edition"),
        raw_record_factory(locale="fr-fr", sku="E1871", slug="monopoly-game-cheaters-edition"),
    ]
    catalog = build_canonical_catalog(records)
    assert len(catalog.editions) == 1
    assert len(catalog.manual_variants) == 2
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_build_canonical_catalog_groups_by_sku_and_keeps_locale_variants -v`  
Expected: FAIL with missing module/function.

**Step 3: Write minimal implementation**

```python
def build_canonical_catalog(records: list[RawInstructionRecord]) -> CanonicalCatalog:
    by_sku: dict[str, list[RawInstructionRecord]] = {}
    for record in records:
        by_sku.setdefault(record.sku, []).append(record)
    editions: list[CanonicalEdition] = []
    manual_variants: list[dict] = []
    for sku, sku_records in sorted(by_sku.items()):
        base = sku_records[0]
        edition = CanonicalEdition.from_raw(base)
        editions.append(edition)
        for raw in sku_records:
            for manual in raw.manuals:
                manual_variants.append(
                    {
                        "edition_id": edition.edition_id,
                        "locale": raw.locale,
                        "instruction_url": raw.instruction_url,
                        "pdf_url": manual.pdf_url,
                        "filename": manual.filename,
                        "size_bytes": manual.size_bytes,
                    }
                )
    return CanonicalCatalog(editions=editions, manual_variants=manual_variants)
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_build_canonical_catalog_groups_by_sku_and_keeps_locale_variants -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/normalize.py server/games/monopoly/catalog/models.py server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add canonical monopoly catalog normalizer"
```

### Task 7: Implement Manual URL Validation and Checksum

**Files:**
- Create: `server/games/monopoly/catalog/manual_validator.py`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`

**Step 1: Write the failing test**

```python
from server.games.monopoly.catalog.manual_validator import validate_manual

def test_validate_manual_records_status_and_sha256(http_mock_pdf):
    result = validate_manual("https://assets-us-01.kc-usercontent.com/file.pdf")
    assert result["http_status"] == 200
    assert len(result["sha256"]) == 64
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_validate_manual_records_status_and_sha256 -v`  
Expected: FAIL with missing function/module.

**Step 3: Write minimal implementation**

```python
import hashlib
from urllib.request import urlopen

def validate_manual(pdf_url: str, timeout: float = 20.0) -> dict:
    with urlopen(pdf_url, timeout=timeout) as response:
        payload = response.read()
        return {
            "pdf_url": pdf_url,
            "http_status": response.status,
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py::test_validate_manual_records_status_and_sha256 -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/games/monopoly/catalog/manual_validator.py server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add manual URL validation helper"
```

### Task 8: Build Offline Pipeline Orchestrator

**Files:**
- Create: `server/scripts/monopoly/build_catalog.py`
- Modify: `server/tests/test_monopoly_catalog_pipeline.py`
- Create: `server/tests/test_monopoly_catalog_integration.py`

**Step 1: Write the failing integration test**

```python
from pathlib import Path
from server.scripts.monopoly.build_catalog import run_pipeline

def test_run_pipeline_offline_fixtures_writes_canonical_outputs(tmp_path: Path, fixture_dir: Path):
    output_dir = tmp_path / "catalog"
    run_pipeline(fixture_dir=fixture_dir, output_dir=output_dir, offline=True)
    assert (output_dir / "monopoly_editions.json").exists()
    assert (output_dir / "monopoly_manual_variants.json").exists()
    assert (output_dir / "catalog_stats.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_run_pipeline_offline_fixtures_writes_canonical_outputs -v`  
Expected: FAIL with missing script or callable.

**Step 3: Write minimal implementation**

```python
def run_pipeline(*, fixture_dir: Path, output_dir: Path, offline: bool = False) -> None:
    # load fixture files -> parse -> normalize -> write json artifacts
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "monopoly_editions.json").write_text(json.dumps([...], indent=2), encoding="utf-8")
    (output_dir / "monopoly_manual_variants.json").write_text(json.dumps([...], indent=2), encoding="utf-8")
    (output_dir / "catalog_stats.json").write_text(json.dumps({...}, indent=2), encoding="utf-8")
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_run_pipeline_offline_fixtures_writes_canonical_outputs -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/scripts/monopoly/build_catalog.py server/tests/test_monopoly_catalog_integration.py server/tests/test_monopoly_catalog_pipeline.py
git commit -m "Add offline monopoly catalog pipeline entrypoint"
```

### Task 9: Deterministic Output and Stats Contract

**Files:**
- Modify: `server/scripts/monopoly/build_catalog.py`
- Modify: `server/tests/test_monopoly_catalog_integration.py`

**Step 1: Write the failing test**

```python
def test_pipeline_outputs_are_stably_sorted_and_repeatable(tmp_path, fixture_dir):
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    run_pipeline(fixture_dir=fixture_dir, output_dir=out1, offline=True)
    run_pipeline(fixture_dir=fixture_dir, output_dir=out2, offline=True)
    assert (out1 / "monopoly_editions.json").read_text() == (out2 / "monopoly_editions.json").read_text()
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_pipeline_outputs_are_stably_sorted_and_repeatable -v`  
Expected: FAIL due non-deterministic ordering.

**Step 3: Write minimal implementation**

```python
json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)
# sort editions/manual variants by stable keys before writing
```

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_pipeline_outputs_are_stably_sorted_and_repeatable -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/scripts/monopoly/build_catalog.py server/tests/test_monopoly_catalog_integration.py
git commit -m "Stabilize monopoly catalog output ordering"
```

### Task 10: Developer Runbook and Validation Commands

**Files:**
- Create: `server/plans/monopoly_catalog_pipeline.md`
- Modify: `docs/plans/2026-02-25-monopoly-catalog-implementation.md`

**Step 1: Write the failing documentation test/check**

```python
def test_runbook_lists_pipeline_commands():
    text = Path("server/plans/monopoly_catalog_pipeline.md").read_text(encoding="utf-8")
    assert "uv run python scripts/monopoly/build_catalog.py" in text
```

**Step 2: Run test to verify it fails**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_runbook_lists_pipeline_commands -v`  
Expected: FAIL because runbook file does not exist.

**Step 3: Write minimal implementation**

Include:

1. Offline fixture command.
2. Live crawl command.
3. Output artifact locations.
4. Recommended checks (targeted pytest commands).
5. Note to use `@pdf` workflow for optional deep manual PDF checks.

**Step 4: Run test to verify it passes**

Run: `cd server && uv run pytest tests/test_monopoly_catalog_integration.py::test_runbook_lists_pipeline_commands -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add server/plans/monopoly_catalog_pipeline.md docs/plans/2026-02-25-monopoly-catalog-implementation.md server/tests/test_monopoly_catalog_integration.py
git commit -m "Document monopoly catalog pipeline runbook"
```

## Final Verification Pass

Run:

1. `cd server && uv run pytest tests/test_monopoly_catalog_pipeline.py -v`
2. `cd server && uv run pytest tests/test_monopoly_catalog_integration.py -v`
3. `cd server && uv run pytest -k monopoly -v`

Expected:

1. All Monopoly catalog pipeline tests PASS.
2. Deterministic artifact contract tests PASS.
3. No regressions in touched test surfaces.
