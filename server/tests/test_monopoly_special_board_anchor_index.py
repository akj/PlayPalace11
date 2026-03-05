"""Tests for special-board anchor index artifact."""

from __future__ import annotations

import json
from pathlib import Path

from server.games.monopoly.board_parity import get_parity_board_ids


def _index_path() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "games"
        / "monopoly"
        / "catalog"
        / "special_board_anchor_index.json"
    )


def test_anchor_index_has_unique_board_ids():
    data = json.loads(_index_path().read_text(encoding="utf-8"))
    ids = [row["board_id"] for row in data]

    assert len(ids) == len(set(ids))


def test_anchor_index_excludes_pacman_game_unit():
    data = json.loads(_index_path().read_text(encoding="utf-8"))

    assert all(row["board_id"] != "pacman" for row in data)


def test_anchor_index_covers_parity_manifest_boards():
    data = json.loads(_index_path().read_text(encoding="utf-8"))
    indexed_ids = {row["board_id"] for row in data}
    parity_ids = set(get_parity_board_ids())

    assert parity_ids.issubset(indexed_ids)


def test_anchor_index_marks_all_special_boards_manual_core():
    data = json.loads(_index_path().read_text(encoding="utf-8"))

    assert all(row.get("fidelity_status") == "manual_core" for row in data)
