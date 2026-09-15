"""Operator-run local backup and restore verification for Track 2 artifacts."""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from zerotrust_x.artifacts import ArtifactContractError, validate_artifact_contract


class RecoveryVerificationError(RuntimeError):
    """A local backup bundle cannot be verified safely."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_recovery_bundle(
    input_dir: Path,
    processed_dir: Path,
    quarantine_dir: Path,
    destination: Path,
) -> dict[str, Any]:
    """Copy an immutable local bundle and verify it independently.

    Paths are operator-selected CLI inputs, never request data. Existing
    destinations are rejected to prevent accidental overwrite.
    """
    input_dir = Path(input_dir)
    processed_dir = Path(processed_dir)
    quarantine_dir = Path(quarantine_dir)
    destination = Path(destination)
    if destination.exists():
        raise RecoveryVerificationError("destination already exists")
    for source in (input_dir, processed_dir, quarantine_dir):
        if not source.is_dir():
            raise RecoveryVerificationError("backup source directory is missing")

    destination.mkdir(parents=True)
    try:
        shutil.copytree(input_dir, destination / "input")
        shutil.copytree(processed_dir, destination / "processed")
        shutil.copytree(quarantine_dir, destination / "quarantine")
        contract = validate_artifact_contract(destination / "processed")
        declared_inputs = contract["manifest"].get("inputs", {})
        for filename, expected_hash in declared_inputs.items():
            copied = destination / "input" / filename
            if not copied.is_file() or _sha256(copied) != expected_hash:
                raise RecoveryVerificationError("source hash mismatch")
        quarantine_path = destination / "quarantine" / "quarantine.parquet"
        if _sha256(quarantine_path) != contract["manifest"]["outputs"]["quarantine"]:
            raise RecoveryVerificationError("quarantine hash mismatch")
    except (OSError, ArtifactContractError, RecoveryVerificationError):
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return {
        "status": "verified",
        "destination": str(destination),
        "event_schema_version": contract["manifest"]["event_schema_version"],
        "row_counts": contract["row_counts"],
        "source_files": len(declared_inputs),
    }
