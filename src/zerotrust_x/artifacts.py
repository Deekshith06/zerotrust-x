"""Read-only validation for generated Track 2 artifact contracts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import polars as pl

EXPECTED_MANIFEST_SCHEMA = "2"
EXPECTED_EVENT_SCHEMA = "unified-event-v2"
REQUIRED_OUTPUTS = frozenset(
    {"events", "clean_events", "detections", "user_risk", "data_quality", "quarantine"}
)
REQUIRED_COLUMNS: dict[str, frozenset[str]] = {
    "events": frozenset(
        {
            "event_id", "source", "source_path", "source_row", "source_record_id",
            "raw_record_sha256", "iteration_id", "normalization_rule_version", "event_type",
            "timestamp", "user_id", "hostname", "device_id", "session_id", "source_ip",
            "destination_ip", "src_port", "dst_port", "protocol", "action", "bytes_sent",
            "bytes_received", "severity", "risk_score", "department", "status",
            "device_criticality", "location", "geo_country", "threat_flag", "sha256",
            "quality_status", "quality_reason_codes", "payload",
        }
    ),
    "clean_events": frozenset(
        {
            "event_id", "source", "source_path", "source_row", "source_record_id",
            "raw_record_sha256", "iteration_id", "normalization_rule_version", "event_type",
            "timestamp", "user_id", "hostname", "device_id", "session_id", "source_ip",
            "destination_ip", "src_port", "dst_port", "protocol", "action", "bytes_sent",
            "bytes_received", "severity", "risk_score", "department", "status",
            "device_criticality", "location", "geo_country", "threat_flag", "sha256",
            "quality_status", "quality_reason_codes", "payload",
        }
    ),
    "detections": frozenset(
        {"detection_id", "user_id", "rule_code", "severity", "event_ids", "reason"}
    ),
    "user_risk": frozenset(
        {"user_id", "risk_score", "risk_level", "reason_codes", "evidence_event_ids"}
    ),
    "quarantine": frozenset(
        {
            "source", "source_row", "source_path", "source_record_id", "raw_record_sha256",
            "iteration_id", "normalization_rule_version", "field", "reason_code",
            "classification", "raw_value", "raw_payload", "rule",
        }
    ),
}


class ArtifactContractError(RuntimeError):
    """Generated artifacts are missing, stale, malformed, or inconsistent."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fail(code: str) -> None:
    raise ArtifactContractError(code)


def _load_manifest(processed_dir: Path) -> dict[str, Any]:
    path = processed_dir / "manifest.json"
    if not path.is_file():
        _fail("manifest_missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        _fail("manifest_invalid")
    if not isinstance(value, dict):
        _fail("manifest_invalid")
    return value


def _artifact_path(processed_dir: Path, name: str) -> Path:
    if name == "quarantine":
        return processed_dir.parent / "quarantine" / "quarantine.parquet"
    suffix = ".json" if name == "data_quality" else ".parquet"
    return processed_dir / f"{name}{suffix}"


def _validate_quality(path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    try:
        quality = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        _fail("quality_invalid")
    if not isinstance(quality, dict):
        _fail("quality_invalid")
    required = {
        "event_rows", "quarantine_rows", "detection_rows", "risk_user_rows",
        "cleaning_status", "dataset_baseline_version",
    }
    if not required.issubset(quality):
        _fail("quality_schema_invalid")
    if quality["dataset_baseline_version"] != manifest.get("dataset_baseline_version"):
        _fail("quality_version_mismatch")
    return quality


def _validate_parquet(path: Path, name: str) -> int:
    try:
        frame = pl.read_parquet(path)
    except (OSError, pl.exceptions.PolarsError):
        _fail("artifact_invalid")
    if not REQUIRED_COLUMNS[name].issubset(frame.columns):
        _fail(f"{name}_schema_invalid")
    return frame.height


def validate_artifact_contract(processed_dir: Path) -> dict[str, Any]:
    """Validate a complete v2 artifact set without changing any file."""
    processed_dir = Path(processed_dir)
    manifest = _load_manifest(processed_dir)
    if manifest.get("manifest_schema_version") != EXPECTED_MANIFEST_SCHEMA:
        _fail("legacy_manifest")
    required_metadata = {
        "pipeline_version", "dataset_baseline_version", "iteration_id",
        "normalization_rule_version", "inputs", "context_inputs", "quality",
    }
    if not required_metadata.issubset(manifest):
        _fail("manifest_schema_invalid")
    if not isinstance(manifest["inputs"], dict) or not isinstance(manifest["context_inputs"], dict):
        _fail("manifest_schema_invalid")
    if not isinstance(manifest["pipeline_version"], str) or not isinstance(manifest["dataset_baseline_version"], str):
        _fail("manifest_schema_invalid")
    if not isinstance(manifest["iteration_id"], str) or not isinstance(manifest["normalization_rule_version"], str):
        _fail("manifest_schema_invalid")
    if manifest.get("event_schema_version") != EXPECTED_EVENT_SCHEMA:
        _fail("event_schema_unsupported")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != REQUIRED_OUTPUTS:
        _fail("outputs_invalid")
    for key, value in outputs.items():
        if not isinstance(value, str) or len(value) != 64:
            _fail("output_hash_invalid")
        path = _artifact_path(processed_dir, key)
        if not path.is_file():
            _fail("artifact_missing")
        try:
            if _sha256(path) != value:
                _fail("artifact_hash_mismatch")
        except OSError:
            _fail("artifact_unreadable")

    quality = _validate_quality(_artifact_path(processed_dir, "data_quality"), manifest)
    if manifest.get("quality") != quality:
        _fail("manifest_quality_mismatch")
    row_counts = {
        "events": _validate_parquet(_artifact_path(processed_dir, "events"), "events"),
        "clean_events": _validate_parquet(_artifact_path(processed_dir, "clean_events"), "clean_events"),
        "detections": _validate_parquet(_artifact_path(processed_dir, "detections"), "detections"),
        "user_risk": _validate_parquet(_artifact_path(processed_dir, "user_risk"), "user_risk"),
        "quarantine": _validate_parquet(_artifact_path(processed_dir, "quarantine"), "quarantine"),
    }
    expected_counts = {
        "events": "event_rows", "detections": "detection_rows",
        "user_risk": "risk_user_rows", "quarantine": "quarantine_rows",
    }
    for artifact, quality_key in expected_counts.items():
        if row_counts[artifact] != quality[quality_key]:
            _fail("quality_count_mismatch")
    return {"manifest": manifest, "quality": quality, "row_counts": row_counts}
