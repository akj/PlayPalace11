"""Rule-pack constants for jurassic_park board."""

RULE_PACK_ID = "jurassic_park"
ANCHOR_EDITION_ID = "monopoly-f1662"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "electronic_gate_sound_unit",
)
CARD_ID_REMAPS = {
    ("chance", "bank_dividend_50"): "go_back_three",
}
CARD_CASH_OVERRIDES: dict[str, int] = {}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
