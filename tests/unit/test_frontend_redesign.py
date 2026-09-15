from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zerotrust_x.geoip import OfflineGeoIPProvider, get_geoip_provider
from zerotrust_x.pipeline import run_pipeline
from zerotrust_x.scenarios import list_scenarios
from zerotrust_x.web import create_web_app

_AUTH_ANALYST = {"X-Demo-Token": "analyst-demo"}


@pytest.fixture(scope="module")
def processed_client(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("redesign_test")
    root = Path(__file__).parents[2]
    run_pipeline(
        root / "track2_cybersecurity_dataset_files",
        tmp_path / "processed",
        tmp_path / "quarantine",
    )
    return TestClient(create_web_app(tmp_path / "processed"))


def test_geoip_provider_strict_zero_guess_policy():
    provider = get_geoip_provider()
    assert isinstance(provider, OfflineGeoIPProvider)
    assert not provider.is_available

    # With explicit country provided from telemetry
    res_explicit = provider.resolve("203.0.113.45", explicit_country="IN")
    assert res_explicit.status == "resolved"
    assert res_explicit.country_code == "IN"
    assert res_explicit.country == "India"
    assert res_explicit.confidence == 1.0
    assert not res_explicit.provenance["inference_used"]

    # Without explicit country: returns unavailable / unresolved, NEVER guesses
    res_unknown = provider.resolve("198.51.100.22", explicit_country=None)
    assert res_unknown.status == "unavailable"
    assert res_unknown.country == "UNKNOWN / UNRESOLVED"
    assert res_unknown.country_code is None
    assert "Geo enrichment unavailable" in res_unknown.provenance["label"]
    assert not res_unknown.provenance["inference_used"]


def test_country_detail_drilldown_endpoint(processed_client):
    # Test IN (India) drill-down
    res_in = processed_client.get("/api/v1/global/country/IN", headers=_AUTH_ANALYST)
    assert res_in.status_code == 200
    data_in = res_in.json()
    assert data_in["country_code"] == "IN"
    assert data_in["country_name"] == "India"
    assert data_in["event_count"] > 0
    assert "explicit telemetry field" in data_in["provenance"]
    assert len(data_in["top_ips"]) > 0
    assert isinstance(data_in["correlated_users"], list)

    # Test UNRESOLVED drill-down
    res_unres = processed_client.get("/api/v1/global/country/UNRESOLVED", headers=_AUTH_ANALYST)
    assert res_unres.status_code == 200
    data_unres = res_unres.json()
    assert data_unres["country_code"] == "UNRESOLVED"
    assert data_unres["event_count"] > 0

    # Test non-existent country returns 404
    res_none = processed_client.get("/api/v1/global/country/ZZ_FAKE", headers=_AUTH_ANALYST)
    assert res_none.status_code == 404


def test_geoip_resolve_endpoint(processed_client):
    # Unauthenticated returns 401
    assert processed_client.get("/api/v1/geoip/resolve?ip=10.0.0.1").status_code == 401

    # Authenticated
    res = processed_client.get("/api/v1/geoip/resolve?ip=10.0.0.1", headers=_AUTH_ANALYST)
    assert res.status_code == 200
    data = res.json()
    assert data["ip"] == "10.0.0.1"
    assert data["status"] in ("resolved", "unavailable")


def test_scenarios_endpoints(processed_client):
    scenarios = list_scenarios()
    assert len(scenarios) == 5

    res_list = processed_client.get("/api/v1/scenarios", headers=_AUTH_ANALYST)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 5

    res_detail = processed_client.get(
        "/api/v1/scenarios/multi-source-correlated", headers=_AUTH_ANALYST
    )
    assert res_detail.status_code == 200
    sc = res_detail.json()
    assert sc["category"] == "CRITICAL"
    assert sc["expected_risk"] == 100
    assert sc["target_user"] == "EMP11411"
    assert len(sc["steps"]) == 6

    # 404 for unknown scenario
    assert processed_client.get("/api/v1/scenarios/unknown-sc", headers=_AUTH_ANALYST).status_code == 404


def test_investigation_endpoint_with_question(processed_client):
    res = processed_client.get(
        "/api/investigations/EMP11411?question=Why%20is%20this%20user%20high%20risk%3F",
        headers=_AUTH_ANALYST,
    )
    assert res.status_code == 200
    inv = res.json()
    assert inv["grounded"] is True
    assert inv["user_id"] == "EMP11411"
    assert len(inv["citations"]) > 0
    assert "tools_completed" in inv
    assert "verify_citations" in inv["tools_completed"]


def test_frontend_routes_served_with_security_headers(processed_client):
    routes = ["/", "/login", "/employee", "/employee/activity", "/soc", "/soc/investigations", "/demo"]
    for route in routes:
        response = processed_client.get(route)
        assert response.status_code == 200
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert "default-src 'self'" in response.headers["content-security-policy"]
        assert "Detection operations" in response.text
        assert "ZeroTrust-X" in response.text
