from pathlib import Path

from zerotrust_x.pipeline import run_pipeline

ROOT = Path(__file__).parents[2]
DATA = ROOT / "track2_cybersecurity_dataset_files"


def test_real_sources_produce_traceable_artifacts(tmp_path: Path):
    result = run_pipeline(DATA, tmp_path / "processed", tmp_path / "quarantine")
    assert result["cleaning_status"] == "CLEAN_WITH_DOCUMENTED_EXCEPTIONS"
    assert result["dataset_baseline_version"] == "data-quality-v1"
    assert result["event_rows"] == 62430
    assert result["quarantine_rows"] > 0
    assert result["quarantine_rows"] == 36220
    assert result["quarantine_affected_rows"] == 29536
    assert result["duplicate_rows"] == 1430
    assert result["reason_counts"]["RESOLUTION_BEFORE_DETECTION"] == 268
    assert result["classification_counts"] == {
        "DUPLICATE_FINDING": 1430,
        "VALID_AND_UNRECOVERABLE": 34790,
    }
    assert result["source_record_counts"] == {
        "endpoint": 8240,
        "firewall": 30600,
        "iam": 20500,
        "identity": 3090,
    }
    assert round(result["quarantine_finding_per_affected_row"], 4) == 1.2263
    assert (tmp_path / "processed" / "events.parquet").exists()
    assert (tmp_path / "quarantine" / "quarantine.parquet").exists()
    assert (tmp_path / "processed" / "data_quality.json").exists()
    import polars as pl

    events = pl.read_parquet(tmp_path / "processed" / "events.parquet")
    assert {"department", "src_port", "dst_port", "bytes_sent", "bytes_received", "status", "sha256", "threat_flag"}.issubset(events.columns)
    manifest = __import__("json").loads((tmp_path / "processed" / "manifest.json").read_text())
    assert manifest["event_schema_version"] == "unified-event-v2"
    assert set(manifest["inputs"]) == {
        "track2_firewall_logs.csv",
        "track2_iam_audit_trail.json",
        "track2_endpoint_alerts.xlsx",
        "track2_identity_asset_master.csv",
    }
    assert set(manifest["context_inputs"]) == {"track2_dataset_notes.txt"}
    assert set(manifest["outputs"]) == {
        "events",
        "clean_events",
        "detections",
        "user_risk",
        "data_quality",
        "quarantine",
    }
    assert manifest["manifest_schema_version"] == "2"


def test_manifest_ignores_undeclared_and_stale_files(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for source in (DATA).iterdir():
        if source.is_file():
            (input_dir / source.name).write_bytes(source.read_bytes())
    (input_dir / ".DS_Store").write_bytes(b"transient")
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    (output_dir / "stale.parquet").write_bytes(b"stale")
    quarantine_dir = tmp_path / "quarantine"

    run_pipeline(input_dir, output_dir, quarantine_dir)

    import json

    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert ".DS_Store" not in manifest["inputs"]
    assert "stale.parquet" not in manifest["outputs"]
    assert "quarantine" in manifest["outputs"]


def test_pipeline_records_iteration_and_finding_provenance(tmp_path: Path):
    run_pipeline(
        DATA,
        tmp_path / "processed",
        tmp_path / "quarantine",
        iteration_id="audit-A",
    )

    import polars as pl

    events = pl.read_parquet(tmp_path / "processed" / "events.parquet")
    findings = pl.read_parquet(tmp_path / "quarantine" / "quarantine.parquet")
    for frame in (events, findings):
        assert frame.get_column("iteration_id").unique().to_list() == ["audit-A"]
        assert frame.get_column("normalization_rule_version").null_count() == 0
        assert frame.get_column("source_path").null_count() == 0
        assert frame.get_column("raw_record_sha256").null_count() == 0
    assert findings.get_column("classification").null_count() == 0
