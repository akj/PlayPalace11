# Monopoly Wave 5 Mario Collectors Promotion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Promote `mario_collectors` to include both card remap and card cash override behavior with deterministic tests.

**Architecture:** Reuse existing Wave 4 capability runtime (`card_id_remap`, `card_cash_override`) and add collectors-specific mapping data. Verify board-rules and skin-only divergence with targeted integration tests.

**Tech Stack:** Python 3.13, pytest, Monopoly board rule-pack modules and runtime hooks.

---

### Task 1: Add failing collectors contract tests
- Modify: `server/tests/test_monopoly_board_rules_registry.py`
- Modify: `server/tests/test_monopoly_mario_rule_packs.py`

### Task 2: Add failing collectors integration tests
- Modify: `server/tests/test_monopoly_mario_boards.py`

### Task 3: Implement collectors module mappings
- Modify: `server/games/monopoly/board_rules/mario_collectors.py`

### Task 4: Verify targeted suites
- Run collectors-focused tests and Mario-focused tests.

### Task 5: Run Monopoly regression
- Run `pytest -k monopoly -v` and confirm clean branch.
