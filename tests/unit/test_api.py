from pathlib import Path

from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.pipeline import run_pipeline


def test_api_exposes_real_artifacts(tmp_path: Path):
    run_pipeline(
        Path(__file__).parents[2] / "track2_cybersecurity_dataset_files",
        tmp_path / "processed",
        tmp_path / "quarantine",
    )
    client = TestClient(create_app(tmp_path / "processed"))
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    summary = client.get("/api/summary")
    assert summary.status_code == 401
    analyst = {"X-Demo-Token": "analyst-demo"}
    summary = client.get("/api/summary", headers=analyst)
    assert summary.status_code == 200
    assert summary.json()["events"] == 62430
    assert client.get("/api/users").status_code == 401
    assert client.get("/api/users", headers=analyst).status_code == 200
    assert client.get("/api/graph/NOT_A_USER", headers=analyst).status_code == 404
    assert client.get("/api/anomalies").status_code == 401
    assert client.get("/api/anomalies", headers={"X-Demo-Token": "analyst-demo"}).status_code == 200
    assert client.get("/api/employee", headers={"X-Demo-Token": "employee-demo"}).status_code == 200
