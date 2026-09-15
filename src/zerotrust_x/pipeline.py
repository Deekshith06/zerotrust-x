"""P0 ingestion, normalization, and artifact pipeline."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from zerotrust_x.adapters.readers import read_csv, read_json, read_xlsx
from zerotrust_x.models import QualityIssue, RawEnvelope, UnifiedEvent
from zerotrust_x.normalize import (
    normalize_action,
    normalize_bool,
    normalize_department,
    normalize_device_criticality,
    normalize_event_type,
    normalize_geo_country,
    normalize_hostname,
    normalize_location,
    normalize_protocol,
    normalize_severity,
    normalize_status,
    normalize_user_id,
    parse_bytes,
    parse_ip,
    parse_port,
    parse_risk,
    parse_sha256,
    parse_timestamp,
)
from zerotrust_x.provenance import canonical_json, record_hash

SOURCE_FILES = {
    "firewall": ("track2_firewall_logs.csv", "csv"),
    "iam": ("track2_iam_audit_trail.json", "json"),
    "endpoint": ("track2_endpoint_alerts.xlsx", "xlsx"),
    "identity": ("track2_identity_asset_master.csv", "csv"),
}
PIPELINE_VERSION = "0.1.0"
MANIFEST_SCHEMA_VERSION = "2"
DATASET_BASELINE_VERSION = "data-quality-v1"
NORMALIZATION_RULE_VERSION = "normalize-2026-09-14-v2"
EVENT_SCHEMA_VERSION = "unified-event-v2"
DEFAULT_ITERATION_ID = "unattributed-run"


def iter_source_records(input_dir: Path):
    yield from read_csv(input_dir / SOURCE_FILES["firewall"][0], "firewall", "log_id")
    yield from read_json(input_dir / SOURCE_FILES["iam"][0], "iam", "event_id")
    yield from read_xlsx(input_dir / SOURCE_FILES["endpoint"][0], "endpoint", "alert_id", "endpoint_alerts")
    yield from read_csv(input_dir / SOURCE_FILES["identity"][0], "identity", "user_id")


def _issue(envelope: RawEnvelope, field: str, code: str, value: Any, rule: str) -> QualityIssue:
    return QualityIssue(envelope.source, envelope.source_row, field, code, value, rule, envelope.record_id)


def _finding_classification(reason_code: str) -> str:
    if reason_code == "DUPLICATE_RECORD":
        return "DUPLICATE_FINDING"
    if reason_code in {"BYTES_INVALID", "BYTES_OUT_OF_RANGE", "HASH_FORMAT_INVALID", "IP_ADDRESS_INVALID",
                       "PORT_INVALID", "PORT_OUT_OF_RANGE", "RESOLUTION_BEFORE_DETECTION",
                       "RISK_NON_NUMERIC", "RISK_OUT_OF_RANGE"}:
        return "VALID_AND_UNRECOVERABLE"
    return "UNKNOWN"


def normalize_envelope(
    envelope: RawEnvelope,
    *,
    iteration_id: str = DEFAULT_ITERATION_ID,
) -> tuple[UnifiedEvent, list[QualityIssue]]:
    row = envelope.record
    issues: list[QualityIssue] = []
    raw_hash = record_hash(row)
    event_id = envelope.record_id or f"{envelope.source}-{envelope.source_row}"
    timestamp_key = "timestamp" if envelope.source != "endpoint" else "detected_timestamp"
    timestamp, timestamp_format, timestamp_error = parse_timestamp(row.get(timestamp_key))
    if timestamp_error:
        issues.append(_issue(envelope, timestamp_key, timestamp_error, row.get(timestamp_key), "explicit timestamp formats"))

    user_id = normalize_user_id(row.get("user_id"))
    if row.get("user_id") not in (None, "") and user_id is None:
        issues.append(_issue(envelope, "user_id", "USER_ID_UNRECOGNIZED", row.get("user_id"), "EMP prefix plus digits"))
    hostname = normalize_hostname(row.get("hostname"))
    source_ip, ip_status = parse_ip(row.get("source_ip", row.get("src_ip")))
    if ip_status in {"invalid", "out_of_range"}:
        issues.append(_issue(envelope, "source_ip", "IP_ADDRESS_INVALID", row.get("source_ip", row.get("src_ip")), "strict IP parser"))
    risk, risk_status = parse_risk(row.get("risk_score"))
    if risk_status in {"non_numeric", "out_of_range"}:
        issues.append(_issue(envelope, "risk_score", f"RISK_{risk_status.upper()}", row.get("risk_score"), "numeric risk in range 0..100"))

    src_port, src_port_status = parse_port(row.get("src_port"))
    dst_port, dst_port_status = parse_port(row.get("dst_port"))
    for field, status in (("src_port", src_port_status), ("dst_port", dst_port_status)):
        if status in {"invalid", "out_of_range"}:
            issues.append(_issue(envelope, field, f"PORT_{status.upper()}", row.get(field), "integer port in range 0..65535"))
    bytes_sent, bytes_sent_status = parse_bytes(row.get("bytes_sent"))
    bytes_received, bytes_received_status = parse_bytes(row.get("bytes_received"))
    for field, status in (("bytes_sent", bytes_sent_status), ("bytes_received", bytes_received_status)):
        if status in {"invalid", "out_of_range"}:
            issues.append(_issue(envelope, field, f"BYTES_{status.upper()}", row.get(field), "non-negative byte count"))
    sha256, hash_status = parse_sha256(row.get("sha256"))
    if envelope.source == "endpoint":
        if hash_status == "invalid":
            issues.append(_issue(envelope, "sha256", "HASH_FORMAT_INVALID", row.get("sha256"), "64 hexadecimal characters"))
        detected, _, _ = parse_timestamp(row.get("detected_timestamp"))
        resolved, _, _ = parse_timestamp(row.get("resolved_timestamp"))
        if detected and resolved and resolved < detected:
            issues.append(_issue(envelope, "resolved_timestamp", "RESOLUTION_BEFORE_DETECTION", row.get("resolved_timestamp"), "resolved timestamp must not precede detection"))

    event_type = normalize_event_type(row.get("event_type", row.get("alert_name", "other")))
    if envelope.source == "firewall":
        event_type = "network_activity"
    elif envelope.source == "endpoint":
        event_type = "endpoint_alert"
    elif envelope.source == "identity":
        event_type = "identity_record"

    quality_codes = sorted({issue.reason_code for issue in issues})
    return UnifiedEvent(
        event_id=str(event_id), source=envelope.source, source_path=envelope.source_path,
        source_row=envelope.source_row,
        source_record_id=str(envelope.record_id) if envelope.record_id is not None else None,
        raw_record_sha256=raw_hash, iteration_id=iteration_id,
        normalization_rule_version=NORMALIZATION_RULE_VERSION,
        event_type=event_type,
        raw_event_type=row.get("event_type"), timestamp=timestamp,
        timestamp_raw=str(row.get(timestamp_key)) if row.get(timestamp_key) is not None else None,
        timestamp_format=timestamp_format, user_id=user_id, hostname=hostname,
        device_id=row.get("device_id"), session_id=row.get("session_id"), source_ip=source_ip,
        destination_ip=parse_ip(row.get("destination_ip", row.get("dst_ip")))[0],
        src_port=src_port, dst_port=dst_port,
        protocol=normalize_protocol(row.get("protocol")), action=normalize_action(row.get("action")),
        bytes_sent=bytes_sent, bytes_received=bytes_received,
        severity=normalize_severity(row.get("severity")), risk_score=risk,
        department=normalize_department(row.get("department")),
        status=normalize_status(row.get("status")),
        device_criticality=normalize_device_criticality(row.get("device_criticality")),
        location=normalize_location(row.get("location")),
        geo_country=normalize_geo_country(row.get("geo_country")),
        threat_flag=normalize_bool(row.get("threat_flag")), sha256=sha256,
        quality_status="normalized" if quality_codes else "clean",
        quality_reason_codes=quality_codes, payload={"raw": row},
    ), issues



def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    quarantine_dir: Path,
    *,
    iteration_id: str = DEFAULT_ITERATION_ID,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    seen_ids: set[tuple[str, str]] = set()
    reason_counts: Counter[str] = Counter()
    received_counts: Counter[str] = Counter()
    affected_rows: set[tuple[str, int]] = set()
    duplicate_rows: set[tuple[str, int]] = set()
    for envelope in iter_source_records(input_dir):
        received_counts[envelope.source] += 1
        event, issues = normalize_envelope(envelope, iteration_id=iteration_id)
        identity = (event.source, event.event_id)
        if identity in seen_ids:
            issue = _issue(envelope, "record", "DUPLICATE_RECORD", envelope.record_id, "unique source identifier")
            issues.append(issue)
            event.quality_reason_codes.append(issue.reason_code)
            event.quality_status = "normalized"
        seen_ids.add(identity)
        if issues:
            affected_rows.add((envelope.source, envelope.source_row))
        for issue in issues:
            reason_counts[issue.reason_code] += 1
            if issue.reason_code == "DUPLICATE_RECORD":
                duplicate_rows.add((envelope.source, envelope.source_row))
            quarantine.append({
                "source": issue.source, "source_row": issue.source_row,
                "source_path": envelope.source_path,
                "source_record_id": issue.source_record_id,
                "raw_record_sha256": event.raw_record_sha256,
                "iteration_id": iteration_id,
                "normalization_rule_version": NORMALIZATION_RULE_VERSION,
                "field": issue.field,
                "reason_code": issue.reason_code,
                "classification": _finding_classification(issue.reason_code),
                "raw_value": str(issue.raw_value),
                "raw_payload": canonical_json(envelope.record),
                "rule": issue.rule,
            })
        payload = event.__dict__.copy()
        payload["timestamp"] = event.timestamp.isoformat() if event.timestamp else None
        payload["quality_reason_codes"] = sorted(set(event.quality_reason_codes))
        payload["payload"] = json.dumps(event.payload, default=str, sort_keys=True)
        events.append(payload)

    clean_events = [item for item in events if item.get("quality_status") == "clean"]
    _write_parquet(events, output_dir / "events.parquet")
    _write_parquet(clean_events, output_dir / "clean_events.parquet")
    _write_parquet(quarantine, quarantine_dir / "quarantine.parquet")
    from zerotrust_x.detection import detect, score_users

    detections = detect(events)
    risks = score_users(events, detections)
    _write_parquet([item.__dict__ for item in detections], output_dir / "detections.parquet")
    _write_parquet([item.__dict__ for item in risks], output_dir / "user_risk.parquet")
    source_totals = dict(sorted(received_counts.items()))
    classification_counts = Counter(
        str(item["classification"]) for item in quarantine
    )
    affected_by_source = {
        source: sum(1 for item in affected_rows if item[0] == source)
        for source in sorted(received_counts)
    }
    cleaning_status = "CLEAN_100_PERCENT" if not quarantine else "CLEAN_WITH_DOCUMENTED_EXCEPTIONS"
    quality = {
        "cleaning_status": cleaning_status,
        "dataset_baseline_version": DATASET_BASELINE_VERSION,
        "event_rows": len(events),
        "quarantine_rows": len(quarantine),
        "quarantine_affected_rows": len(affected_rows),
        "duplicate_rows": len(duplicate_rows),
        "detection_rows": len(detections),
        "risk_user_rows": len(risks),
        "reason_counts": dict(sorted(reason_counts.items())),
        "classification_counts": dict(sorted(classification_counts.items())),
        "source_record_counts": source_totals,
        "source_affected_rows": affected_by_source,
        "quarantine_finding_per_affected_row": round(
            len(quarantine) / len(affected_rows), 6
        ) if affected_rows else 0.0,
    }
    quality_json = json.dumps(quality, indent=2, sort_keys=True)
    (output_dir / "data_quality.json").write_text(quality_json, encoding="utf-8")
    declared_inputs = {
        filename: _sha256(input_dir / filename)
        for filename, _ in sorted(SOURCE_FILES.values())
        if (input_dir / filename).is_file()
    }
    context_filename = "track2_dataset_notes.txt"
    context_inputs = (
        {context_filename: _sha256(input_dir / context_filename)}
        if (input_dir / context_filename).is_file()
        else {}
    )
    missing_inputs = [
        filename for filename, _ in SOURCE_FILES.values()
        if not (input_dir / filename).is_file()
    ]
    if missing_inputs:
        raise FileNotFoundError(f"Missing declared source files: {missing_inputs}")
    artifact_paths = {
        "events": output_dir / "events.parquet",
        "clean_events": output_dir / "clean_events.parquet",
        "detections": output_dir / "detections.parquet",
        "user_risk": output_dir / "user_risk.parquet",
        "data_quality": output_dir / "data_quality.json",
        "quarantine": quarantine_dir / "quarantine.parquet",
    }
    manifest = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "dataset_baseline_version": DATASET_BASELINE_VERSION,
        "iteration_id": iteration_id,
        "normalization_rule_version": NORMALIZATION_RULE_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "inputs": declared_inputs,
        "context_inputs": context_inputs,
        "outputs": {name: _sha256(path) for name, path in artifact_paths.items()},
        "quality": quality,
        "baseline": {
            "dataset_version": DATASET_BASELINE_VERSION,
            "pipeline_status": quality["cleaning_status"],
            "source_hashes": declared_inputs,
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return quality


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    import polars as pl

    if not rows:
        pl.DataFrame({"_empty": []}).write_parquet(path)
        return
    pl.DataFrame(rows, infer_schema_length=None, strict=False).write_parquet(path)
