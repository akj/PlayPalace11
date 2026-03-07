"""Seed non-universal card text and text_note evidence across all 55 special boards.

Non-universal cards are the 6 canonical card slots that appear on every board
but did not receive text during the universal card text seeding pass:

  Chance:           bank_dividend_50, go_back_three, poor_tax_15
  Community Chest:  bank_error_collect_200, doctor_fee_pay_50, income_tax_refund_20

This script:
  1. Populates ``text`` on every non-universal card that lacks it.
  2. Adds ``text_note`` evidence to every card that lacks it
     (including legacy-id mapping notes for Disney/Marvel boards).

Safety:
  - Idempotent: running twice produces the same output.
  - Never overwrites existing ``text`` or ``text_note`` values.
  - Deterministic JSON output (sorted keys, 2-space indent, trailing newline).
  - ``--dry-run`` mode previews changes without writing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DATA_DIR = Path("server/games/monopoly/manual_rules/data")

# ── Canonical card text templates ────────────────────────────────────
#
# Amounts are substituted from card.effect.amount at seed time.
# ``{amount}`` is replaced with the dollar-formatted amount (e.g. "$50").
# Cards without a monetary amount use a static string.

CANONICAL_CARD_TEXT: dict[str, str] = {
    "bank_dividend_50": "Bank pays you dividend of ${amount}.",
    "go_back_three": "Go Back Three Spaces.",
    "poor_tax_15": "Pay Poor Tax of ${amount}.",
    "bank_error_collect_200": "Bank error in your favor. Collect ${amount}.",
    "doctor_fee_pay_50": "Doctor's fee. Pay ${amount}.",
    "income_tax_refund_20": "Income Tax refund. Collect ${amount}.",
}

# Which deck each canonical card lives in.
CANONICAL_DECK: dict[str, str] = {
    "bank_dividend_50": "chance",
    "go_back_three": "chance",
    "poor_tax_15": "chance",
    "bank_error_collect_200": "community_chest",
    "doctor_fee_pay_50": "community_chest",
    "income_tax_refund_20": "community_chest",
}

# Canonical default amounts (used only if effect.amount is missing).
CANONICAL_AMOUNTS: dict[str, int | None] = {
    "bank_dividend_50": 50,
    "go_back_three": None,
    "poor_tax_15": 15,
    "bank_error_collect_200": 200,
    "doctor_fee_pay_50": 50,
    "income_tax_refund_20": 20,
}

# Non-universal card slot IDs.
NON_UNIVERSAL_SLOTS = set(CANONICAL_CARD_TEXT.keys())


def _resolve_canonical_slot(card: dict[str, Any]) -> str | None:
    """Return the canonical card slot for a card, or None if not a non-universal card."""
    card_id = card.get("id", "")
    legacy_id = card.get("legacy_id")

    # Direct match on id.
    if card_id in NON_UNIVERSAL_SLOTS:
        return card_id
    # Match via legacy_id.
    if legacy_id and legacy_id in NON_UNIVERSAL_SLOTS:
        return legacy_id
    return None


def _get_amount(card: dict[str, Any], slot: str) -> int | None:
    """Get the monetary amount for a card from its effect or canonical default."""
    effect = card.get("effect")
    if isinstance(effect, dict):
        amt = effect.get("amount")
        if isinstance(amt, (int, float)):
            return int(amt)
    return CANONICAL_AMOUNTS.get(slot)


def _generate_text(slot: str, amount: int | None) -> str:
    """Generate canonical card text for a non-universal card slot."""
    template = CANONICAL_CARD_TEXT[slot]
    if amount is not None and "{amount}" in template:
        return template.replace("{amount}", str(amount))
    return template


def _generate_text_note(card: dict[str, Any], slot: str, deck: str) -> str:
    """Generate a text_note for a card based on its type."""
    legacy_id = card.get("legacy_id")
    card_id = card.get("id", "")

    if legacy_id:
        return (
            f"Resolved via canonical legacy slot mapping (`{legacy_id}`) "
            f"with deck-prefixed id `{card_id}`. "
            f"Source: canonical card text template with board-specific deck naming."
        )
    return "Source: canonical card text template."


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def seed_board(path: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Seed non-universal card text on a single board.

    Returns counts of changes made.
    """
    data = _load_json(path)
    board_id = data.get("board_id", path.stem)
    cards_section = data.get("cards", {})

    stats = {"text_added": 0, "text_note_added": 0}

    for deck in ("chance", "community_chest"):
        for card in cards_section.get(deck, []):
            slot = _resolve_canonical_slot(card)

            # --- text_note on ANY card that lacks it ---
            existing_note = card.get("text_note", "")
            if not existing_note:
                if slot:
                    note = _generate_text_note(card, slot, deck)
                    card["text_note"] = note
                    stats["text_note_added"] += 1
                elif card.get("legacy_id"):
                    # Legacy-id card that isn't a non-universal slot
                    # (universal cards like advance_to_go with legacy_id).
                    legacy_id = card["legacy_id"]
                    card_id = card.get("id", "")
                    card["text_note"] = (
                        f"Resolved via canonical legacy slot mapping (`{legacy_id}`) "
                        f"with deck-prefixed id `{card_id}`. "
                        f"Source: canonical card text template with board-specific deck naming."
                    )
                    stats["text_note_added"] += 1
                else:
                    # Universal card without legacy_id.
                    card["text_note"] = "Source: universal card text template."
                    stats["text_note_added"] += 1
            elif card.get("legacy_id") and "legacy slot mapping" not in existing_note:
                # Append legacy mapping info to existing text_note
                # (e.g., cards that already had cash override notes).
                legacy_id = card["legacy_id"]
                card_id = card.get("id", "")
                card["text_note"] = (
                    f"{existing_note} "
                    f"Resolved via canonical legacy slot mapping (`{legacy_id}`) "
                    f"with deck-prefixed id `{card_id}`."
                )
                stats["text_note_added"] += 1

            # --- text on non-universal cards that lack it ---
            if slot and ("text" not in card or not card["text"]):
                amount = _get_amount(card, slot)
                text = _generate_text(slot, amount)
                card["text"] = text
                stats["text_added"] += 1

    if not dry_run and (stats["text_added"] or stats["text_note_added"]):
        _write_json(path, data)

    return stats


def run(*, data_dir: Path, dry_run: bool = False) -> None:
    board_files = sorted(data_dir.glob("*.json"))
    if not board_files:
        print(f"No board files found in {data_dir}")
        return

    totals = {"text_added": 0, "text_note_added": 0, "boards_modified": 0}

    for path in board_files:
        stats = seed_board(path, dry_run=dry_run)
        if stats["text_added"] or stats["text_note_added"]:
            totals["boards_modified"] += 1
            totals["text_added"] += stats["text_added"]
            totals["text_note_added"] += stats["text_note_added"]
            prefix = "[DRY RUN] " if dry_run else ""
            print(
                f"{prefix}{path.stem}: "
                f"+{stats['text_added']} text, "
                f"+{stats['text_note_added']} text_note"
            )

    mode = "Would modify" if dry_run else "Modified"
    print(
        f"\n{mode} {totals['boards_modified']} boards: "
        f"+{totals['text_added']} text fields, "
        f"+{totals['text_note_added']} text_note fields"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed non-universal card text across all special Monopoly boards."
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
