"""Install one original Monopoly hardware sound replacement asset.

Usage:
    python server/scripts/monopoly/install_hardware_sound_replacement.py \
      --event junior_coin_sound_powerup \
      --source /abs/path/to/source.ogg
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from server.games.monopoly.hardware_emulation import HARDWARE_EVENT_SOUND_PROFILES


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_target_asset(event_id: str) -> str:
    profile = HARDWARE_EVENT_SOUND_PROFILES[event_id]
    target = profile.get("original_asset", "")
    if not target:
        raise ValueError(f"event {event_id!r} does not define an original_asset target")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install an original Monopoly hardware sound replacement."
    )
    parser.add_argument(
        "--event",
        required=True,
        choices=sorted(HARDWARE_EVENT_SOUND_PROFILES),
        help="Hardware event id to replace.",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source audio file path (.ogg preferred).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing files.",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"source file not found: {source_path}")

    target_asset = _resolve_target_asset(args.event)
    target_path = _repo_root() / "client" / "sounds" / target_asset

    if args.dry_run:
        print(f"[dry-run] event={args.event}")
        print(f"[dry-run] source={source_path}")
        print(f"[dry-run] target={target_path}")
        return 0

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    print(f"Installed original sound for {args.event}: {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
