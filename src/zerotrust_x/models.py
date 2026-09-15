"""Typed contracts for raw envelopes, quality findings, and unified events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RawEnvelope:
    source: str
    source_path: str
    source_row: int
    record: dict[str, Any]
    record_id: str | None = None

    @property
    def source_reference(self) -> str:
        return f"{self.source}:{self.source_row}"


@dataclass(frozen=True)
class QualityIssue:
    source: str
    source_row: int
    field: str
    reason_code: str
    raw_value: Any
    rule: str
    source_record_id: str | None = None


@dataclass
class UnifiedEvent:
    event_id: str
    source: str
    source_path: str
    source_row: int
    source_record_id: str | None
    raw_record_sha256: str
    iteration_id: str
    normalization_rule_version: str
    event_type: str
    raw_event_type: str | None = None
    timestamp: datetime | None = None
    timestamp_raw: str | None = None
    timestamp_format: str | None = None
    user_id: str | None = None
    hostname: str | None = None
    device_id: str | None = None
    session_id: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    protocol: str | None = None
    action: str | None = None
    bytes_sent: int | None = None
    bytes_received: int | None = None
    severity: str | None = None
    risk_score: float | None = None
    department: str | None = None
    status: str | None = None
    device_criticality: str | None = None
    location: str | None = None
    geo_country: str | None = None
    threat_flag: bool | None = None
    sha256: str | None = None
    quality_status: str = "clean"
    quality_reason_codes: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
