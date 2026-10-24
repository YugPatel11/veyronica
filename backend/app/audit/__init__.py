"""Decision Ledger — Hash-chained audit trail.

EPIC-09-T01: Hash-chain ledger writer.
EPIC-09-T02: Chain verification.
EPIC-09-T03: Canonical JSON serialisation.
EPIC-09-T04: Ledger query API.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class LedgerEntry(BaseModel):
    """A single hash-chained audit entry."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sequence_number: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str | None = None
    task_id: str | None = None
    agent_id: str | None = None
    user_id: str | None = None
    event_type: str  # decision, action, approval, connector_call, error
    action: str
    entity_type: str | None = None
    entity_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    reasoning: str | None = None
    confidence: float | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    previous_hash: str = "0" * 64
    entry_hash: str = ""


def canonical_json(data: dict[str, Any]) -> str:
    """EPIC-09-T03: Deterministic JSON serialisation for hashing."""
    return json.dumps(data, sort_keys=True, default=str, separators=(",", ":"))


def compute_entry_hash(entry: LedgerEntry) -> str:
    """Compute SHA-256 hash of a ledger entry."""
    data = {
        "seq": entry.sequence_number,
        "ts": entry.timestamp.isoformat(),
        "event_type": entry.event_type,
        "action": entry.action,
        "payload": entry.payload,
        "previous_hash": entry.previous_hash,
    }
    return hashlib.sha256(canonical_json(data).encode()).hexdigest()


class DecisionLedger:
    """Append-only, hash-chained decision ledger.

    EPIC-09-T01: Write entries with hash chain.
    EPIC-09-T02: Verify chain integrity.
    """

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []
        self._sequence = 0

    def append(
        self,
        event_type: str,
        action: str,
        *,
        run_id: str | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        payload: dict[str, Any] | None = None,
        reasoning: str | None = None,
        confidence: float | None = None,
        model_used: str | None = None,
        tokens_used: int | None = None,
    ) -> LedgerEntry:
        """Append a new entry to the ledger with hash chain."""
        self._sequence += 1
        previous_hash = self._entries[-1].entry_hash if self._entries else "0" * 64

        entry = LedgerEntry(
            sequence_number=self._sequence,
            event_type=event_type,
            action=action,
            run_id=run_id,
            task_id=task_id,
            agent_id=agent_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
            reasoning=reasoning,
            confidence=confidence,
            model_used=model_used,
            tokens_used=tokens_used,
            previous_hash=previous_hash,
        )
        entry.entry_hash = compute_entry_hash(entry)
        self._entries.append(entry)

        logger.info("ledger_entry_appended", seq=self._sequence, event=event_type, action=action)
        return entry

    def verify_chain(self) -> tuple[bool, int]:
        """EPIC-09-T02: Verify the entire hash chain.

        Returns (is_valid, last_verified_sequence).
        """
        if not self._entries:
            return True, 0

        prev_hash = "0" * 64
        for entry in self._entries:
            # Check previous hash link
            if entry.previous_hash != prev_hash:
                logger.error("chain_broken_previous", seq=entry.sequence_number)
                return False, entry.sequence_number - 1

            # Recompute and verify entry hash
            expected = compute_entry_hash(entry)
            if entry.entry_hash != expected:
                logger.error("chain_broken_hash", seq=entry.sequence_number)
                return False, entry.sequence_number - 1

            prev_hash = entry.entry_hash

        return True, self._entries[-1].sequence_number

    def query(
        self,
        *,
        run_id: str | None = None,
        event_type: str | None = None,
        agent_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LedgerEntry]:
        """EPIC-09-T04: Query ledger entries with filters."""
        filtered = self._entries

        if run_id:
            filtered = [e for e in filtered if e.run_id == run_id]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if agent_id:
            filtered = [e for e in filtered if e.agent_id == agent_id]

        return filtered[offset:offset + limit]

    @property
    def count(self) -> int:
        return len(self._entries)


# Singleton
ledger = DecisionLedger()
