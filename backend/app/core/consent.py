"""Student and Parent Consent Management.

EPIC-24-T06: Consent management for student data and notification channels.
Prevents automated communication or processing without explicit consent on file.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ConsentStatus(StrEnum):
    GRANTED = "granted"
    REVOKED = "revoked"
    PENDING = "pending"


class ConsentRecord:
    def __init__(
        self,
        student_id: str,
        channel_email: ConsentStatus = ConsentStatus.GRANTED,
        channel_sms: ConsentStatus = ConsentStatus.GRANTED,
        ai_grading_consent: ConsentStatus = ConsentStatus.GRANTED,
    ) -> None:
        self.student_id = student_id
        self.channel_email = channel_email
        self.channel_sms = channel_sms
        self.ai_grading_consent = ai_grading_consent

    def can_send_email(self) -> bool:
        return self.channel_email == ConsentStatus.GRANTED

    def can_send_sms(self) -> bool:
        return self.channel_sms == ConsentStatus.GRANTED

    def can_ai_evaluate(self) -> bool:
        return self.ai_grading_consent == ConsentStatus.GRANTED


class ConsentManager:
    """In-memory consent database and policy enforcer."""

    def __init__(self) -> None:
        self._records: dict[str, ConsentRecord] = {
            "2024-CS-001": ConsentRecord("2024-CS-001"),
            "2024-CS-002": ConsentRecord("2024-CS-002"),
            "2024-CS-003": ConsentRecord(
                "2024-CS-003",
                channel_sms=ConsentStatus.REVOKED,
            ),
        }

    def get_consent(self, student_id: str) -> ConsentRecord:
        """Get or create default consent record for student."""
        if student_id not in self._records:
            self._records[student_id] = ConsentRecord(student_id)
        return self._records[student_id]

    def update_consent(
        self,
        student_id: str,
        channel_email: ConsentStatus | None = None,
        channel_sms: ConsentStatus | None = None,
        ai_grading_consent: ConsentStatus | None = None,
    ) -> ConsentRecord:
        record = self.get_consent(student_id)
        if channel_email is not None:
            record.channel_email = channel_email
        if channel_sms is not None:
            record.channel_sms = channel_sms
        if ai_grading_consent is not None:
            record.ai_grading_consent = ai_grading_consent
        return record


consent_manager = ConsentManager()
