"""Ingestion Agent: upload handler, file validation, and storage (EPIC-15-T01).

Validates answer sheets (magic bytes, MIME type, file size limits),
stores securely with content-addressed SHA256 hashes, and registers ingestion metadata.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


ALLOWED_MIME_TYPES = {
    "application/pdf": b"%PDF-",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


@dataclass
class IngestionResult:
    file_id: str
    original_filename: str
    mime_type: str
    size_bytes: int
    sha256_hash: str
    storage_path: str
    status: str  # "accepted", "rejected"
    error_reason: str | None = None


class IngestionAgent:
    """Handles upload validation, anti-tamper hashing, and storage of exam answer sheets."""

    def __init__(self, storage_dir: str | Path = "./storage/answer_sheets") -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, content: bytes, filename: str) -> tuple[bool, str | None, str | None]:
        """Validate file size and magic bytes against allowed formats."""
        if len(content) == 0:
            return False, None, "File is empty"

        if len(content) > MAX_FILE_SIZE_BYTES:
            return False, None, f"File exceeds maximum size limit of {MAX_FILE_SIZE_BYTES} bytes"

        # Check magic bytes
        detected_mime = None
        for mime, magic in ALLOWED_MIME_TYPES.items():
            if content.startswith(magic):
                detected_mime = mime
                break

        if not detected_mime:
            return False, None, "Unsupported file format. Allowed formats: PDF, PNG, JPEG"

        return True, detected_mime, None

    def ingest_answer_sheet(self, file_bytes: bytes, filename: str) -> IngestionResult:
        """Process incoming answer sheet, validate, hash, and persist to storage."""
        is_valid, detected_mime, error_msg = self.validate_file(file_bytes, filename)
        sha256 = hashlib.sha256(file_bytes).hexdigest()

        if not is_valid:
            return IngestionResult(
                file_id=f"reject_{sha256[:12]}",
                original_filename=filename,
                mime_type=detected_mime or "application/octet-stream",
                size_bytes=len(file_bytes),
                sha256_hash=sha256,
                storage_path="",
                status="rejected",
                error_reason=error_msg,
            )

        file_ext = Path(filename).suffix or ".bin"
        file_id = f"ans_{sha256[:16]}"
        target_path = self.storage_dir / f"{file_id}{file_ext}"

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return IngestionResult(
            file_id=file_id,
            original_filename=filename,
            mime_type=detected_mime,
            size_bytes=len(file_bytes),
            sha256_hash=sha256,
            storage_path=str(target_path),
            status="accepted",
            error_reason=None,
        )
