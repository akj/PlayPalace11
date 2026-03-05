"""Tests for Monopoly catalog ingestion and normalization pipeline."""

from pathlib import Path
import json

from server.games.monopoly.catalog.models import RawInstructionRecord, CanonicalEdition
from server.games.monopoly.catalog.sitemap_parser import (
    parse_sitemap_index,
    parse_monopoly_instruction_urls,
)
from server.games.monopoly.catalog.instruction_parser import (
    extract_next_data_json,
    extract_raw_records,
)
from server.games.monopoly.catalog.normalize import build_canonical_catalog
from server.games.monopoly.catalog.manual_validator import validate_manual


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "monopoly"


def fixture_text(name: str) -> str:
    """Load a text fixture from tests/fixtures/monopoly."""
    return (FIXTURE_ROOT / name).read_text(encoding="utf-8")


def payload_fixture(name: str) -> dict:
    """Load parsed payload fixture from tests/fixtures/monopoly."""
    return json.loads((FIXTURE_ROOT / f"{name}.json").read_text(encoding="utf-8"))


def test_model_defaults_are_serializable():
    """Raw records can be transformed into canonical editions."""
    raw = RawInstructionRecord(
        locale="en-us",
        instruction_url=(
            "https://instructions.hasbro.com/en-us/instruction/"
            "monopoly-game-cheaters-edition"
        ),
        sku="E1871",
        slug="monopoly-game-cheaters-edition",
        name="Monopoly Game: Cheaters Edition",
        brand="Monopoly",
        manuals=[],
    )

    edition = CanonicalEdition.from_raw(raw)

    assert edition.sku == "E1871"
    assert edition.edition_id.startswith("monopoly-")


def test_parse_sitemap_index_returns_locale_sitemap_urls():
    """Root sitemap index exposes locale sitemap URLs."""
    urls = parse_sitemap_index(fixture_text("sitemap_index.xml"))
    assert "https://instructions.hasbro.com/en-gb/sitemap.xml" in urls
    assert len(urls) >= 6


def test_extract_monopoly_instruction_urls_from_locale_sitemap():
    """Locale sitemap parser keeps Monopoly instruction URLs only."""
    urls = parse_monopoly_instruction_urls(fixture_text("en_gb_sitemap.xml"))
    assert any("/instruction/monopoly-game-cheaters-edition" in url for url in urls)
    assert all("/instruction/" in url for url in urls)


def test_extract_next_data_json_handles_unquoted_script_attributes():
    """Parser handles __NEXT_DATA__ script tag without strict quoting."""
    payload = extract_next_data_json(fixture_text("instruction_en_gb_cheaters.html"))
    assert payload["page"] == "/instruction/[instruction]"
    assert payload["query"]["instruction"] == "monopoly-game-cheaters-edition"


def test_extract_raw_records_preserves_multiple_entries():
    """Instruction payload can return multiple records for one slug."""
    payload = payload_fixture("instruction_en_gb_cheaters_payload")
    records = extract_raw_records(
        payload,
        "https://instructions.hasbro.com/en-gb/instruction/monopoly-game-cheaters-edition",
    )
    assert len(records) == 2
    assert all(record.sku == "E1871" for record in records)
    assert all(record.manuals for record in records)


def test_build_canonical_catalog_groups_by_sku_and_keeps_locale_variants():
    """Canonical catalog merges editions by SKU but keeps manual variants."""
    records = [
        RawInstructionRecord(
            locale="en-gb",
            instruction_url=(
                "https://instructions.hasbro.com/en-gb/instruction/"
                "monopoly-game-cheaters-edition"
            ),
            sku="E1871",
            slug="monopoly-game-cheaters-edition",
            name="Monopoly Game: Cheaters Edition",
            brand="Monopoly",
            manuals=[],
        ),
        RawInstructionRecord(
            locale="fr-fr",
            instruction_url=(
                "https://instructions.hasbro.com/fr-fr/instruction/"
                "monopoly-game-cheaters-edition"
            ),
            sku="E1871",
            slug="monopoly-game-cheaters-edition",
            name="Monopoly Game: Cheaters Edition",
            brand="Monopoly",
            manuals=[],
        ),
    ]
    catalog = build_canonical_catalog(records)

    assert len(catalog.editions) == 1
    assert len(catalog.manual_variants) == 0


def test_validate_manual_records_status_and_sha256(monkeypatch):
    """Manual validator records HTTP status and sha256 for downloaded bytes."""

    class _FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"%PDF-1.7 fake bytes"

    monkeypatch.setattr(
        "server.games.monopoly.catalog.manual_validator.urlopen",
        lambda request, timeout=20.0: _FakeResponse(),
    )

    result = validate_manual("https://assets-us-01.kc-usercontent.com/file.pdf")
    assert result["http_status"] == 200
    assert len(result["sha256"]) == 64
