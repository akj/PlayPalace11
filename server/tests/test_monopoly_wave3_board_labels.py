"""Tests for Wave 3 Monopoly board label localization coverage."""

import pytest

from server.messages.localization import Localization

WAVE3_LABEL_KEYS = [
    "monopoly-board-disney-star-wars-dark-side",
    "monopoly-board-disney-legacy",
    "monopoly-board-disney-the-edition",
    "monopoly-board-lord-of-the-rings-trilogy",
    "monopoly-board-star-wars-saga",
    "monopoly-board-marvel-avengers-legacy",
    "monopoly-board-star-wars-legacy",
    "monopoly-board-star-wars-classic-edition",
    "monopoly-board-star-wars-solo",
    "monopoly-board-game-of-thrones",
    "monopoly-board-deadpool-collectors",
    "monopoly-board-toy-story",
    "monopoly-board-black-panther",
    "monopoly-board-stranger-things-collectors",
    "monopoly-board-ghostbusters",
    "monopoly-board-marvel-eternals",
    "monopoly-board-transformers",
    "monopoly-board-stranger-things-netflix",
    "monopoly-board-fortnite-collectors",
    "monopoly-board-star-wars-mandalorian-s2",
    "monopoly-board-transformers-beast-wars",
    "monopoly-board-marvel-falcon-winter-soldier",
    "monopoly-board-fortnite-flip",
    "monopoly-board-marvel-flip",
    "monopoly-board-pokemon",
]

LOCALES = ("en", "pl", "pt", "ru", "vi", "zh")


@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("label_key", WAVE3_LABEL_KEYS)
def test_wave3_board_label_keys_exist_per_locale(locale: str, label_key: str):
    value = Localization.get(locale, label_key)
    assert value != label_key
