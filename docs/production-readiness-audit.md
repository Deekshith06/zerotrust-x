# Production-readiness audit

**Status: production-oriented local reference implementation; not certified production-ready.**

## Evidence reviewed

- Source: `src/zerotrust_x/` and `tests/`
- Real Track 2 ingestion artifacts and independent A/B/C manifests generated directly from `track2_cybersecurity_dataset_files/`
- `README.md`, `docs/security.md`, `docs/evaluation.md`
- Ruff and pytest verification
- Reproducible ingestion runs, artifact-contract validation, and HTTP smoke checks on 2026-09-15

## Scorecard

| Area | Status | Evidence / limitation |
|---|---|---|
| Ingestion validation | Implemented locally | CSV/JSON/XLSX adapters, typed normalization, quarantine, provenance; independent reruns match |
| Deterministic detection | Implemented | Rule-based detections and bounded risk score |
| Grounded investigation | Implemented locally | Citation validation and read-only deterministic fallback; optional LangGraph only |
| Prompt-injection boundary | Implemented locally | Telemetry wrapper and adversarial grounding test |
| RBAC | Simulated/local | Demo header tokens; analyst/admin protection now covers aggregate evidence routes; no external IdP |
| OIDC/SSO | Contract/configuration only | Provider and JWKS integration remain unverified |
| Tenant isolation | Implemented locally / deployment unverified | Tenant context and SQLite store enforce local scope; current artifacts remain single-tenant and deployed durable isolation is unverified |
| Audit logging | Local tamper-evident | Hash-chained JSONL with verification and context hooks; filesystem is not immutable and external retention remains unverified |
| Rate limiting | Local partial control | Process-local sliding-window limiter now protects `/api/*`; no distributed limiter/backend is present |
| CSRF | Not applicable to current read-only GET routes | Current CORS policy permits only GET/OPTIONS; CSRF must be added before cookie-authenticated mutations |
| Observability | Process-local | Request IDs and structured timing logs are present; no distributed tracing or durable metrics backend |
| Threat labels | Unverified | Dataset is synthetic and lacks verified ground truth |
| Container | Local asset | Non-root/read-only guidance exists; dependency version evidence is checked in CI, but image scanning and production orchestration validation remain unverified |
| Backup/restore | Local verification implemented / production unverified | Recovery bundle copy/hash verification is tested; encrypted production recovery environment and RPO/RTO remain unmeasured |

## Priority findings

### High

1. The local authentication adapter must not be used for production. Integrate a validated OIDC provider, issuer/audience checks, JWKS rotation, session policy, and lifecycle controls.
2. Durable storage must enforce tenant isolation at repository and storage layers before multi-tenant deployment.
3. Audit JSONL must be exported to an append-only external retention system for operational accountability.

### Medium

1. Add distributed, tenant-aware rate limiting for ingestion, investigations, graph queries, and authentication endpoints.
2. Add load benchmarks and p95/p99 measurements under representative telemetry volumes.
3. Add dependency lock and image vulnerability scanning in CI.
4. Add cookie/CSRF controls only when state-changing browser endpoints are introduced.

### Low

1. Expand adapter SDK examples and schema-version migration documentation.
2. Add analyst annotation and human approval workflows behind explicit policy checks.

## What is verified

The local verification gate currently covers deterministic artifacts, strict v2 artifact-contract validation, complete event/finding provenance, role boundaries, employee self-scope, unknown-resource fail-closed behavior, grounding behavior, graph provenance, XSS-safe dashboard rendering, and reproducible ingestion. It does not prove enterprise identity, availability, confidentiality, or incident-detection accuracy.

## Latest local verification evidence — 2026-09-15

- Ruff: PASS.
- Pytest: 67 passed; one upstream Starlette/AnyIO deprecation warning.
- Fresh source run: 62,430 events, 36,220 quarantine findings, 29,536 affected rows, 1,473 detections, and 3,000 risk identities.
- Local recovery verification: PASS for complete bundle copy and source/output hash validation; corrupted and existing destinations are rejected.
- Bounded local benchmark: PASS for summary, filtered events, graph, and investigation smoke operations; timings are environment-specific and not production SLO evidence.
- A/B/C artifact comparison: PASS; manifests and generated artifacts matched.
- Source immutability comparison: PASS; all original source hashes matched before and after execution.
- Provenance null scan: PASS for required event and finding provenance fields, including iteration ID and normalization-rule version.
- API probes: disposable valid artifact set `/ready` 200, checked-in legacy `/ready` 503, aggregate route without token 401, analyst aggregate access 200 on valid disposable artifacts, employee cross-scope timeline 403, unknown graph 404, unknown investigation 404.
- Credential-pattern scan: no application credential or private-key material identified; local adapter tokens are intentionally local fixtures and are not production authentication.
