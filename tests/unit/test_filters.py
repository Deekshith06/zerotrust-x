import json
from pathlib import Path

import polars as pl
import pytest
from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.filters import Dataset, FilterSpec
from zerotrust_x.pipeline import run_pipeline
from zerotrust_x.query import ArtifactQuery

_AUTH = {"X-Demo-Token": "analyst-demo"}


def _write_small_artifacts(directory: Path) -> None:
    directory.mkdir(parents=True)
    pl.DataFrame(
        {
            "event_id": ["evt-1", "evt-2"],
            "timestamp": ["2025-01-01T00:00:00+00:00", "2025-01-02T00:00:00+00:00"],
            "user_id": ["EMP1", "EMP2"],
            "source": ["test", "test"],
        }
    ).write_parquet(directory / "events.parquet")
    pl.DataFrame(
        {
            "detection_id": ["det-1"],
            "user_id": ["EMP1"],
            "rule_code": ["TEST"],
            "severity": ["high"],
        }
    ).write_parquet(directory / "detections.parquet")
    pl.DataFrame(
        {
            "user_id": ["EMP1", "EMP2", "EMP3"],
            "risk_score": [95, 70, 10],
            "risk_level": ["critical", "high", "low"],
        }
    ).write_parquet(directory / "user_risk.parquet")


@pytest.mark.parametrize(
    "value",
    [
        "2025-01-01T00:00:00Z",
        "2025-01-01T00:00:00.000000+00:00",
        "2025-01-01T00:00:00+01:00",
        "2025-02-29T00:00:00+00:00",
    ],
)
def test_timestamp_filters_require_strict_utc_seconds(value):
    with pytest.raises(ValueError):
        FilterSpec.from_json(
            Dataset.EVENTS,
            json.dumps([{"field": "timestamp", "op": "gte", "value": value}]),
        )


def test_filter_contract_rejects_unknown_and_unbounded_values():
    for raw in [
        json.dumps([{"field": "unknown", "op": "eq", "value": "x"}]),
        json.dumps([{"field": "severity", "op": "gte", "value": "high"}]),
        json.dumps([{"field": "user_id", "op": "in", "value": list(map(str, range(26)))}]),
    ]:
        try:
            FilterSpec.from_json(Dataset.EVENTS, raw)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid filter accepted")


@pytest.mark.parametrize("filters", ["null", "{}", '"not an array"', "[null]", '[{"field":"user_id"}]'])
def test_filtered_api_rejects_malformed_json_null_and_wrong_types(tmp_path: Path, filters: str):
    _write_small_artifacts(tmp_path / "processed")
    client = TestClient(create_app(tmp_path / "processed"))
    response = client.get("/api/v1/events", params={"filters": filters}, headers=_AUTH)
    assert response.status_code == 422


def test_missing_artifact_returns_503(tmp_path: Path):
    _write_small_artifacts(tmp_path / "processed")
    (tmp_path / "processed" / "events.parquet").unlink()
    response = TestClient(create_app(tmp_path / "processed")).get("/api/v1/events", headers=_AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Required artifact set is not ready"


def test_malformed_artifact_returns_503(tmp_path: Path):
    _write_small_artifacts(tmp_path / "processed")
    (tmp_path / "processed" / "events.parquet").write_bytes(b"not parquet")
    response = TestClient(create_app(tmp_path / "processed")).get("/api/v1/events", headers=_AUTH)
    assert response.status_code == 503
    assert response.json()["detail"] == "Required artifact set is not ready"


def test_summary_high_risk_count_intersects_supplied_risk_filter(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    client = TestClient(create_app(tmp_path / "processed"))
    response = client.get(
        "/api/v1/summary",
        params={"risk_filters": '[{"field":"user_id","op":"eq","value":"EMP10001"}]'},
        headers=_AUTH,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filtered"]["users"] == 1
    assert body["filtered"]["high_risk_users"] == 1
    assert body["high_risk_users"] == 1


def test_query_does_not_mutate_artifact_or_returned_rows(tmp_path: Path):
    _write_small_artifacts(tmp_path / "processed")
    artifact = tmp_path / "processed" / "events.parquet"
    before = artifact.read_bytes()
    query = ArtifactQuery(tmp_path / "processed")
    spec = FilterSpec.from_json(Dataset.EVENTS, limit=1)
    result = query.query(spec)
    result["items"][0]["event_id"] = "tampered"
    assert artifact.read_bytes() == before
    assert query.query(spec)["items"][0]["event_id"] == "evt-1"


def test_filtered_query_is_deterministic_and_paged(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    query = ArtifactQuery(tmp_path / "processed")
    spec = FilterSpec.from_json(Dataset.EVENTS, limit=7)
    first = query.query(spec)
    second = query.query(spec)
    assert first == second
    assert first["filtered_count"] == 62430
    assert len(first["items"]) == 7
    assert first["has_more"]


def test_filtered_api_preserves_baseline_and_requires_auth(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    client = TestClient(create_app(tmp_path / "processed"))
    assert client.get("/api/v1/events").status_code == 401
    response = client.get(
        "/api/v1/events?filters="
        + '[{"field":"user_id","op":"eq","value":"EMP10001"}]',
        headers={"X-Demo-Token": "analyst-demo"},
    )
    assert response.status_code == 200
    assert response.json()["filtered_count"] > 0
    summary = client.get("/api/v1/summary", headers={"X-Demo-Token": "analyst-demo"})
    assert summary.json()["baseline"] == {"dataset_version": "data-quality-v1", "events": 62430, "detections": 1473, "users": 3000}
