from pathlib import Path

from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.pipeline import run_pipeline


def _client(tmp_path: Path) -> TestClient:
    root = Path(__file__).parents[3]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    return TestClient(create_app(tmp_path / "processed"))


def test_sensitive_quality_route_fails_closed(tmp_path: Path):
    client = _client(tmp_path)
    assert client.get("/api/data-quality").status_code == 401
    assert client.get(
        "/api/data-quality", headers={"X-Demo-Token": "analyst-demo"}
    ).status_code == 200


def test_request_id_is_propagated_without_trusting_unbounded_input(tmp_path: Path):
    client = _client(tmp_path)
    supplied = "trace-123"
    response = client.get("/health", headers={"X-Request-ID": supplied})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == supplied


def test_unknown_graph_does_not_disclose_artifact_details(tmp_path: Path):
    client = _client(tmp_path)
    response = client.get(
        "/api/graph/does-not-exist", headers={"X-Demo-Token": "analyst-demo"}
    )
    assert response.status_code == 404
    assert "parquet" not in response.text.lower()
