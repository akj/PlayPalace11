"""Refine non-universal card text on themed-currency boards for consistency.

18 of 55 boards have themed universal card text (e.g., "Collect 200 Credits"),
but their 6 non-universal cards still use canonical English ``$`` notation
(e.g., "Bank pays you dividend of $50.").  Additionally, ``disney_princesses``
has Portuguese universal text but English non-universal text.

This script replaces ``text`` on non-universal cards with themed versions:
  - Star Wars (12 boards): ``$X`` → ``X Credits``
  - Mario (4) / Pokemon (1) / Transformers (1): drop ``$`` symbol
  - Disney Princesses (1): translate to Portuguese

Safety:
  - Idempotent: running twice produces the same output.
  - Deterministic JSON output (sorted keys, 2-space indent, trailing newline).
  - ``--dry-run`` mode previews changes without writing.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DATA_DIR = Path("server/games/monopoly/manual_rules/data")

# ── Themed board configuration ──────────────────────────────────────
#
# mode=substitute: replace ``$X`` with ``X {currency}`` in existing text
# mode=drop_symbol: remove ``$`` from existing text
# mode=portuguese: replace text entirely with Portuguese translation

THEMED_CURRENCY_BOARDS: dict[str, dict[str, str]] = {
    # Star Wars: 1:1 Credits
    "star_wars_saga": {"currency": "Credits", "mode": "substitute"},
    "star_wars_mandalorian": {"currency": "Credits", "mode": "substitute"},
    "star_wars_mandalorian_s2": {"currency": "Credits", "mode": "substitute"},
    "star_wars_complete_saga": {"currency": "Credits", "mode": "substitute"},
    "star_wars_boba_fett": {"currency": "Credits", "mode": "substitute"},
    "star_wars_solo": {"currency": "Credits", "mode": "substitute"},
    "star_wars_the_child": {"currency": "Credits", "mode": "substitute"},
    "star_wars_light_side": {"currency": "Credits", "mode": "substitute"},
    "star_wars_40th": {"currency": "Credits", "mode": "substitute"},
    "star_wars_classic_edition": {"currency": "Credits", "mode": "substitute"},
    "star_wars_legacy": {"currency": "Credits", "mode": "substitute"},
    "disney_star_wars_dark_side": {"currency": "Credits", "mode": "substitute"},
    # Mario: drop $ symbol
    "mario_celebration": {"mode": "drop_symbol"},
    "mario_kart": {"mode": "drop_symbol"},
    "mario_movie": {"mode": "drop_symbol"},
    "junior_super_mario": {"mode": "drop_symbol"},
    # Pokemon: drop $ symbol
    "pokemon": {"mode": "drop_symbol"},
    # Transformers Beast Wars: drop $ symbol
    "transformers_beast_wars": {"mode": "drop_symbol"},
    # Disney Princesses: Portuguese
    "disney_princesses": {"mode": "portuguese"},
}

# ── Portuguese translations ─────────────────────────────────────────
#
# Uses ``A`` prefix notation to match existing universal card text style
# on the disney_princesses board (e.g., "Recebe A200.").
# Amounts are substituted from the card's existing text at runtime.

PORTUGUESE_TEMPLATES: dict[str, str] = {
    "bank_dividend_50": "O banco paga-te um dividendo de A{amount}.",
    "go_back_three": "Recua Três Casas.",
    "poor_tax_15": "Paga Taxa de Pobreza de A{amount}.",
    "bank_error_collect_200": "Erro bancário a teu favor. Recebe A{amount}.",
    "doctor_fee_pay_50": "Taxa do médico. Paga A{amount}.",
    "income_tax_refund_20": "Reembolso de Imposto. Recebe A{amount}.",
}

# Non-universal card slot IDs.
NON_UNIVERSAL_SLOTS = set(PORTUGUESE_TEMPLATES.keys())


def _resolve_canonical_slot(card: dict[str, Any]) -> str | None:
    """Return the canonical card slot for a card, or None if not non-universal."""
    card_id = card.get("id", "")
    legacy_id = card.get("legacy_id")

    if card_id in NON_UNIVERSAL_SLOTS:
        return card_id
    if legacy_id and legacy_id in NON_UNIVERSAL_SLOTS:
        return legacy_id
    return None


def _extract_amount(text: str) -> str | None:
    """Extract the dollar amount from canonical card text like '$50' or '$200'."""
    m = re.search(r"\$(\d+)", text)
    return m.group(1) if m else None


def _transform_text(
    text: str,
    slot: str,
    config: dict[str, str],
) -> str:
    """Transform card text according to the themed board config."""
    mode = config["mode"]

    if mode == "substitute":
        # Replace $X with X {currency}
        currency = config["currency"]
        return re.sub(r"\$(\d+)", rf"\1 {currency}", text)

    if mode == "drop_symbol":
        # Remove $ symbol, keep the number
        return text.replace("$", "")

    if mode == "portuguese":
        template = PORTUGUESE_TEMPLATES[slot]
        if "{amount}" in template:
            amount = _extract_amount(text)
            if amount is not None:
                return template.replace("{amount}", amount)
        return template

    return text


def _is_already_themed(text: str, config: dict[str, str]) -> bool:
    """Check if text has already been themed (idempotency guard)."""
    mode = config["mode"]

    if mode == "substitute":
        currency = config["currency"]
        # Already themed if it contains "X Credits" and no "$"
        return "$" not in text and currency in text

    if mode == "drop_symbol":
        # Already themed if no "$" remains (but "Go Back Three Spaces." never had $)
        return "$" not in text

    if mode == "portuguese":
        # Already Portuguese if it doesn't match English canonical patterns
        english_markers = ["Bank pays", "Go Back", "Pay Poor Tax", "Bank error", "Doctor's fee", "Income Tax refund"]
        return not any(marker in text for marker in english_markers)

    return False


def _themed_text_note_suffix(config: dict[str, str]) -> str:
    """Return the text_note suffix for a themed transformation."""
    mode = config["mode"]
    if mode == "substitute":
        currency = config["currency"]
        return f" Themed currency: {currency}."
    if mode == "drop_symbol":
        return " Currency symbol removed for themed consistency."
    if mode == "portuguese":
        return " Translated to Portuguese for disney_princesses edition."
    return ""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def refine_board(path: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Refine themed card text on a single board.

    Returns counts of changes made.
    """
    data = _load_json(path)
    board_id = data.get("board_id", path.stem)

    config = THEMED_CURRENCY_BOARDS.get(board_id)
    if config is None:
        return {"text_refined": 0, "text_note_updated": 0}

    cards_section = data.get("cards", {})
    stats = {"text_refined": 0, "text_note_updated": 0}

    for deck in ("chance", "community_chest"):
        for card in cards_section.get(deck, []):
            slot = _resolve_canonical_slot(card)
            if slot is None:
                continue

            text = card.get("text", "")
            if not text:
                continue

            # Skip if already themed.
            if _is_already_themed(text, config):
                continue

            # Transform the text.
            new_text = _transform_text(text, slot, config)
            if new_text == text:
                continue

            card["text"] = new_text
            stats["text_refined"] += 1

            # Append themed info to text_note (never overwrite).
            suffix = _themed_text_note_suffix(config)
            existing_note = card.get("text_note", "")
            if suffix and suffix not in existing_note:
                card["text_note"] = existing_note + suffix
                stats["text_note_updated"] += 1

    if not dry_run and (stats["text_refined"] or stats["text_note_updated"]):
        _write_json(path, data)

    return stats


def run(*, data_dir: Path, dry_run: bool = False) -> None:
    board_files = sorted(data_dir.glob("*.json"))
    if not board_files:
        print(f"No board files found in {data_dir}")
        return

    totals = {"text_refined": 0, "text_note_updated": 0, "boards_modified": 0}

    for path in board_files:
        stats = refine_board(path, dry_run=dry_run)
        if stats["text_refined"] or stats["text_note_updated"]:
            totals["boards_modified"] += 1
            totals["text_refined"] += stats["text_refined"]
            totals["text_note_updated"] += stats["text_note_updated"]
            prefix = "[DRY RUN] " if dry_run else ""
            print(
                f"{prefix}{path.stem}: "
                f"+{stats['text_refined']} text refined, "
                f"+{stats['text_note_updated']} text_note updated"
            )

    mode = "Would modify" if dry_run else "Modified"
    print(
        f"\n{mode} {totals['boards_modified']} boards: "
        f"+{totals['text_refined']} text fields refined, "
        f"+{totals['text_note_updated']} text_note fields updated"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refine themed card text on special Monopoly boards."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Path to the board data directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files.",
    )
    args = parser.parse_args()
    run(data_dir=args.data_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
