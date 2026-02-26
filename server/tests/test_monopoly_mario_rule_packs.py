"""Tests for Wave 1 Monopoly Mario board rule-pack modules."""

from server.games.monopoly.board_rules import (
    mario_celebration,
    mario_collectors,
    mario_kart,
    mario_movie,
)


def test_mario_pack_exposes_anchor_edition_id():
    assert mario_kart.ANCHOR_EDITION_ID.startswith("monopoly-")


def test_mario_pack_exposes_pass_go_contract():
    assert mario_movie.PASS_GO_CREDIT_OVERRIDE is None or isinstance(
        mario_movie.PASS_GO_CREDIT_OVERRIDE, int
    )


def test_mario_kart_exports_card_id_remap_mapping():
    assert mario_kart.CARD_ID_REMAPS[("chance", "bank_dividend_50")] == "advance_to_go"


def test_mario_movie_exports_card_cash_override_mapping():
    assert mario_movie.CARD_CASH_OVERRIDES["bank_dividend_50"] == 120


def test_mario_collectors_exports_card_id_remap_mapping():
    assert mario_collectors.CARD_ID_REMAPS[("chance", "go_back_three")] == "bank_dividend_50"


def test_mario_collectors_exports_card_cash_override_mapping():
    assert mario_collectors.CARD_CASH_OVERRIDES["bank_error_collect_200"] == 250


def test_mario_celebration_exports_card_id_remap_mapping():
    assert mario_celebration.CARD_ID_REMAPS[("chance", "poor_tax_15")] == "bank_dividend_50"


def test_mario_celebration_exports_card_cash_override_mapping():
    assert mario_celebration.CARD_CASH_OVERRIDES["income_tax_refund_20"] == 60
