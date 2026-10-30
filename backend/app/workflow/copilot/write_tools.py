"""Write Tool Confirmation Cards Engine (EPIC-17-T03).

Generates structured confirmation card tokens for mutating actions
(e.g., publishing marks, mass notifications, enrollments) before execution.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConfirmationCardData:
    confirmation_token: str
    action_name: str
    description: str
    risk_level: str  # "low", "medium", "high", "critical"
    affected_entity: str
    parameters: dict[str, Any]
    diff_summary: dict[str, Any]
    created_at: float
    expires_at: float
    is_confirmed: bool = False
    is_cancelled: bool = False


class WriteToolConfirmationManager:
    """Manages creation, verification, and execution of confirmation cards."""

    def __init__(self, token_ttl_seconds: int = 300) -> None:
        self.token_ttl_seconds = token_ttl_seconds
        self._pending_cards: dict[str, ConfirmationCardData] = {}

    def prepare_write_card(
        self,
        action_name: str,
        description: str,
        risk_level: str,
        affected_entity: str,
        parameters: dict[str, Any],
        diff_summary: dict[str, Any] | None = None,
    ) -> ConfirmationCardData:
        """Create a new confirmation card requiring human approval."""
        token = f"cf_{secrets.token_hex(16)}"
        now = time.time()

        card = ConfirmationCardData(
            confirmation_token=token,
            action_name=action_name,
            description=description,
            risk_level=risk_level,
            affected_entity=affected_entity,
            parameters=parameters,
            diff_summary=diff_summary or {},
            created_at=now,
            expires_at=now + self.token_ttl_seconds,
        )

        self._pending_cards[token] = card
        return card

    def confirm_action(self, token: str) -> tuple[bool, str, ConfirmationCardData | None]:
        """Confirm and validate card token before triggering execution."""
        card = self._pending_cards.get(token)
        if not card:
            return False, "Confirmation token not found or already executed", None

        if time.time() > card.expires_at:
            del self._pending_cards[token]
            return False, "Confirmation token has expired. Please re-initiate the action.", None

        if card.is_cancelled:
            return False, "Action was previously cancelled", None

        card.is_confirmed = True
        del self._pending_cards[token]
        return True, "Action successfully confirmed", card

    def cancel_action(self, token: str) -> tuple[bool, str]:
        """Cancel a pending write card."""
        card = self._pending_cards.get(token)
        if not card:
            return False, "Confirmation token not found"

        card.is_cancelled = True
        del self._pending_cards[token]
        return True, "Action cancelled successfully"
