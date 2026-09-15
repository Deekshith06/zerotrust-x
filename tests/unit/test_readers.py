from pathlib import Path

from zerotrust_x.adapters.readers import read_json, read_xlsx
from zerotrust_x.pipeline import normalize_envelope

ROOT = Path(__file__).parents[2]
DATA = ROOT / "track2_cybersecurity_dataset_files"


def test_json_reader_uses_tabular_logical_row_convention(tmp_path: Path):
    path = tmp_path / "records.json"
    path.write_text('[{"event_id":"evt-1"}]', encoding="utf-8")

    envelope = next(read_json(path, "iam", "event_id"))

    assert envelope.source_row == 2
    assert envelope.source_reference == "iam:2"


def test_endpoint_reader_preserves_duplicate_timestamp_columns():
    envelopes = list(
        read_xlsx(
            DATA / "track2_endpoint_alerts.xlsx",
            "endpoint",
            "alert_id",
            "endpoint_alerts",
        )
    )

    assert len(envelopes) == 8240
    assert "detected_timestamp" in envelopes[0].record
    assert "resolved_timestamp" in envelopes[0].record
    assert envelopes[0].record["detected_timestamp"] != envelopes[0].record["resolved_timestamp"]


def test_endpoint_resolution_findings_match_frozen_contract():
    findings = 0
    for envelope in read_xlsx(
        DATA / "track2_endpoint_alerts.xlsx",
        "endpoint",
        "alert_id",
        "endpoint_alerts",
    ):
        _, issues = normalize_envelope(envelope)
        findings += sum(
            issue.reason_code == "RESOLUTION_BEFORE_DETECTION" for issue in issues
        )

    assert findings == 268
