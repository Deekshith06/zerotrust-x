"""Tamper-evident local audit sink and external-retention contract."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4


class AuditSink(Protocol):
    def append(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


class ExternalAuditSink:
    """Contract for WORM/object-lock retention supplied by deployment infrastructure."""

    def append(self, **_: Any) -> dict[str, Any]:
        raise NotImplementedError("configure an external immutable audit sink")


class LocalAuditSink:
    """Hash-chained JSONL sink; tamper-evident but not filesystem immutable."""

    def __init__(self, path: Path):
        self.path = path

    def append(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        details: dict[str, Any] | None = None,
        *,
        request_id: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        previous_hash = "GENESIS"
        sequence = 1
        if self.path.exists():
            existing = self.path.read_text(encoding="utf-8").splitlines()
            if existing:
                prior = json.loads(existing[-1])
                previous_hash = str(prior["current_hash"])
                sequence = int(prior["sequence"]) + 1
        entry: dict[str, Any] = {
            "event_id": f"audit-{uuid4().hex}",
            "sequence": sequence,
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "tenant_id": tenant_id,
            "request_id": request_id,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "details": details or {},
            "previous_hash": previous_hash,
        }
        entry["current_hash"] = _entry_hash(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry


def _entry_hash(entry: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in entry.items() if key != "current_hash"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def verify_audit_chain(path: Path) -> tuple[bool, str | None]:
    if not path.exists():
        return True, None
    previous = "GENESIS"
    expected_sequence = 1
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False, f"line {line_number}: invalid JSON"
        if entry.get("sequence") != expected_sequence:
            return False, f"line {line_number}: sequence mismatch"
        if entry.get("previous_hash") != previous:
            return False, f"line {line_number}: previous hash mismatch"
        if entry.get("current_hash") != _entry_hash(entry):
            return False, f"line {line_number}: current hash mismatch"
        previous = entry["current_hash"]
        expected_sequence += 1
    return True, None


def append_audit(
    path: Path,
    actor: str,
    action: str,
    resource: str,
    outcome: str,
    details: dict[str, Any] | None = None,
    *,
    request_id: str | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    return LocalAuditSink(path).append(
        actor, action, resource, outcome, details,
        request_id=request_id, tenant_id=tenant_id,
    )
