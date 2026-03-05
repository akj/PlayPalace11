"""Extract manual text artifacts from board-linked Monopoly PDF manuals."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any
from urllib.request import Request, urlopen


# Allow direct script execution: python server/scripts/monopoly/extract_manual_text.py
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from pypdf import PdfReader
    import pypdf.filters as pypdf_filters
except ModuleNotFoundError as error:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing optional dependency 'pypdf'. Install with: "
        "./.venv/bin/python -m pip install pypdf"
    ) from error


BOARD_ZLIB_RETRY_LIMITS: dict[str, int] = {
    # This manual includes a very large compressed stream that exceeds
    # the default extraction cap.
    "marvel_flip": 252_000_000,
}

QUALITY_STOPWORDS = {
    "a",
    "and",
    "card",
    "cards",
    "collect",
    "community",
    "do",
    "for",
    "go",
    "if",
    "in",
    "is",
    "jail",
    "of",
    "on",
    "pay",
    "player",
    "roll",
    "team",
    "the",
    "to",
    "turn",
    "up",
    "you",
    "your",
}


def _stable_dump(path: Path, data: Any) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    tmp_path.replace(path)


def _fetch_pdf_bytes(url: str, timeout: float) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "PlayPalace-Monopoly-ManualExtract/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def _extract_pages(pdf_bytes: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text.strip())
    return pages


def _extract_text_strings_fallback(pdf_bytes: bytes, *, max_lines: int = 12_000) -> str:
    decoded = pdf_bytes.decode("latin-1", errors="ignore")
    pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .,;:!?()\-/'\"&%+=_]{5,}")
    lines: list[str] = []
    seen: set[str] = set()
    for match in pattern.findall(decoded):
        normalized = " ".join(match.split())
        if len(normalized) < 6:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        lines.append(normalized)
        if len(lines) >= max_lines:
            break
    return "\n".join(lines).strip()


def _attach_preferred_text_metadata(meta: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    """Attach OCR-aware preferred text metadata for one extracted board row."""
    board_id = str(meta.get("board_id", ""))
    text_path_value = str(meta.get("text_path", ""))
    text_sha = str(meta.get("text_sha256", ""))
    text_char_count = int(meta.get("text_char_count", 0) or 0)
    extraction_mode = str(meta.get("extraction_mode", "pypdf"))

    preferred_text_path = text_path_value
    preferred_text_sha = text_sha
    preferred_text_char_count = text_char_count
    preferred_text_source = extraction_mode

    ocr_path = output_dir / f"{board_id}.ocr.txt"
    if ocr_path.exists():
        base_text = ""
        base_path = Path(text_path_value)
        if base_path.exists():
            base_text = base_path.read_text(encoding="utf-8", errors="ignore")
        ocr_text = ocr_path.read_text(encoding="utf-8")
        ocr_char_count = len(ocr_text)
        ocr_sha = hashlib.sha256(ocr_text.encode("utf-8")).hexdigest()
        meta["ocr_text_path"] = str(ocr_path)
        meta["ocr_text_sha256"] = ocr_sha
        meta["ocr_text_char_count"] = ocr_char_count

        # Prefer OCR over strings fallback when OCR is meaningfully more readable.
        if (
            extraction_mode == "strings_fallback"
            and _score_text_quality(ocr_text) > (_score_text_quality(base_text) * 1.35)
        ):
            preferred_text_path = str(ocr_path)
            preferred_text_sha = ocr_sha
            preferred_text_char_count = ocr_char_count
            preferred_text_source = "ocr_sidecar"
        # Otherwise prefer OCR text only when it is richer than base extraction.
        elif ocr_char_count > text_char_count:
            preferred_text_path = str(ocr_path)
            preferred_text_sha = ocr_sha
            preferred_text_char_count = ocr_char_count
            preferred_text_source = "ocr_sidecar"

    meta["preferred_text_path"] = preferred_text_path
    meta["preferred_text_sha256"] = preferred_text_sha
    meta["preferred_text_char_count"] = preferred_text_char_count
    meta["preferred_text_source"] = preferred_text_source
    return meta


def _extract_pages_with_ocr(pdf_bytes: bytes, *, dpi: int) -> list[str]:
    """Extract OCR page text using pdftoppm + tesseract available on PATH."""
    pdftoppm_cmd = shutil.which("pdftoppm")
    tesseract_cmd = shutil.which("tesseract")
    if not pdftoppm_cmd or not tesseract_cmd:
        raise RuntimeError("OCR tools unavailable (pdftoppm and tesseract are required on PATH)")

    with tempfile.TemporaryDirectory(prefix="monopoly-manual-ocr-") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        pdf_path = tmp_dir / "manual.pdf"
        pdf_path.write_bytes(pdf_bytes)
        image_prefix = tmp_dir / "page"

        render = subprocess.run(
            [pdftoppm_cmd, "-r", str(dpi), "-png", str(pdf_path), str(image_prefix)],
            capture_output=True,
            text=True,
            check=False,
        )
        if render.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {render.stderr.strip()}")

        image_paths = sorted(tmp_dir.glob("page-*.png"))
        if not image_paths:
            raise RuntimeError("pdftoppm produced no page images")

        pages: list[str] = []
        for image_path in image_paths:
            ocr = subprocess.run(
                [tesseract_cmd, str(image_path), "stdout", "--psm", "6"],
                capture_output=True,
                text=True,
                check=False,
            )
            if ocr.returncode != 0:
                raise RuntimeError(f"tesseract failed on {image_path.name}: {ocr.stderr.strip()}")
            pages.append(ocr.stdout.strip())
        return pages


def _score_text_quality(text: str) -> float:
    """Return a simple readability score for extracted text quality selection."""
    if not text:
        return 0.0
    words = re.findall(r"[A-Za-z]{2,}", text)
    if not words:
        return 0.0
    stopword_hits = sum(1 for word in words if word.lower() in QUALITY_STOPWORDS)
    stopword_ratio = stopword_hits / len(words)
    alpha_ratio = sum(char.isalpha() for char in text) / len(text)
    space_ratio = sum(char.isspace() for char in text) / len(text)
    return (stopword_ratio * 0.7) + (alpha_ratio * 0.2) + (space_ratio * 0.1)


def _maybe_write_ocr_sidecar(
    *,
    board_id: str,
    pdf_bytes: bytes,
    output_dir: Path,
    text_char_count: int,
    ocr_board_ids: set[str],
    ocr_when_text_below: int,
    ocr_dpi: int,
) -> None:
    """Optionally render OCR sidecar text for low-text or explicitly selected boards."""
    should_ocr = board_id in ocr_board_ids
    if ocr_when_text_below > 0 and text_char_count < ocr_when_text_below:
        should_ocr = True
    if not should_ocr:
        return

    try:
        ocr_pages = _extract_pages_with_ocr(pdf_bytes, dpi=ocr_dpi)
    except Exception as error:  # pragma: no cover - runtime dependency/tooling path
        print(f"[ocr-fail] {board_id}: {error}")
        return

    ocr_chunks: list[str] = []
    for idx, text in enumerate(ocr_pages, start=1):
        ocr_chunks.append(f"=== OCR Page {idx} ===\n{text}\n")
    ocr_text = "\n".join(ocr_chunks).strip() + "\n"
    ocr_path = output_dir / f"{board_id}.ocr.txt"
    ocr_path.write_text(ocr_text, encoding="utf-8")
    print(f"[ocr] {board_id}: pages={len(ocr_pages)} chars={len(ocr_text)}")


def _extract_pages_with_fallback(
    board_id: str,
    pdf_bytes: bytes,
    base_zlib_limit: int,
) -> tuple[list[str], int, str]:
    attempted_limits: list[int] = [base_zlib_limit]
    board_retry_limit = BOARD_ZLIB_RETRY_LIMITS.get(board_id)
    if (
        board_retry_limit is not None
        and board_retry_limit > base_zlib_limit
        and board_retry_limit not in attempted_limits
    ):
        attempted_limits.append(board_retry_limit)

    last_error: Exception | None = None
    for index, zlib_limit in enumerate(attempted_limits):
        pypdf_filters.ZLIB_MAX_OUTPUT_LENGTH = zlib_limit
        try:
            if index > 0:
                print(f"[retry] {board_id}: trying zlib limit {zlib_limit}")
            pages = _extract_pages(pdf_bytes)
            return pages, zlib_limit, "pypdf"
        except Exception as error:  # pragma: no cover - runtime decoding path
            last_error = error
            message = str(error)
            if "Limit reached while decompressing." not in message:
                raise
            if index == len(attempted_limits) - 1:
                fallback_text = _extract_text_strings_fallback(pdf_bytes)
                if fallback_text:
                    print(f"[fallback] {board_id}: using strings extraction fallback")
                    return [fallback_text], zlib_limit, "strings_fallback"
                raise

    assert last_error is not None
    raise last_error


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_cached_extraction_meta(board_id: str, output_dir: Path) -> dict[str, Any] | None:
    """Return previously extracted board metadata when still structurally valid."""
    meta_path = output_dir / f"{board_id}.json"
    if not meta_path.exists():
        return None
    try:
        cached = _load_json(meta_path)
    except Exception:
        return None
    if not isinstance(cached, dict):
        return None
    if str(cached.get("status", "")) != "ok":
        return None
    text_path_value = str(cached.get("text_path", "")).strip()
    if not text_path_value:
        return None
    text_path = Path(text_path_value)
    if not text_path.exists():
        return None
    return _attach_preferred_text_metadata(dict(cached), output_dir=output_dir)


def _select_targets(
    anchor_rows: list[dict[str, Any]],
    families: set[str],
    board_ids: set[str],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in anchor_rows:
        board_id = str(row.get("board_id", ""))
        family = str(row.get("family", ""))
        if board_ids and board_id in board_ids:
            selected.append(row)
            continue
        if families and family in families:
            selected.append(row)
    selected.sort(key=lambda row: str(row.get("board_id", "")))
    return selected


def run_extraction(
    *,
    families: set[str],
    board_ids: set[str],
    anchor_index_path: Path,
    manual_rules_dir: Path,
    output_dir: Path,
    timeout: float,
    zlib_max_output_length: int,
    merge_manifest: bool,
    ocr_board_ids: set[str],
    ocr_when_text_below: int,
    ocr_dpi: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    anchor_rows = _load_json(anchor_index_path)
    targets = _select_targets(anchor_rows, families=families, board_ids=board_ids)
    if not targets:
        raise SystemExit("No matching boards selected.")

    manifest_rows: list[dict[str, Any]] = []
    target_board_ids = {str(row.get("board_id", "")) for row in targets}
    if merge_manifest:
        existing_manifest_path = output_dir / "manifest.json"
        if existing_manifest_path.exists():
            existing_rows = _load_json(existing_manifest_path)
            if isinstance(existing_rows, list):
                for row in existing_rows:
                    if not isinstance(row, dict):
                        continue
                    board_id = str(row.get("board_id", ""))
                    if board_id and board_id not in target_board_ids:
                        manifest_rows.append(row)
    for row in targets:
        board_id = str(row["board_id"])
        family = str(row.get("family", ""))
        anchor_edition_id = str(row.get("anchor_edition_id", ""))
        rule_path = manual_rules_dir / f"{board_id}.json"
        if not rule_path.exists():
            manifest_rows.append(
                {
                    "board_id": board_id,
                    "family": family,
                    "anchor_edition_id": anchor_edition_id,
                    "status": "missing_manual_rule_file",
                }
            )
            continue

        rule_payload = _load_json(rule_path)
        manual_source = (
            rule_payload.get("mechanics", {}).get("manual_source", {})
            if isinstance(rule_payload.get("mechanics"), dict)
            else {}
        )
        pdf_url = str(manual_source.get("pdf_url", "")).strip()
        if not pdf_url:
            manifest_rows.append(
                {
                    "board_id": board_id,
                    "family": family,
                    "anchor_edition_id": anchor_edition_id,
                    "status": "missing_pdf_url",
                }
            )
            continue

        try:
            pdf_bytes = _fetch_pdf_bytes(pdf_url, timeout=timeout)
            pages, used_zlib_limit, extraction_mode = _extract_pages_with_fallback(
                board_id=board_id,
                pdf_bytes=pdf_bytes,
                base_zlib_limit=zlib_max_output_length,
            )
        except Exception as error:  # pragma: no cover - network/runtime failure path
            cached_meta = _load_cached_extraction_meta(board_id, output_dir=output_dir)
            if cached_meta is not None:
                cached_meta["status"] = "ok"
                manifest_rows.append(cached_meta)
                print(f"[cache-fallback] {board_id}: {error}")
                continue

            print(f"[fail] {board_id}: {error}")
            manifest_rows.append(
                {
                    "board_id": board_id,
                    "family": family,
                    "anchor_edition_id": anchor_edition_id,
                    "pdf_url": pdf_url,
                    "status": "failed",
                    "error": str(error),
                    "zlib_limit_attempted": zlib_max_output_length,
                }
            )
            continue

        text_path = output_dir / f"{board_id}.txt"
        text_chunks: list[str] = []
        for idx, text in enumerate(pages, start=1):
            text_chunks.append(f"=== Page {idx} ===\n{text}\n")
        full_text = "\n".join(text_chunks).strip() + "\n"
        text_path.write_text(full_text, encoding="utf-8")

        text_sha256 = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        text_char_count = len(full_text)
        _maybe_write_ocr_sidecar(
            board_id=board_id,
            pdf_bytes=pdf_bytes,
            output_dir=output_dir,
            text_char_count=text_char_count,
            ocr_board_ids=ocr_board_ids,
            ocr_when_text_below=ocr_when_text_below,
            ocr_dpi=ocr_dpi,
        )
        meta = {
            "board_id": board_id,
            "family": family,
            "anchor_edition_id": anchor_edition_id,
            "status": "ok",
            "pdf_url": pdf_url,
            "instruction_url": manual_source.get("instruction_url"),
            "filename": manual_source.get("filename"),
            "pdf_sha256": pdf_sha256,
            "pdf_size_bytes": len(pdf_bytes),
            "page_count": len(pages),
            "text_char_count": text_char_count,
            "text_sha256": text_sha256,
            "text_path": str(text_path),
            "zlib_limit_used": used_zlib_limit,
            "extraction_mode": extraction_mode,
        }
        meta = _attach_preferred_text_metadata(meta, output_dir=output_dir)
        _stable_dump(output_dir / f"{board_id}.json", meta)
        manifest_rows.append(meta)
        print(f"[ok] {board_id}: pages={len(pages)} chars={text_char_count}")

    manifest_rows = [_attach_preferred_text_metadata(dict(row), output_dir=output_dir) for row in manifest_rows]
    manifest_rows.sort(key=lambda item: str(item.get("board_id", "")))
    _stable_dump(output_dir / "manifest.json", manifest_rows)

    ok_count = sum(1 for row in manifest_rows if row.get("status") == "ok")
    print(
        f"Wrote extraction artifacts for {ok_count}/{len(manifest_rows)} "
        f"selected boards into {output_dir}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text from Monopoly board manual PDFs into local artifacts."
    )
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        help="Family id from special_board_anchor_index.json (repeatable).",
    )
    parser.add_argument(
        "--board-id",
        action="append",
        default=[],
        help="Explicit board id (repeatable).",
    )
    parser.add_argument(
        "--anchor-index",
        type=Path,
        default=Path("server/games/monopoly/catalog/special_board_anchor_index.json"),
        help="Path to special board anchor index JSON.",
    )
    parser.add_argument(
        "--manual-rules-dir",
        type=Path,
        default=Path("server/games/monopoly/manual_rules/data"),
        help="Directory containing board manual rule JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("server/games/monopoly/manual_rules/extracted"),
        help="Directory where extracted text/metadata artifacts are written.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=45.0,
        help="Download timeout in seconds for each manual PDF.",
    )
    parser.add_argument(
        "--zlib-max-output-length",
        type=int,
        default=120_000_000,
        help=(
            "pypdf decompression output limit for trusted large manual PDFs "
            "(0 disables limit)."
        ),
    )
    parser.add_argument(
        "--no-merge-manifest",
        action="store_true",
        help="Do not preserve existing manifest rows for non-target boards.",
    )
    parser.add_argument(
        "--ocr-board-id",
        action="append",
        default=[],
        help="Board id to force OCR sidecar generation for (repeatable).",
    )
    parser.add_argument(
        "--ocr-when-text-below",
        type=int,
        default=0,
        help=(
            "If >0, run OCR sidecar generation when extracted text char count "
            "is below this threshold."
        ),
    )
    parser.add_argument(
        "--ocr-dpi",
        type=int,
        default=400,
        help="DPI used for OCR rasterization when OCR sidecar generation is enabled.",
    )
    args = parser.parse_args()

    families = {value.strip() for value in args.family if value.strip()}
    board_ids = {value.strip() for value in args.board_id if value.strip()}
    ocr_board_ids = {value.strip() for value in args.ocr_board_id if value.strip()}
    if not families and not board_ids:
        raise SystemExit("Provide at least one --family or --board-id selection.")

    run_extraction(
        families=families,
        board_ids=board_ids,
        anchor_index_path=args.anchor_index,
        manual_rules_dir=args.manual_rules_dir,
        output_dir=args.output_dir,
        timeout=args.timeout,
        zlib_max_output_length=args.zlib_max_output_length,
        merge_manifest=not args.no_merge_manifest,
        ocr_board_ids=ocr_board_ids,
        ocr_when_text_below=args.ocr_when_text_below,
        ocr_dpi=args.ocr_dpi,
    )


if __name__ == "__main__":
    main()
