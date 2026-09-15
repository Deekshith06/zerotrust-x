"""Small durable tenant-scoped store for security-boundary tests and local deployments."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zerotrust_x.tenant import TenantContext, require_same_tenant


@dataclass(frozen=True)
class TenantRecord:
    tenant_id: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any]


class TenantStore:
    """SQLite-backed repository whose public methods require request context."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_records (
                    tenant_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, resource_type, resource_id)
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def put(self, context: TenantContext, record: TenantRecord) -> None:
        require_same_tenant(context, record.tenant_id)
        import json

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tenant_records(tenant_id, resource_type, resource_id, payload)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(tenant_id, resource_type, resource_id)
                DO UPDATE SET payload = excluded.payload
                """,
                (record.tenant_id, record.resource_type, record.resource_id,
                 json.dumps(record.payload, sort_keys=True)),
            )

    def get(self, context: TenantContext, resource_type: str, resource_id: str) -> TenantRecord | None:
        import json

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT tenant_id, resource_type, resource_id, payload
                FROM tenant_records
                WHERE tenant_id = ? AND resource_type = ? AND resource_id = ?
                """,
                (context.tenant_id, resource_type, resource_id),
            ).fetchone()
        if row is None:
            return None
        return TenantRecord(
            tenant_id=row["tenant_id"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            payload=json.loads(row["payload"]),
        )

    def list(self, context: TenantContext, resource_type: str) -> list[TenantRecord]:
        import json

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT tenant_id, resource_type, resource_id, payload
                FROM tenant_records
                WHERE tenant_id = ? AND resource_type = ?
                ORDER BY resource_id
                """,
                (context.tenant_id, resource_type),
            ).fetchall()
        return [
            TenantRecord(
                tenant_id=row["tenant_id"],
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                payload=json.loads(row["payload"]),
            )
            for row in rows
        ]
