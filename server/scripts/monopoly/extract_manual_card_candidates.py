"""Mine manual/OCR text artifacts for likely card wording candidate lines."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

ACTION_KEYWORDS = re.compile(
    r"\b("
    r"collect|pay|advance|proceed|move|go to jail|"
    r"get out of jail|draw|go back|take|return"
    r")\b",
    flags=re.IGNORECASE,
)
CARD_FLOW_KEYWORDS = re.compile(
    r"\b("
    r"take the top|follow the instructions|return the card|"
    r"return .* deck|draw a .* card|get out of jail free"
    r")\b",
    flags=re.IGNORECASE,
)
NOISE_LINE_MARKERS = (
    "HASBRO",
    "CONSUMER",
    "HTTPS://",
    "HTTP://",
    "WWW.",
    "BATTERY",
    "FCC",
    "COPYRIGHT",
    "MISCELLANEOUS",
    "OBJECT",
    "PREPARATION",
    "CONTENTS",
    "PAYING RENT",
)


def _stable_dump(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_source_text_path(path_value: str, *, manifest_path: Path) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
        return candidate
    repo_candidate = REPO_ROOT / candidate
    if repo_candidate.exists():
        return repo_candidate
    manifest_relative = manifest_path.parent / candidate
    return manifest_relative


def _normalize_line(raw_line: str) -> str:
    return " ".join(raw_line.split())


def _line_has_noise_marker(line: str) -> bool:
    upper = line.upper()
    return any(marker in upper for marker in NOISE_LINE_MARKERS)


def _alpha_ratio(line: str) -> float:
    if not line:
        return 0.0
    alpha_count = sum(1 for ch in line if ch.isalpha())
    return alpha_count / max(1, len(line))


def _extract_candidate_lines(
    text: str,
    *,
    max_lines: int,
    min_len: int,
    max_len: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        normalized_line = _normalize_line(raw_line)
        if not normalized_line:
            continue
        if normalized_line.startswith("==="):
            continue
        segments = [seg.strip() for seg in re.split(r"(?<=[.!?])\s+", normalized_line) if seg.strip()]
        for segment in segments:
            if len(segment) < min_len or len(segment) > max_len:
                continue
            if "|" in segment:
                continue
            if _line_has_noise_marker(segment):
                continue
            if _alpha_ratio(segment) < 0.55:
                continue

            lowered = segment.casefold()
            word_count = len(segment.split())
            if word_count < 4 or word_count > 40:
                continue

            has_action = ACTION_KEYWORDS.search(segment) is not None
            has_card_flow = CARD_FLOW_KEYWORDS.search(segment) is not None
            has_card_word = "card" in lowered or "cards" in lowered
            if not has_action and not (has_card_word and has_card_flow):
                continue

            dedupe_key = segment.casefold()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            tags: list[str] = []
            if has_card_word:
                tags.append("mentions_card")
            if "collect" in lowered:
                tags.append("collect")
            if "pay" in lowered:
                tags.append("pay")
            if "go to jail" in lowered or "jail" in lowered:
                tags.append("jail")
            if "move" in lowered or "advance" in lowered or "proceed" in lowered:
                tags.append("movement")

            candidates.append(
                {
                    "line": segment,
                    "tags": tags,
                }
            )
            if len(candidates) >= max_lines:
                return candidates
    return candidates


def run_candidate_extraction(
    *,
    manifest_path: Path,
    output_dir: Path,
    board_ids: set[str],
    max_lines: int,
    min_len: int,
    max_len: int,
) -> None:
    manifest_rows = _load_json(manifest_path)
    if not isinstance(manifest_rows, list):
        raise SystemExit("Manifest must be a JSON list.")

    output_dir.mkdir(parents=True, exist_ok=True)

    selected_rows: list[dict[str, Any]] = []
    for row in manifest_rows:
        if not isinstance(row, dict):
            continue
        board_id = str(row.get("board_id", "")).strip()
        if not board_id:
            continue
        if row.get("status") != "ok":
            continue
        if board_ids and board_id not in board_ids:
            continue
        selected_rows.append(row)

    if not selected_rows:
        raise SystemExit("No matching manifest rows selected.")

    generated_at = datetime.now(timezone.utc).isoformat()
    for row in sorted(selected_rows, key=lambda item: str(item.get("board_id", ""))):
        board_id = str(row["board_id"])
        source_path_value = str(row.get("preferred_text_path") or row.get("text_path") or "").strip()
        if not source_path_value:
            print(f"[skip] {board_id}: missing preferred/text path in manifest row")
            continue

        source_path = _resolve_source_text_path(source_path_value, manifest_path=manifest_path)
        if not source_path.exists():
            print(f"[skip] {board_id}: text source path not found: {source_path}")
            continue

        source_text = source_path.read_text(encoding="utf-8")
        candidates = _extract_candidate_lines(
            source_text,
            max_lines=max_lines,
            min_len=min_len,
            max_len=max_len,
        )
        payload = {
            "board_id": board_id,
            "source_text_path": str(source_path),
            "preferred_text_source": row.get("preferred_text_source", row.get("extraction_mode", "pypdf")),
            "generated_at_utc": generated_at,
            "candidate_lines": candidates,
        }
        _stable_dump(output_dir / f"{board_id}.json", payload)
        print(f"[ok] {board_id}: candidates={len(candidates)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract likely manual card wording lines from extracted manual text artifacts.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("server/games/monopoly/manual_rules/extracted/manifest.json"),
        help="Path to extracted manual manifest JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("server/games/monopoly/manual_rules/extracted/card_candidates"),
        help="Output directory for per-board card candidate JSON files.",
    )
    parser.add_argument(
        "--board-id",
        action="append",
        default=[],
        help="Board id to process (repeatable). If omitted, process all status=ok boards.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=120,
        help="Maximum number of candidate lines to keep per board.",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=20,
        help="Minimum normalized line length to consider.",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=220,
        help="Maximum normalized line length to consider.",
    )
    args = parser.parse_args()

    board_ids = {value.strip() for value in args.board_id if value.strip()}
    run_candidate_extraction(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        board_ids=board_ids,
        max_lines=max(1, args.max_lines),
        min_len=max(1, args.min_len),
        max_len=max(args.min_len, args.max_len),
    )


if __name__ == "__main__":
    main()
