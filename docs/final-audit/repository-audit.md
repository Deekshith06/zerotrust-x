# ZeroTrust-X Final Repository Audit

**Review date:** 2026-09-14  
**Reviewer mode:** independent read-only forensic pass before remediation  
**Scope:** source, tests, generated artifacts, deployment files, documentation, and local HTTP behavior.

## Executive finding

The repository is a working local synthetic-telemetry demonstration, not an independently validated production service. The deterministic pipeline and read-only investigation flow are present, but several API routes expose evidence without authentication, the local demo identity model is not an OIDC implementation, and tenant isolation is only a contract because artifacts are single-tenant. These findings prevent a higher deployment status.

## Inventory observations

- Python package: `src/zerotrust_x/` with FastAPI, Polars/Parquet, CSV/JSON/XLSX readers, deterministic detections, graph, investigation, and server-rendered dashboard.
- Tests: unit, integration, web, production, and adversarial boundary tests; no browser automation suite and no dedicated multi-tenant storage fixture.
- Runtime artifacts are generated under `data/processed` and `data/quarantine`; local audit output is `data/audit.jsonl` by default.
- The repository contains `.venv`, caches, bytecode, `.DS_Store`, and egg-info in the working tree. `.gitignore` excludes most generated material, but this review does not establish whether any of those files are tracked because this directory is not a Git repository.

## Route exposure audit

Direct `TestClient` probes against `create_app(data/processed)` returned:

| Route family | No token | Finding |
|---|---:|---|
| `/health`, `/ready` | 200 | Intended operational probes |
| `/api/summary` | 200 | Aggregate evidence is public |
| `/api/users`, `/api/users/{id}` | 200 | Risk identities and scores are public |
| `/api/events` | 200 | Telemetry is public |
| `/api/alerts` | 200 | Detection records are public |
| `/api/users/{id}/timeline` | 401 | Protected |
| `/api/graph/{id}` | 401 | Protected |
| `/api/investigations/{id}` | 401 | Protected |
| `/api/data-quality` | 401 | Protected after hardening |
| `/api/manifest`, `/api/evaluation`, `/api/anomalies` | 401 | Protected |

The public evidence routes are a **HIGH** confidentiality issue for any deployment containing non-synthetic telemetry. Frontend hiding does not mitigate this.

## Authentication and authorization

- `src/zerotrust_x/access.py` implements only static `X-Demo-Token` values.
- `Settings` validates that OIDC issuer/audience are configured outside demo mode, but no JWT signature, issuer, audience, expiry, JWKS retrieval, key rotation, or claim-to-tenant mapping is implemented.
- Employee self-scope is enforced only on the timeline route. Public user/event/alert routes bypass that scope.
- Roles are limited to `EMPLOYEE`, `SOC_ANALYST`, and `SOC_ADMIN`; requested enterprise roles such as tenant/platform administrators do not exist.
- `TenantContext` is an architectural contract only. No tenant field is present on persisted events, detections, risks, or query filters.

## Data and pipeline observations

- Pipeline output is deterministic across two clean runs for the supplied files.
- `seen_ids` detects duplicate `(source, event_id)` values, but missing source IDs fall back to source-row-derived IDs; cross-source identity collisions are not resolved.
- A normalized user ID removes all non-alphanumeric characters before validation. This makes `EMP-12345`, `EMP 12345`, and `12345` equivalent by design, but also means the helper is not safe as a general identity resolver without ambiguity checks.
- The audit found that `parse_port` previously converted through `float` and then `int`, silently accepting a fractional value such as `65535.5` as `65535`. This was fixed locally to require an integer lexical form, with a regression test.
- `parse_timestamp` supports several explicit formats, but date-only slash values are interpreted as day/month/year and epoch parsing only recognizes ten-digit seconds.
- Quarantine preserves raw values, raw payloads, provenance, deterministic classifications, and reason codes; findings and affected records are reported separately. The current post-fix output is 36,220 findings affecting 29,536 rows; the earlier 46,008/33,596 values are retained as a historical pre-fix baseline.

## Agent and grounding observations

- The current investigation path is deterministic and does not invoke an LLM by default.
- `compile_langgraph` is dependency-gated but only creates an intake graph; no production tool registry, authorization context, or external action path is implemented.
- Citation validation checks identifiers present in evidence but does not prove semantic correctness of every prose claim.
- Telemetry boundary escaping is tested for the closing delimiter, but there is no full adversarial agent harness exercising all requested injection locations.

## Deployment and dependency observations

- Docker uses a non-root user and read-only Compose filesystem guidance.
- No lockfile, SBOM, image scan, dependency vulnerability scan, load test, backup/restore drill, or external audit-retention verification is present.
- Runtime dependency ranges in `pyproject.toml` are not a reproducible lock strategy.
- CSP still permits `'unsafe-inline'` because the dashboard embeds CSS and JavaScript.
- Local JSONL audit is append-mode application behavior, not immutable retention; a process or filesystem administrator can rewrite it.

## Required remediation priorities

1. **Fixed locally:** protected `/api/summary`, `/api/users`, `/api/users/{id}`, `/api/events`, and `/api/alerts` with analyst/admin dependencies; dashboard requests now send the analyst demo header.
2. **Partially fixed locally:** added regression coverage for protected evidence routes and unknown investigations. Full employee-vs-analyst resource policy remains a product decision.
3. **Fixed locally:** corrected fractional port acceptance and added a normalization regression test.
4. **Documented:** affected-record and finding counts are now distinguished in `quarantine-quality-report.md`; the production API still returns the legacy finding count for compatibility.
5. Treat OIDC/JWKS, durable tenant isolation, external audit immutability, distributed rate limiting, dependency scanning, and recovery drills as **EXTERNAL DEPENDENCY / UNVERIFIED** until exercised.
