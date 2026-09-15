from pathlib import Path

import pytest

from zerotrust_x.pipeline import run_pipeline
from zerotrust_x.recovery import RecoveryVerificationError, verify_recovery_bundle

ROOT = Path(__file__).parents[2]
DATA = ROOT / "track2_cybersecurity_dataset_files"


def test_recovery_bundle_is_copied_and_verified(tmp_path: Path):
    processed = tmp_path / "processed"
    quarantine = tmp_path / "quarantine"
    run_pipeline(DATA, processed, quarantine)
    result = verify_recovery_bundle(DATA, processed, quarantine, tmp_path / "restore")
    assert result["status"] == "verified"
    assert result["event_schema_version"] == "unified-event-v2"
    assert result["row_counts"]["events"] == 62430
    assert (tmp_path / "restore/input/track2_firewall_logs.csv").exists()


def test_recovery_rejects_existing_destination(tmp_path: Path):
    processed = tmp_path / "processed"
    quarantine = tmp_path / "quarantine"
    run_pipeline(DATA, processed, quarantine)
    destination = tmp_path / "restore"
    destination.mkdir()
    with pytest.raises(RecoveryVerificationError, match="destination already exists"):
        verify_recovery_bundle(DATA, processed, quarantine, destination)


def test_recovery_rejects_corrupted_source(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for source in DATA.iterdir():
        if source.is_file():
            (input_dir / source.name).write_bytes(source.read_bytes())
    processed = tmp_path / "processed"
    quarantine = tmp_path / "quarantine"
    run_pipeline(input_dir, processed, quarantine)
    (input_dir / "track2_firewall_logs.csv").write_bytes(b"changed")
    with pytest.raises(RecoveryVerificationError, match="source hash mismatch"):
        verify_recovery_bundle(input_dir, processed, quarantine, tmp_path / "restore")
