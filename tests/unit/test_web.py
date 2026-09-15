from pathlib import Path

from fastapi.testclient import TestClient

from zerotrust_x.pipeline import run_pipeline
from zerotrust_x.web import create_web_app


def test_dashboard_contains_industrial_shell_and_graph_surface(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    response = TestClient(create_web_app(tmp_path / "processed")).get("/")
    assert response.status_code == 200
    body = response.text
    assert "Detection operations" in body
    assert "Entity graph" in body
    assert "graph-svg" in body
    assert "Operational overview" in body
    assert "Local / unverified" in body
    assert "Scenario laboratory" not in body
    assert "Derived from indexed events only" in body
    assert "QUALITY WARNINGS" in body
    assert 'id="filter-event-severity"' in body
    assert 'id="filter-detection-severity"' not in body
    assert "renderEventSignals" in body
    assert "api('/api/v1/events?" in body
    assert "All event severities" in body
    assert "All detection severities" not in body
    assert "filter-detection-severity" not in body
    assert "Know what changed" not in body
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in response.headers["content-security-policy"]
