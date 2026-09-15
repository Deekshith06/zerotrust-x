"""Truthful deterministic evaluation summary for synthetic telemetry."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from zerotrust_x.artifacts import ArtifactContractError, validate_artifact_contract


def evaluation_report(processed_dir: Path) -> dict[str, Any]:
    try:
        contract = validate_artifact_contract(processed_dir)
    except ArtifactContractError as exc:
        raise FileNotFoundError("artifact contract is not ready") from exc
    quality = contract["quality"]
    return {
        "dataset": "Track 2 synthetic telemetry",
        "ground_truth": "unverified",
        "event_rows": quality["event_rows"],
        "detection_rows": quality["detection_rows"],
        "risk_user_rows": quality["risk_user_rows"],
        "quarantine_rows": quality["quarantine_rows"],
        "evaluation_mode": "deterministic acceptance checks; not accuracy measurement",
        "claims_supported": [
            "pipeline output counts",
            "artifact reproducibility",
            "reason-coded quality handling",
            "deterministic rule execution",
        ],
        "claims_not_supported": [
            "real-world precision or recall",
            "malicious intent",
            "insider-threat ground truth",
        ],
    }
