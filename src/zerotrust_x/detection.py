"""Deterministic detection and explainable risk scoring."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Detection:
    detection_id: str
    user_id: str
    rule_code: str
    severity: str
    event_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class UserRisk:
    user_id: str
    risk_score: int
    risk_level: str
    reason_codes: tuple[str, ...]
    evidence_event_ids: tuple[str, ...]


def _timestamp(row: dict[str, Any]) -> datetime | None:
    value = row.get("timestamp")
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def detect(events: Iterable[dict[str, Any]], failed_threshold: int = 3) -> list[Detection]:
    by_user: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        user_id = event.get("user_id")
        if user_id:
            by_user[str(user_id)].append(event)
    findings: list[Detection] = []
    for user_id, rows in by_user.items():
        failed = [row for row in rows if row.get("event_type") in {"login_failed", "mfa_failed"}]
        if len(failed) >= failed_threshold:
            findings.append(Detection(
                f"det-failed-{user_id}", user_id, "MULTIPLE_FAILED_LOGINS", "high",
                tuple(str(row["event_id"]) for row in failed),
                f"{len(failed)} authentication failures were observed for this identity.",
            ))
        mfa = [row for row in rows if row.get("event_type") == "mfa_failed"]
        if mfa:
            findings.append(Detection(
                f"det-mfa-{user_id}", user_id, "MFA_FAILURE", "high",
                tuple(str(row["event_id"]) for row in mfa),
                "One or more MFA failures were observed for this identity.",
            ))
    return findings


def score_users(events: Iterable[dict[str, Any]], detections: Iterable[Detection]) -> list[UserRisk]:
    rows_by_user: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        if row.get("user_id"):
            rows_by_user[str(row["user_id"])].append(row)
    detections_by_user: dict[str, list[Detection]] = defaultdict(list)
    for detection in detections:
        detections_by_user[detection.user_id].append(detection)
    results: list[UserRisk] = []
    for user_id, rows in rows_by_user.items():
        reasons: list[str] = []
        evidence: list[str] = []
        failed = [row for row in rows if row.get("event_type") in {"login_failed", "mfa_failed"}]
        endpoint = [row for row in rows if row.get("event_type") == "endpoint_alert"]
        denied = [row for row in rows if row.get("action") == "deny"]
        score = min(100, len(failed) * 8 + len(endpoint) * 12 + len(denied) * 3)
        for detection in detections_by_user.get(user_id, []):
            reasons.append(detection.rule_code)
            evidence.extend(detection.event_ids)
        if endpoint:
            reasons.append("ENDPOINT_ALERT")
            evidence.extend(str(row["event_id"]) for row in endpoint)
        if denied:
            reasons.append("FIREWALL_DENY")
            evidence.extend(str(row["event_id"]) for row in denied)
        if score >= 80:
            level = "critical"
        elif score >= 60:
            level = "high"
        elif score >= 30:
            level = "medium"
        else:
            level = "low"
        results.append(UserRisk(user_id, score, level, tuple(sorted(set(reasons))), tuple(dict.fromkeys(evidence))))
    return sorted(results, key=lambda result: (-result.risk_score, result.user_id))
