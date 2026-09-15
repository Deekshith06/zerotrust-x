# Production API contract

The current unversioned routes remain for local compatibility. A production gateway should expose equivalent contracts under `/api/v1/` after an explicit migration.

| Route family | Auth | Scope | Mutation | Audit |
|---|---|---|---|---|
| `/health`, `/ready` | Public/process policy | Deployment | No | No |
| `/api/summary`, `/api/users`, `/api/events`, `/api/alerts` | Auth in production | Tenant | No | Optional access log |
| `/api/users/{id}/timeline` | Employee self or analyst/admin | Tenant + resource | No | Yes |
| `/api/graph/{id}`, `/api/investigations/{id}`, `/api/anomalies` | Analyst/admin | Tenant + resource | No | Yes |
| `/api/metrics`, `/api/manifest`, `/api/evaluation`, `/api/v1/global` | Admin/analyst policy | Deployment/tenant policy | No | Yes |

All inputs are bounded and all errors should use explicit HTTP status codes. No endpoint accepts arbitrary SQL, shell, filesystem paths, or model-generated query text. State-changing routes are not currently exposed; CSRF is required before adding cookie-authenticated mutations.

## Complete-dataset filtering

The versioned list routes expose bounded, read-only filtering over immutable Parquet artifacts:

- `GET /api/v1/events`
- `GET /api/v1/alerts` (detections)
- `GET /api/v1/users` (risk register)
- `GET /api/v1/summary` with separate `event_filters`, `detection_filters`, and `risk_filters`

List routes accept `filters` as a JSON array of allowlisted `{field, op, value}` clauses, plus `sort_by`, `descending`, `offset`, and `limit`. Unknown fields/operators, malformed JSON, null clauses, wrong scalar/list types, non-finite numbers, invalid timestamps, excessive clauses, and unbounded pagination return `422`. String fields require non-empty values; null is not a filter value, and null artifact values do not match equality, membership, or ordered predicates. Timestamps must be UTC seconds in the canonical `YYYY-MM-DDTHH:MM:SS+00:00` form. SQL, Polars expressions, paths, and model-generated query text are never accepted. Responses contain `items`, `filtered_count`, `has_more`, canonical filters, and deterministic sorting with a unique ID tie-breaker; sorting always places nulls last. Authorization scope is applied before filtering, counting, and paging. Missing, legacy, malformed, tampered, or schema-invalid artifact sets return a stable `503` without filesystem paths, hashes, or tracebacks. Every artifact-consuming route family uses the same strict v2 contract gate; `/health` remains process-only and `/ready` is the public readiness boundary. Contract validation is intentionally per-request and local; no distributed freshness or external integrity guarantee is implied.

`GET /api/v1/global` returns bounded country activity grouped from the explicit `geo_country` event field. Null or empty values are returned as `UNKNOWN / UNRESOLVED`; the route performs no IP geolocation or external enrichment. It is analyst/admin protected and remains tenant-scoped through the application boundary.

Filtered totals are derived views. They do not modify detections, risk, source files, generated artifacts, or frozen `data-quality-v1`. Summary responses retain compatibility top-level totals and also expose distinct `baseline` and `filtered` sections. `baseline` is always the unfiltered artifact total; `filtered` independently applies each supplied dataset filter. `filtered.high_risk_users` is the intersection of the supplied risk filter and `risk_level in ["high", "critical"]`; it never changes baseline totals.
