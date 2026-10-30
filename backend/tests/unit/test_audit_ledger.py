"""Unit tests for Decision Ledger & Tamper Detection.

EPIC-09-T07: Decision Ledger unit tests:
- Hash-chain writer with SHA-256
- Canonical JSON determinism
- Chain verification on untampered ledger
- Tamper detection test (modifying entry payload breaks chain)
- Query filtering and pagination
"""

from __future__ import annotations

import pytest

from app.audit import DecisionLedger, LedgerEntry, canonical_json, compute_entry_hash


class TestDecisionLedger:
    def test_canonical_json_sorts_keys(self) -> None:
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        assert canonical_json(d1) == canonical_json(d2)

    def test_appends_entries_with_hash_chain(self) -> None:
        ledger = DecisionLedger()
        e1 = ledger.append(
            event_type="decision",
            action="model_selected",
            run_id="run_001",
            payload={"model": "gpt-4o"},
        )
        assert e1.sequence_number == 1
        assert e1.previous_hash == "0" * 64
        assert len(e1.entry_hash) == 64

        e2 = ledger.append(
            event_type="action",
            action="marks_updated",
            run_id="run_001",
            payload={"score": 85},
        )
        assert e2.sequence_number == 2
        assert e2.previous_hash == e1.entry_hash
        assert len(e2.entry_hash) == 64

    def test_chain_verification_succeeds_on_intact_ledger(self) -> None:
        ledger = DecisionLedger()
        for i in range(5):
            ledger.append(event_type="action", action=f"step_{i}", payload={"i": i})

        is_valid, last_seq = ledger.verify_chain()
        assert is_valid is True
        assert last_seq == 5

    def test_tamper_detection_reports_broken_chain(self) -> None:
        ledger = DecisionLedger()
        ledger.append(event_type="action", action="step_1", payload={"data": "original_1"})
        ledger.append(event_type="action", action="step_2", payload={"data": "original_2"})
        ledger.append(event_type="action", action="step_3", payload={"data": "original_3"})

        # Tamper with the second entry's payload
        ledger._entries[1].payload["data"] = "TAMPERED_DATA"

        is_valid, last_valid = ledger.verify_chain()
        assert is_valid is False
        assert last_valid == 1  # Entry 1 was last valid, Entry 2 was tampered

    def test_query_filtering_and_pagination(self) -> None:
        ledger = DecisionLedger()
        ledger.append(event_type="decision", action="act_1", run_id="run_A", agent_id="master")
        ledger.append(event_type="action", action="act_2", run_id="run_B", agent_id="evaluator")
        ledger.append(event_type="decision", action="act_3", run_id="run_A", agent_id="evaluator")

        # Filter by run_id
        res_a = ledger.query(run_id="run_A")
        assert len(res_a) == 2

        # Filter by event_type
        res_action = ledger.query(event_type="action")
        assert len(res_action) == 1

        # Pagination limit
        res_limit = ledger.query(limit=2)
        assert len(res_limit) == 2
