"""Tests for Wave 1 Monopoly Mario board rule-pack modules."""

from server.games.monopoly.board_rules import mario_kart, mario_movie


def test_mario_pack_exposes_anchor_edition_id():
    assert mario_kart.ANCHOR_EDITION_ID.startswith("monopoly-")


def test_mario_pack_exposes_pass_go_contract():
    assert mario_movie.PASS_GO_CREDIT_OVERRIDE is None or isinstance(
        mario_movie.PASS_GO_CREDIT_OVERRIDE, int
    )
