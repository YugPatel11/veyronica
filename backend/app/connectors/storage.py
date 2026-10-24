"""Storage Connector Adapter (MinIO/S3). EPIC-05-T12."""
from __future__ import annotations
import hashlib, io
from typing import Any
import httpx, structlog
from app.connectors import BaseConnector, ConnectorResult, ConnectorStatus

logger = structlog.get_logger()

class StorageConnector(BaseConnector):
    """MinIO/S3-compatible object storage connector."""

    async def execute(self, operation: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False, idempotency_key: str | None = None) -> ConnectorResult:
        payload = payload or {}
        if operation == "upload":
            bucket = payload.get("bucket", "nexus")
            key = payload.get("key", "")
            content = payload.get("content", b"")
            if dry_run:
                return ConnectorResult(success=True, data={"bucket": bucket, "key": key, "size": len(content)}, is_dry_run=True)
            try:
                url = f"{self.base_url}/{bucket}/{key}"
                access_key = self.auth_config.get("access_key", "minioadmin")
                secret_key = self.auth_config.get("secret_key", "minioadmin")
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.put(url, content=content if isinstance(content, bytes) else content.encode(), auth=(access_key, secret_key))
                return ConnectorResult(success=resp.status_code in (200, 201), data={"url": url}, status_code=resp.status_code)
            except Exception as e:
                return ConnectorResult(success=False, error=str(e))

        if operation == "download":
            bucket = payload.get("bucket", "nexus")
            key = payload.get("key", "")
            try:
                url = f"{self.base_url}/{bucket}/{key}"
                access_key = self.auth_config.get("access_key", "minioadmin")
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(url, auth=(access_key, self.auth_config.get("secret_key", "minioadmin")))
                return ConnectorResult(success=resp.status_code == 200, data={"content_length": len(resp.content)}, status_code=resp.status_code)
            except Exception as e:
                return ConnectorResult(success=False, error=str(e))

        if operation == "delete":
            bucket = payload.get("bucket", "nexus")
            key = payload.get("key", "")
            if dry_run:
                return ConnectorResult(success=True, data={"action": "delete", "key": key}, is_dry_run=True)
            try:
                url = f"{self.base_url}/{bucket}/{key}"
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.delete(url, auth=(self.auth_config.get("access_key", "minioadmin"), self.auth_config.get("secret_key", "minioadmin")))
                return ConnectorResult(success=resp.status_code in (200, 204), status_code=resp.status_code)
            except Exception as e:
                return ConnectorResult(success=False, error=str(e))

        return ConnectorResult(success=False, error=f"Unknown storage operation: {operation}")

    async def health_check(self) -> ConnectorStatus:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/minio/health/live")
                return ConnectorStatus.HEALTHY if resp.status_code == 200 else ConnectorStatus.DEGRADED
        except Exception:
            return ConnectorStatus.DOWN
