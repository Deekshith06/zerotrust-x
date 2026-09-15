# Track 2 alignment and evidence scorecard

## Scope

ZeroTrust-X is aligned to the synthetic TransOrg AgentIQ Track 2 bundle: IAM audit,
firewall, endpoint, and identity/asset telemetry. This document separates observed
implementation evidence from unsupported or externally unverified claims. It is not
a maliciousness, insider-threat, precision, or recall report.

## Requirements-to-evidence matrix

| Track 2 requirement | Current status | Evidence / boundary |
|---|---|---|
| Ingest CSV, JSON, XLSX sources | Implemented locally | `pipeline.py`, source readers, deterministic disposable runs |
| Standardize employee IDs | Implemented locally | `normalize_user_id`; canonical `EMP` plus digits |
| Standardize departments | Implemented locally | `normalize_department`; canonical value is retained on events |
| Parse mixed timestamps | Implemented locally | `parse_timestamp`; raw value and format are retained |
| Normalize firewall actions/protocols/ports/bytes | Implemented locally | typed canonical event columns plus quarantine reason codes |
| Normalize IAM event types | Partial and intentional | login success/failure, MFA failure, and other action subtypes are retained; raw type is preserved |
| Normalize endpoint severity/status | Implemented locally | canonical fields plus raw payload/provenance |
| Preserve missing/duplicate/invalid values | Implemented locally | quarantine rows retain raw value, payload, row, ID, hash, classification, and reason |
| Expected source joins | Partial | normalized keys and evidence graph exist; unmatched/ambiguous relationships are not guessed |
| Dashboard example questions | Partial | bounded event/detection views exist; unsupported aggregations must not be represented as completed |
| Optional graph-first agent | Implemented as grounded local workflow | deterministic investigation and citation validation are authoritative; optional LangGraph adapter is local only |

The source data is synthetic and contains no independently verified incident or
insider-threat labels. A suspicious pattern is not proof of malicious intent.

## Weighted evidence scorecard

The score is a review prioritization tool, not a threat-detection accuracy score.
Weights total 100:

| Dimension | Weight | Local evidence required |
|---|---:|---|
| Ingestion and source coverage | 15 | all four declared files, source hashes, rerun |
| Normalization and quarantine | 20 | canonical fields, invalid-value findings, raw preservation |
| Provenance and reproducibility | 15 | stable manifest/artifact hashes and source immutability |
| Deterministic detections and explainable risk | 15 | rule IDs, evidence IDs, stable severity and score behavior |
| Joins, correlation, and grounded investigation | 10 | bounded keys, ambiguity handling, citation validation |
| Dashboard question coverage and UX | 10 | supported queries and truthful empty/unsupported states |
| Agent safety and authorization | 10 | typed tools, read-only scope, rejected unsupported citations |
| Tests, documentation, and status honesty | 5 | regression suite, limitations, unverified controls |

Each dimension must be reported as `implemented`, `partial`, `unsupported`, or
`unverified` with a test or artifact reference. The weighted result must not be
converted into a production-readiness or threat-label claim.

## Deterministic detection and risk boundary

Current detections are generated without an LLM:

- `MULTIPLE_FAILED_LOGINS`: at least three `login_failed` or `mfa_failed` events for an identity.
- `MFA_FAILURE`: one or more `mfa_failed` events for an identity.
- Current checked-in detections are high severity only; absence of other severities is a valid artifact property.

Current derived risk is bounded to 0–100 and uses failed authentication events,
endpoint alerts, and firewall denies. It is explainable and reproducible but not
calibrated against verified labels. Source `risk_score` values remain telemetry,
not ground truth.

## Grounded agent boundary

The investigation workflow is read-only:

`intake → bounded evidence collection → deterministic correlation → report → citation validation`

Allowed agent responsibilities are planning or summarizing evidence already returned
by typed bounded tools. The agent may not normalize data, detect threats, assign risk
or severity, invent joins/citations, execute SQL/Polars/shell/filesystem/network/browser
operations, mutate artifacts, or take response actions. Telemetry is untrusted data,
including instruction-like strings. Unsupported citations reject a report and missing
information remains explicit.

## Dashboard filter decision

The dashboard exposes user, source, and event-severity filters. The detection-severity
select was removed because the checked-in detection artifact is high-only and the
control was misleading. API-level detection filtering remains available and typed;
removing the UI control does not weaken the backend contract. Event-backed fallback
signals remain available for event severity selections.

## Artifact contract and readiness

Generated v2 artifact directories are validated before readiness and API consumption. Validation requires the manifest schema, `unified-event-v2`, required output set, expected local artifact locations, SHA-256 matches, required Parquet columns, and consistent quality counts. Missing, legacy, malformed, tampered, or schema-incompatible artifact sets fail closed with sanitized `503` responses. The checked-in legacy artifact set remains immutable and is intentionally not ready until separately migrated.

## Control status boundary

The complete local-versus-deployment status matrix is maintained in `docs/status-matrix.md`. Local tenant-boundary tests, recovery verification, dependency-version evidence, and bounded benchmark measurements are implemented locally. OIDC/JWKS, durable deployed tenancy, external immutable retention, distributed limiting, browser E2E, production-scale performance, production backup RPO/RTO, image scanning/signing, and verified threat accuracy remain unverified because this repository does not contain the required external systems or ground truth.

## Known unsupported or unverified controls

- Verified insider-threat labels, malicious-intent inference, and detection precision/recall.
- Complete department/time-series/protocol aggregations unless a bounded route and test exists.
- External OIDC/JWKS, durable tenant isolation, distributed rate limiting, immutable external audit retention.
- Browser E2E, enterprise load/performance, backup/restore, dependency/SBOM scanning, and external connectors.

Deployment status remains `PRODUCTION-ORIENTED`.
