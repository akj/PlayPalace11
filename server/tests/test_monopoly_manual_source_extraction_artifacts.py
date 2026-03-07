from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXTRACTED_DIR = REPO_ROOT / "server/games/monopoly/manual_rules/extracted"
MANIFEST_PATH = EXTRACTED_DIR / "manifest.json"
ANCHOR_INDEX_PATH = REPO_ROOT / "server/games/monopoly/catalog/special_board_anchor_index.json"
EXPECTED_FALLBACK_MODES = {
    "marvel_flip": "strings_fallback",
}
EXPECTED_OCR_SIDECAR_BOARDS = {
    "disney_the_edition",
    "lord_of_the_rings_trilogy",
    "marvel_avengers_legacy",
    "marvel_flip",
    "star_wars_saga",
}
EXPECTED_OCR_PREFERRED_BOARDS = EXPECTED_OCR_SIDECAR_BOARDS


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_covers_all_anchor_board_ids() -> None:
    anchor_rows = _load_json(ANCHOR_INDEX_PATH)
    expected_board_ids = {
        row["board_id"]
        for row in anchor_rows
        if row.get("board_id")
    }
    manifest_rows = _load_json(MANIFEST_PATH)
    manifest_board_ids = {row["board_id"] for row in manifest_rows}
    assert expected_board_ids <= manifest_board_ids


def test_manifest_entries_are_valid_or_known_exceptions() -> None:
    manifest_rows = _load_json(MANIFEST_PATH)
    failed_board_ids = [row["board_id"] for row in manifest_rows if row.get("status") != "ok"]
    assert failed_board_ids == []

    for row in manifest_rows:
        board_id = row["board_id"]
        assert row.get("status") == "ok"

        assert row.get("page_count", 0) > 0
        assert row.get("text_char_count", 0) > 0
        assert row.get("pdf_sha256")
        assert row.get("text_sha256")
        extraction_mode = row.get("extraction_mode", "pypdf")
        expected_mode = EXPECTED_FALLBACK_MODES.get(board_id, "pypdf")
        assert extraction_mode == expected_mode

        text_path = Path(str(row["text_path"]))
        if not text_path.is_absolute():
            text_path = REPO_ROOT / text_path
        assert text_path.exists(), f"missing extracted text for {board_id}"
        text_content = text_path.read_text(encoding="utf-8")
        assert "=== Page 1 ===" in text_content
        assert len(text_content) >= row["text_char_count"]

        preferred_text_path = Path(str(row.get("preferred_text_path", row["text_path"])))
        if not preferred_text_path.is_absolute():
            preferred_text_path = REPO_ROOT / preferred_text_path
        assert preferred_text_path.exists(), f"missing preferred extracted text for {board_id}"
        preferred_text_content = preferred_text_path.read_text(encoding="utf-8")
        assert len(preferred_text_content) >= row.get("preferred_text_char_count", row["text_char_count"])
        assert row.get("preferred_text_sha256")
        assert row.get("preferred_text_source")

        ocr_text_path = row.get("ocr_text_path")
        if board_id in EXPECTED_OCR_SIDECAR_BOARDS:
            assert isinstance(ocr_text_path, str) and ocr_text_path
        if board_id in EXPECTED_OCR_PREFERRED_BOARDS:
            assert row.get("preferred_text_source") == "ocr_sidecar"
        if ocr_text_path:
            resolved_ocr_path = Path(str(ocr_text_path))
            if not resolved_ocr_path.is_absolute():
                resolved_ocr_path = REPO_ROOT / resolved_ocr_path
            assert resolved_ocr_path.exists(), f"missing OCR sidecar text for {board_id}"
            ocr_text_content = resolved_ocr_path.read_text(encoding="utf-8")
            assert len(ocr_text_content) >= row.get("ocr_text_char_count", 0)
            assert row.get("ocr_text_sha256")

        meta_path = EXTRACTED_DIR / f"{board_id}.json"
        assert meta_path.exists(), f"missing metadata for {board_id}"


VALID_OCR_QUALITY_GRADES = {"unusable", "low", "medium", "high"}


def test_ocr_sidecar_boards_have_quality_grade() -> None:
    manifest_rows = _load_json(MANIFEST_PATH)
    for row in manifest_rows:
        board_id = row["board_id"]
        if board_id not in EXPECTED_OCR_SIDECAR_BOARDS:
            continue
        grade = row.get("ocr_quality_grade")
        assert grade is not None, (
            f"{board_id}: OCR sidecar board missing 'ocr_quality_grade'"
        )
        assert grade in VALID_OCR_QUALITY_GRADES, (
            f"{board_id}: invalid ocr_quality_grade '{grade}'"
        )
        note = row.get("ocr_quality_note")
        assert note and isinstance(note, str), (
            f"{board_id}: OCR sidecar board missing 'ocr_quality_note'"
        )
