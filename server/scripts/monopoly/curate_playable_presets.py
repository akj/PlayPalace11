"""Curate Monopoly catalog artifacts and generate playable preset groups."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, UTC
import json
from pathlib import Path
import re
import sys


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def _stable_dump(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def _normalize_sku_for_merge(sku: str) -> str:
    sku = sku.strip()
    if sku.isdigit():
        return sku.lstrip("0") or "0"
    return sku.upper()


def _normalize_name_for_merge(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _text_blob(edition: dict) -> str:
    return f"{edition.get('display_name', '')} {edition.get('canonical_slug', '')}".lower()


def _match_family(text: str) -> str:
    checks = [
        ("junior", "junior"),
        ("cheaters", "cheaters"),
        ("voice banking", "voice_banking"),
        ("electronic banking", "electronic_banking"),
        ("super electronic", "electronic_banking"),
        ("bid", "bid_card_game"),
        (" deal", "deal_card_game"),
        ("knockout", "knockout"),
        ("speed", "speed"),
        ("sore losers", "sore_losers"),
        ("free parking jackpot", "free_parking_jackpot"),
        ("builder", "builder"),
        ("city", "city"),
    ]
    for needle, family in checks:
        if needle in text:
            return family
    return "classic_and_themed_standard"


def curate_catalog(editions: list[dict], manuals: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """Merge obvious duplicate editions and update manual variant references."""
    merge_groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for edition in editions:
        merge_key = (
            _normalize_sku_for_merge(edition["sku"]),
            edition["canonical_slug"].lower(),
            _normalize_name_for_merge(edition["display_name"]),
        )
        merge_groups[merge_key].append(edition)

    edition_id_remap: dict[str, str] = {}
    curated_editions: list[dict] = []
    merged_sets: list[dict] = []
    for merge_key, group in sorted(merge_groups.items(), key=lambda item: item[0]):
        if len(group) == 1:
            curated_editions.append(group[0])
            continue

        normalized_sku = merge_key[0]
        sorted_group = sorted(group, key=lambda e: (e["sku"] != normalized_sku, e["sku"]))
        primary = dict(sorted_group[0])
        primary["sku"] = normalized_sku
        primary["edition_id"] = f"monopoly-{normalized_sku.lower()}"

        merged_from = []
        for duplicate in sorted_group:
            edition_id_remap[duplicate["edition_id"]] = primary["edition_id"]
            merged_from.append(duplicate["edition_id"])
        curated_editions.append(primary)
        merged_sets.append(
            {
                "merge_key": list(merge_key),
                "primary_edition_id": primary["edition_id"],
                "merged_edition_ids": merged_from,
            }
        )

    for edition in curated_editions:
        edition_id_remap.setdefault(edition["edition_id"], edition["edition_id"])

    curated_manuals_raw: list[dict] = []
    for manual in manuals:
        row = dict(manual)
        original_id = row["edition_id"]
        row["edition_id"] = edition_id_remap.get(original_id, original_id)
        if row.get("sku"):
            row["sku"] = _normalize_sku_for_merge(str(row["sku"]))
        curated_manuals_raw.append(row)

    deduped_manuals: list[dict] = []
    seen_manual_keys: set[tuple[str, str, str, str]] = set()
    for row in sorted(
        curated_manuals_raw,
        key=lambda r: (
            r.get("edition_id", ""),
            r.get("locale", ""),
            r.get("filename", ""),
            r.get("pdf_url", ""),
        ),
    ):
        dedupe_key = (
            row.get("edition_id", ""),
            row.get("locale", ""),
            row.get("instruction_url", ""),
            row.get("pdf_url", ""),
        )
        if dedupe_key in seen_manual_keys:
            continue
        seen_manual_keys.add(dedupe_key)
        deduped_manuals.append(row)

    curated_editions.sort(key=lambda e: (e["sku"], e["edition_id"]))
    qa_report = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "input_editions_count": len(editions),
        "input_manual_variants_count": len(manuals),
        "curated_editions_count": len(curated_editions),
        "curated_manual_variants_count": len(deduped_manuals),
        "merged_duplicate_sets_count": len(merged_sets),
        "merged_duplicate_sets": merged_sets,
    }
    return curated_editions, deduped_manuals, qa_report


def build_playable_presets(curated_editions: list[dict]) -> dict:
    """Build preset group definitions from curated editions."""
    families: dict[str, list[str]] = defaultdict(list)
    for edition in curated_editions:
        family = _match_family(_text_blob(edition))
        families[family].append(edition["edition_id"])

    presets_meta = {
        "classic_and_themed_standard": (
            "classic_standard",
            "Classic and Themed Standard",
            "Standard Monopoly ruleset including licensed/theme boards with classic flow.",
        ),
        "junior": ("junior", "Monopoly Junior", "Junior rules family."),
        "cheaters": ("cheaters", "Monopoly Cheaters Edition", "Cheaters rules family."),
        "electronic_banking": (
            "electronic_banking",
            "Electronic Banking",
            "Electronic/Super Electronic Banking variants.",
        ),
        "voice_banking": ("voice_banking", "Voice Banking", "Voice banking variant family."),
        "bid_card_game": ("bid_card_game", "Monopoly Bid", "Bid card game family."),
        "deal_card_game": ("deal_card_game", "Monopoly Deal", "Deal card game family."),
        "knockout": ("knockout", "Monopoly Knockout", "Knockout family."),
        "speed": ("speed", "Monopoly Speed", "Speed family."),
        "sore_losers": ("sore_losers", "Monopoly for Sore Losers", "Sore Losers family."),
        "free_parking_jackpot": (
            "free_parking_jackpot",
            "Free Parking Jackpot",
            "Free Parking Jackpot variant family.",
        ),
        "builder": ("builder", "Monopoly Builder", "Builder variant family."),
        "city": ("city", "Monopoly City", "Monopoly City family."),
    }

    presets: list[dict] = []
    for family, edition_ids in sorted(families.items()):
        meta = presets_meta.get(
            family,
            (
                family,
                family.replace("_", " ").title(),
                "Auto-classified rules family.",
            ),
        )
        edition_ids_sorted = sorted(set(edition_ids))
        presets.append(
            {
                "preset_id": meta[0],
                "family_key": family,
                "name": meta[1],
                "description": meta[2],
                "edition_count": len(edition_ids_sorted),
                "anchor_edition_id": edition_ids_sorted[0] if edition_ids_sorted else "",
                "edition_ids": edition_ids_sorted,
            }
        )

    roadmap_order = [
        "classic_standard",
        "junior",
        "cheaters",
        "electronic_banking",
        "voice_banking",
        "sore_losers",
        "speed",
        "builder",
        "city",
        "bid_card_game",
        "deal_card_game",
        "knockout",
        "free_parking_jackpot",
    ]

    return {
        "version": 1,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "preset_count": len(presets),
        "playable_roadmap_order": roadmap_order,
        "presets": presets,
    }


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Curate monopoly catalog outputs and generate playable presets."
    )
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=Path("server/games/monopoly/catalog"),
        help="Path containing monopoly_editions.json and monopoly_manual_variants.json",
    )
    args = parser.parse_args()

    catalog_dir = args.catalog_dir
    editions = json.loads((catalog_dir / "monopoly_editions.json").read_text(encoding="utf-8"))
    manuals = json.loads(
        (catalog_dir / "monopoly_manual_variants.json").read_text(encoding="utf-8")
    )

    curated_editions, curated_manuals, qa_report = curate_catalog(editions, manuals)
    presets = build_playable_presets(curated_editions)

    _stable_dump(catalog_dir / "monopoly_editions_curated.json", curated_editions)
    _stable_dump(
        catalog_dir / "monopoly_manual_variants_curated.json",
        curated_manuals,
    )
    _stable_dump(catalog_dir / "catalog_qa_report.json", qa_report)
    _stable_dump(catalog_dir / "playable_presets.json", presets)

    print(
        "Curated catalog and presets written:",
        len(curated_editions),
        "editions,",
        len(curated_manuals),
        "manual variants,",
        len(presets["presets"]),
        "presets",
    )


if __name__ == "__main__":
    main()

