"""Tests for manual card candidate extraction script."""

from __future__ import annotations

import json
from pathlib import Path

from server.scripts.monopoly.extract_manual_card_candidates import (
    _extract_candidate_lines,
    run_candidate_extraction,
)


def test_extract_candidate_lines_filters_noise_and_keeps_card_wording() -> None:
    text = """
=== Page 1 ===
OBJECT
Take the top Jedi card and do what it says.
Pay 50 Republic Credits to the Bank.
HASBRO customer support line.
Go to Jail immediately. Do not collect salary.
"""
    rows = _extract_candidate_lines(
        text,
        max_lines=20,
        min_len=10,
        max_len=200,
    )
    lines = [row["line"] for row in rows]

    assert "Take the top Jedi card and do what it says." in lines
    assert "Pay 50 Republic Credits to the Bank." in lines
    assert "Go to Jail immediately." in lines
    assert "Do not collect salary." in lines
    assert all("HASBRO" not in line.upper() for line in lines)
    assert all("OBJECT" != line for line in lines)


def test_run_candidate_extraction_writes_board_payload(tmp_path: Path) -> None:
    source_text_path = tmp_path / "source.txt"
    source_text_path.write_text(
        "=== Page 1 ===\nTake the top Jedi card and do what it says.\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "board_id": "star_wars_saga",
                    "status": "ok",
                    "preferred_text_path": str(source_text_path),
                    "preferred_text_source": "ocr_sidecar",
                }
            ]
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "out"
    run_candidate_extraction(
        manifest_path=manifest_path,
        output_dir=output_dir,
        board_ids={"star_wars_saga"},
        max_lines=10,
        min_len=10,
        max_len=200,
    )

    payload_path = output_dir / "star_wars_saga.json"
    assert payload_path.exists()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["board_id"] == "star_wars_saga"
    assert payload["preferred_text_source"] == "ocr_sidecar"
    assert payload["candidate_lines"]
