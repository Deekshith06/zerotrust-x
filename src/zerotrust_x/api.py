"""Small read-only FastAPI surface over generated Parquet artifacts."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import polars as pl
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from zerotrust_x.access import Role, can_read_user, require_role, tenant_context
from zerotrust_x.anomaly import baseline_scores
from zerotrust_x.artifacts import ArtifactContractError, validate_artifact_contract
from zerotrust_x.audit import append_audit
from zerotrust_x.config import load_settings
from zerotrust_x.evaluation import evaluation_report
from zerotrust_x.filters import Dataset, FilterSpec
from zerotrust_x.geoip import get_geoip_provider
from zerotrust_x.graph import user_graph
from zerotrust_x.investigation import investigate
from zerotrust_x.observability import measure, metrics
from zerotrust_x.observability import request_id as new_request_id
from zerotrust_x.query import (
    ArtifactMalformedError,
    ArtifactMissingError,
    ArtifactQuery,
    ArtifactQueryError,
    ArtifactSchemaError,
)
from zerotrust_x.rate_limit import LocalRateLimiter, RateLimitKey
from zerotrust_x.scenarios import get_scenario, list_scenarios


def create_app(processed_dir: Path = Path("data/processed")) -> FastAPI:
    app = FastAPI(title="ZeroTrust-X SOC API", version="0.1.0")
    settings = replace(
        load_settings(),
        processed_dir=processed_dir,
        audit_path=processed_dir.parent / "audit-chain.jsonl",
    )
    limiter = LocalRateLimiter(limit=settings.rate_limit_per_minute)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Authorization", "Content-Type", "X-Demo-Token", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or new_request_id()
        if request.url.path.startswith("/api/"):
            key = RateLimitKey(
                scope=request.url.path.split("/", 3)[2] if len(request.url.path.split("/", 3)) > 2 else "api",
                tenant_id=settings.tenant_id,
                subject=request.headers.get("X-Demo-Token"),
                client_ip=request.client.host if request.client else None,
            )
            if not limiter.allow(key):
                response = JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                response.headers["X-Request-ID"] = request_id
                return response
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(ArtifactQueryError)
    async def artifact_error(request: Request, exc: ArtifactQueryError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID") or new_request_id()
        response = JSONResponse(status_code=503, content={"detail": "Required artifact is unavailable"})
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID") or new_request_id()
        response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        response.headers["X-Request-ID"] = request_id
        return response

    def require_artifacts() -> dict[str, Any]:
        try:
            return validate_artifact_contract(processed_dir)
        except ArtifactContractError as exc:
            raise HTTPException(status_code=503, detail="Required artifact set is not ready") from exc

    def require_contract_for_query() -> None:
        try:
            validate_artifact_contract(processed_dir)
        except ArtifactContractError as exc:
            raise HTTPException(status_code=503, detail="Required artifact set is not ready") from exc

    def read(name: str) -> pl.DataFrame:
        require_artifacts()
        path = processed_dir / name
        if not path.exists():
            raise HTTPException(status_code=503, detail="Required artifact is unavailable")
        try:
            return pl.read_parquet(path)
        except (OSError, pl.exceptions.PolarsError) as exc:
            raise HTTPException(status_code=503, detail="Required artifact is unavailable") from exc

    def query_result(query: ArtifactQuery, spec: FilterSpec) -> dict[str, Any]:
        require_contract_for_query()
        try:
            return query.query(spec)
        except ArtifactMissingError as exc:
            raise HTTPException(status_code=503, detail="Required artifact is unavailable") from exc
        except (ArtifactMalformedError, ArtifactSchemaError) as exc:
            raise HTTPException(status_code=503, detail="Required artifact is invalid") from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, Any]:
        contract = require_artifacts()
        return {
            "status": "ready",
            "artifacts": sorted(contract["manifest"]["outputs"]),
            "event_schema_version": contract["manifest"]["event_schema_version"],
        }

    def parse_spec(
        dataset: Dataset,
        filters: str | None,
        sort_by: str | None,
        descending: bool,
        offset: int,
        limit: int,
    ) -> FilterSpec:
        try:
            return FilterSpec.from_json(
                dataset, filters, sort_by=sort_by, descending=descending, offset=offset, limit=limit
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/summary")
    def summary(actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> dict[str, Any]:
        require_artifacts()
        events = read("events.parquet")
        risks = read("user_risk.parquet")
        detections = read("detections.parquet")
        return {
            "events": events.height,
            "users": risks.height,
            "high_risk_users": risks.filter(pl.col("risk_level").is_in(["high", "critical"])).height,
            "critical_users": risks.filter(pl.col("risk_level") == "critical").height,
            "detections": detections.height,
            "sources": events.get_column("source").n_unique(),
        }

    @app.get("/api/v1/events")
    def filtered_events(
        filters: str | None = Query(None, max_length=4096),
        sort_by: str | None = Query(None),
        descending: bool = Query(False),
        offset: int = Query(0, ge=0, le=100000),
        limit: int = Query(50, ge=1, le=200),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        spec = parse_spec(Dataset.EVENTS, filters, sort_by, descending, offset, limit)
        return query_result(ArtifactQuery(processed_dir), spec)

    @app.get("/api/v1/global")
    def global_activity(
        limit: int = Query(25, ge=1, le=100),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        """Return bounded country activity from explicit telemetry only.

        A missing ``geo_country`` value is intentionally grouped as unresolved;
        no IP-to-country inference or external lookup occurs here.
        """
        events = read("events.parquet")
        if "geo_country" not in events.columns:
            raise HTTPException(status_code=503, detail="Country field is unavailable")
        country = pl.col("geo_country").fill_null("UNKNOWN / UNRESOLVED").replace("", "UNKNOWN / UNRESOLVED")
        grouped = (
            events.with_columns(country.alias("country"))
            .group_by("country")
            .agg(
                pl.len().alias("event_count"),
                pl.col("source").drop_nulls().unique().sort().alias("sources"),
                pl.col("severity").drop_nulls().unique().sort().alias("severities"),
                pl.col("event_id").drop_nulls().sort().head(5).alias("sample_event_ids"),
            )
            .sort(["event_count", "country"], descending=[True, False])
            .head(limit)
        )
        return {
            "country_field": "geo_country",
            "country_source": "explicit telemetry field",
            "unresolved_label": "UNKNOWN / UNRESOLVED",
            "items": grouped.to_dicts(),
            "total_events": events.height,
            "resolved_events": events.filter(pl.col("geo_country").is_not_null() & (pl.col("geo_country") != "")).height,
            "unresolved_events": events.filter(pl.col("geo_country").is_null() | (pl.col("geo_country") == "")).height,
        }

    @app.get("/api/v1/global/country/{country_code}")
    def country_detail(
        country_code: str,
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        """Return drill-down intelligence for a specific country from explicit telemetry.

        Transitions: Country -> IPs -> Users -> Devices -> Sessions -> Events -> Alerts.
        Never guesses country.
        """
        require_contract_for_query()
        events = read("events.parquet")
        risks = read("user_risk.parquet")
        detections = read("detections.parquet")

        code_upper = country_code.strip().upper()
        if code_upper in ("UNKNOWN", "UNRESOLVED", "UNKNOWN / UNRESOLVED"):
            country_events = events.filter(pl.col("geo_country").is_null() | (pl.col("geo_country") == ""))
            country_name = "Unknown / Unresolved"
            code_upper = "UNRESOLVED"
        else:
            country_events = events.filter(pl.col("geo_country") == code_upper)
            country_names = {
                "IN": "India",
                "US": "United States",
                "RU": "Russia",
                "CN": "China",
                "GB": "United Kingdom",
            }
            country_name = country_names.get(code_upper, code_upper)

        if country_events.is_empty():
            raise HTTPException(status_code=404, detail=f"No telemetry found for country: {country_code}")

        ip_counts = (
            country_events.filter(pl.col("source_ip").is_not_null() & (pl.col("source_ip") != ""))
            .group_by("source_ip")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
            .head(15)
            .to_dicts()
        )
        c_ips = [r["source_ip"] for r in ip_counts]

        correl_events = events.filter(pl.col("source_ip").is_in(c_ips) & pl.col("user_id").is_not_null())
        correl_user_ids = correl_events["user_id"].unique().to_list()
        correl_devices = [d for d in correl_events["device_id"].drop_nulls().unique().to_list() if d]
        correl_sessions = [s for s in correl_events["session_id"].drop_nulls().unique().to_list() if s]

        correl_risks = (
            risks.filter(pl.col("user_id").is_in(correl_user_ids))
            .sort("risk_score", descending=True)
            .head(10)
            .to_dicts()
        )
        correl_detections = (
            detections.filter(pl.col("user_id").is_in(correl_user_ids))
            .head(10)
            .to_dicts()
        )

        sources = country_events["source"].value_counts().to_dicts()
        actions = country_events["action"].drop_nulls().value_counts().to_dicts()
        failed_auth = country_events.filter(pl.col("event_type").is_in(["login_failed", "mfa_failed"])).height

        return {
            "country_code": code_upper,
            "country_name": country_name,
            "provenance": "explicit telemetry field (`geo_country` in events.parquet)",
            "geo_provider_status": "telemetry-native" if code_upper != "UNRESOLVED" else "unresolved",
            "event_count": country_events.height,
            "failed_auth_count": failed_auth,
            "sources": sources,
            "actions": actions,
            "top_ips": ip_counts,
            "correlated_users": correl_risks,
            "correlated_devices": correl_devices[:10],
            "correlated_sessions": correl_sessions[:10],
            "correlated_alerts": correl_detections,
            "sample_events": country_events.head(8).to_dicts(),
        }

    @app.get("/api/v1/geoip/resolve")
    def resolve_ip(
        ip: str = Query(..., min_length=1, max_length=64),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        """Resolve IP address with provenance. Geolocation inference strictly prohibited."""
        require_contract_for_query()
        events = read("events.parquet")
        matching = events.filter((pl.col("source_ip") == ip) & pl.col("geo_country").is_not_null()).head(1)
        explicit = matching["geo_country"][0] if not matching.is_empty() else None
        resolution = get_geoip_provider().resolve(ip, explicit_country=explicit)
        return resolution.to_dict()


    @app.get("/api/v1/alerts")
    def filtered_alerts(
        filters: str | None = Query(None, max_length=4096),
        sort_by: str | None = Query(None),
        descending: bool = Query(False),
        offset: int = Query(0, ge=0, le=100000),
        limit: int = Query(50, ge=1, le=200),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        spec = parse_spec(Dataset.DETECTIONS, filters, sort_by, descending, offset, limit)
        return query_result(ArtifactQuery(processed_dir), spec)

    @app.get("/api/v1/summary")
    def filtered_summary(
        event_filters: str | None = Query(None, max_length=4096),
        detection_filters: str | None = Query(None, max_length=4096),
        risk_filters: str | None = Query(None, max_length=4096),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        query = ArtifactQuery(processed_dir)
        event_spec = parse_spec(Dataset.EVENTS, event_filters, None, False, 0, 1)
        detection_spec = parse_spec(Dataset.DETECTIONS, detection_filters, None, False, 0, 1)
        risk_spec = parse_spec(Dataset.USER_RISK, risk_filters, None, False, 0, 1)
        event_result = query_result(query, event_spec)
        detection_result = query_result(query, detection_spec)
        risk_result = query_result(query, risk_spec)
        try:
            risk_clauses = [] if not risk_filters else json.loads(risk_filters)
            risk_clauses.append({"field": "risk_level", "op": "in", "value": ["high", "critical"]})
            high_risk_spec = FilterSpec.from_json(
                Dataset.USER_RISK, json.dumps(risk_clauses), limit=200
            )
        except (TypeError, json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail="invalid risk filters") from exc
        high_risk_result = query_result(query, high_risk_spec)
        baseline = {
            "dataset_version": "data-quality-v1",
            "events": read("events.parquet").height,
            "detections": read("detections.parquet").height,
            "users": read("user_risk.parquet").height,
        }
        return {
            "events": baseline["events"],
            "users": baseline["users"],
            "detections": baseline["detections"],
            "high_risk_users": high_risk_result["filtered_count"],
            "baseline": baseline,
            "filtered": {
                "events": event_result["filtered_count"],
                "detections": detection_result["filtered_count"],
                "users": risk_result["filtered_count"],
                "high_risk_users": high_risk_result["filtered_count"],
            },
        }

    @app.get("/api/v1/users")
    def filtered_users(
        filters: str | None = Query(None, max_length=4096),
        sort_by: str | None = Query(None),
        descending: bool = Query(False),
        offset: int = Query(0, ge=0, le=100000),
        limit: int = Query(50, ge=1, le=200),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        spec = parse_spec(Dataset.USER_RISK, filters, sort_by, descending, offset, limit)
        return query_result(ArtifactQuery(processed_dir), spec)

    @app.get("/api/users")
    def users(
        limit: int = Query(50, ge=1, le=500),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> list[dict[str, Any]]:
        return read("user_risk.parquet").head(limit).to_dicts()

    @app.get("/api/users/{user_id}")
    def user(
        user_id: str,
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        rows = read("user_risk.parquet").filter(pl.col("user_id") == user_id).to_dicts()
        if not rows:
            raise HTTPException(status_code=404, detail="User not found")
        return rows[0]

    @app.get("/api/events")
    def events(
        limit: int = Query(100, ge=1, le=1000),
        user_id: str | None = None,
        clean_only: bool = Query(False),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> list[dict[str, Any]]:
        filename = "clean_events.parquet" if clean_only else "events.parquet"
        frame = read(filename)
        if user_id:
            frame = frame.filter(pl.col("user_id") == user_id)
        return frame.head(limit).to_dicts()

    @app.get("/api/alerts")
    def alerts(
        limit: int = Query(100, ge=1, le=1000),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> list[dict[str, Any]]:
        return read("detections.parquet").head(limit).to_dicts()

    @app.get("/api/users/{user_id}/timeline")
    def timeline(user_id: str, actor=Depends(require_role(Role.EMPLOYEE, Role.SOC_ANALYST, Role.SOC_ADMIN))) -> list[dict[str, Any]]:
        require_contract_for_query()
        if not can_read_user(actor, user_id):
            raise HTTPException(status_code=403, detail="Employee access is limited to their own identity")
        context = tenant_context(actor, settings.tenant_id)
        append_audit(
            settings.audit_path, context.subject, "read_timeline", user_id, "success",
            tenant_id=context.tenant_id,
        )
        return ArtifactQuery(processed_dir).events_for_user(user_id)

    @app.get("/api/graph/{user_id}")
    def graph(user_id: str, actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> dict[str, Any]:
        require_contract_for_query()
        result = user_graph(ArtifactQuery(processed_dir), user_id)
        if not result["nodes"]:
            raise HTTPException(status_code=404, detail="Identity not found in indexed artifacts")
        return result

    @app.get("/api/investigations/{user_id}")
    def investigation(
        user_id: str,
        question: str | None = Query(None),
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN)),
    ) -> dict[str, Any]:
        require_contract_for_query()
        query = ArtifactQuery(processed_dir)
        if not query.user_risk(user_id) and not query.events_for_user(user_id) and not query.detections_for_user(user_id):
            raise HTTPException(status_code=404, detail="Identity not found in indexed artifacts")
        with measure("investigation"):
            result = investigate(user_id, question or f"Investigate {user_id}", processed_dir)
        context = tenant_context(actor, settings.tenant_id)
        append_audit(
            settings.audit_path, context.subject, "investigate", user_id, result.status,
            tenant_id=context.tenant_id,
        )
        return result.__dict__

    @app.get("/api/v1/scenarios")
    def scenarios_list(
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN, Role.EMPLOYEE)),
    ) -> list[dict[str, Any]]:
        return list_scenarios()

    @app.get("/api/v1/scenarios/{scenario_id}")
    def scenario_detail(
        scenario_id: str,
        actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN, Role.EMPLOYEE)),
    ) -> dict[str, Any]:
        sc = get_scenario(scenario_id)
        if not sc:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return sc

    @app.get("/api/metrics")
    def process_metrics(actor=Depends(require_role(Role.SOC_ADMIN))) -> dict[str, Any]:
        return metrics()

    @app.get("/api/evaluation")
    def evaluation(actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> dict[str, Any]:
        try:
            return evaluation_report(processed_dir)
        except FileNotFoundError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.get("/api/manifest")
    def manifest(actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> dict[str, Any]:
        return require_artifacts()["manifest"]

    @app.get("/api/anomalies")
    def anomalies(limit: int = Query(100, ge=1, le=500), actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> list[dict[str, Any]]:
        require_contract_for_query()
        events = read("events.parquet").to_dicts()
        return baseline_scores(events)[:limit]

    @app.get("/api/employee")
    def employee_portal(actor=Depends(require_role(Role.EMPLOYEE))) -> dict[str, Any]:
        require_contract_for_query()
        user_id = actor[1]
        if not user_id:
            raise HTTPException(status_code=403, detail="Employee identity is required")
        query = ArtifactQuery(processed_dir)
        return {
            "profile": query.user_risk(user_id),
            "recent_activity": query.events_for_user(user_id, limit=25),
        }

    @app.get("/api/data-quality")
    def data_quality(actor=Depends(require_role(Role.SOC_ANALYST, Role.SOC_ADMIN))) -> dict[str, Any]:
        return require_artifacts()["quality"]

    return app


app = create_app()
