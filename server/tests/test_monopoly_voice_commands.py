"""Tests for deterministic Monopoly voice command parsing."""

from server.games.monopoly.voice_commands import parse_voice_command


def test_requires_exact_voice_prefix():
    assert parse_voice_command("voice: balance").intent == "check_balance"
    assert parse_voice_command("Voice: balance").error == "missing_prefix"
    assert parse_voice_command("balance").error == "missing_prefix"


def test_parses_transfer_and_ledger_commands():
    transfer = parse_voice_command("voice: transfer 200 to Guest")
    assert transfer.intent == "transfer_amount_to_player"
    assert transfer.amount == 200
    assert transfer.target_name == "Guest"

    ledger = parse_voice_command("voice: ledger")
    assert ledger.intent == "show_recent_ledger"


def test_reports_empty_payload_and_unknown_command():
    empty = parse_voice_command("voice:")
    assert empty.error == "empty_command"

    unknown = parse_voice_command("voice: dance")
    assert unknown.error == "unknown_command"
