from pathlib import Path

from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.config import Settings
from zerotrust_x.evaluation import evaluation_report
from zerotrust_x.pipeline import run_pipeline


def test_production_settings_fail_closed_without_oidc():
    settings = Settings(environment="production")
    assert "OIDC_ISSUER is required outside demo mode" in settings.validate()
    assert "OIDC_AUDIENCE is required outside demo mode" in settings.validate()


def test_evaluation_report_is_truthful(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    report = evaluation_report(tmp_path / "processed")
    assert report["ground_truth"] == "unverified"
    assert "malicious intent" in report["claims_not_supported"]


def test_manifest_and_evaluation_require_analyst_access(tmp_path: Path):
    root = Path(__file__).parents[2]
    run_pipeline(root / "track2_cybersecurity_dataset_files", tmp_path / "processed", tmp_path / "quarantine")
    client = TestClient(create_app(tmp_path / "processed"))
    assert client.get("/api/manifest").status_code == 401
    assert client.get("/api/evaluation").status_code == 401
    assert client.get("/api/evaluation", headers={"X-Demo-Token": "analyst-demo"}).status_code == 200
