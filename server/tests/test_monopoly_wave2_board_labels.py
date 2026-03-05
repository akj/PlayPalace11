"""Tests for Wave 2 Monopoly board label localization coverage."""

import pytest

from server.messages.localization import Localization

WAVE2_LABEL_KEYS = [
    "monopoly-board-disney-princesses",
    "monopoly-board-disney-animation",
    "monopoly-board-disney-lion-king",
    "monopoly-board-disney-mickey-friends",
    "monopoly-board-disney-villains",
    "monopoly-board-disney-lightyear",
    "monopoly-board-marvel-80-years",
    "monopoly-board-marvel-avengers",
    "monopoly-board-marvel-spider-man",
    "monopoly-board-marvel-black-panther-wf",
    "monopoly-board-marvel-super-villains",
    "monopoly-board-marvel-deadpool",
    "monopoly-board-star-wars-40th",
    "monopoly-board-star-wars-boba-fett",
    "monopoly-board-star-wars-light-side",
    "monopoly-board-star-wars-the-child",
    "monopoly-board-star-wars-mandalorian",
    "monopoly-board-star-wars-complete-saga",
    "monopoly-board-harry-potter",
    "monopoly-board-fortnite",
    "monopoly-board-stranger-things",
    "monopoly-board-jurassic-park",
    "monopoly-board-lord-of-the-rings",
    "monopoly-board-animal-crossing",
    "monopoly-board-barbie",
]

LOCALES = ("en", "pl", "pt", "ru", "vi", "zh")


@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("label_key", WAVE2_LABEL_KEYS)
def test_wave2_board_label_keys_exist_per_locale(locale: str, label_key: str):
    value = Localization.get(locale, label_key)
    assert value != label_key
