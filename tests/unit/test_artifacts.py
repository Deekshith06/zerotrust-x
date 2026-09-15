import json
from pathlib import Path

import polars as pl
import pytest
from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.artifacts import ArtifactContractError, validate_artifact_contract
from zerotrust_x.pipeline import run_pipeline

ROOT = Path(__file__).parents[2]
DATA = ROOT / "track2_cybersecurity_dataset_files"


def valid_output(tmp_path: Path) -> Path:
    processed = tmp_path / "processed"
    run_pipeline(DATA, processed, tmp_path / "quarantine")
    validate_artifact_contract(processed)
    return processed


def test_generated_artifact_contract_is_valid(tmp_path: Path):
    processed = valid_output(tmp_path)
    contract = validate_artifact_contract(processed)
    assert contract["manifest"]["event_schema_version"] == "unified-event-v2"
    assert contract["row_counts"]["events"] == 62430


@pytest.mark.parametrize("mutation", ["manifest", "output", "quality", "schema"])
def test_artifact_contract_rejects_tampering(tmp_path: Path, mutation: str):
    processed = valid_output(tmp_path)
    if mutation == "manifest":
        (processed / "manifest.json").write_text("{", encoding="utf-8")
    elif mutation == "output":
        (processed / "events.parquet").write_bytes(b"tampered")
    elif mutation == "quality":
        quality = json.loads((processed / "data_quality.json").read_text())
        quality["event_rows"] += 1
        (processed / "data_quality.json").write_text(json.dumps(quality), encoding="utf-8")
    else:
        frame = pl.read_parquet(processed / "events.parquet").drop("department")
        frame.write_parquet(processed / "events.parquet")
    with pytest.raises(ArtifactContractError):
        validate_artifact_contract(processed)


def test_legacy_artifact_set_is_not_ready(tmp_path: Path):
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "manifest.json").write_text(json.dumps({"manifest_schema_version": "1"}), encoding="utf-8")
    with pytest.raises(ArtifactContractError) as error:
        validate_artifact_contract(processed)
    assert error.value.code == "legacy_manifest"


@pytest.mark.parametrize(
    ("path", "token"),
    [
        ("/api/summary", "analyst-demo"),
        ("/api/v1/events", "analyst-demo"),
        ("/api/v1/alerts", "analyst-demo"),
        ("/api/v1/users", "analyst-demo"),
        ("/api/v1/summary", "analyst-demo"),
        ("/api/users", "analyst-demo"),
        ("/api/events", "analyst-demo"),
        ("/api/alerts", "analyst-demo"),
        ("/api/users/EMP10001/timeline", "analyst-demo"),
        ("/api/graph/EMP10001", "analyst-demo"),
        ("/api/investigations/EMP10001", "analyst-demo"),
        ("/api/evaluation", "analyst-demo"),
        ("/api/manifest", "analyst-demo"),
        ("/api/anomalies", "analyst-demo"),
        ("/api/data-quality", "analyst-demo"),
        ("/api/employee", "employee-demo"),
    ],
)
def test_artifact_routes_fail_closed_without_manifest(tmp_path: Path, path: str, token: str):
    processed = tmp_path / "processed"
    processed.mkdir()
    client = TestClient(create_app(processed))
    assert client.get(path, headers={"X-Demo-Token": token}).status_code == 503


def test_protected_route_authorization_precedes_contract_failure(tmp_path: Path):
    processed = tmp_path / "processed"
    processed.mkdir()
    client = TestClient(create_app(processed))
    response = client.get("/api/summary")
    assert response.status_code == 401
    assert "artifact" not in response.text.lower()
