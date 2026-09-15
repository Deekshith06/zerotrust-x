# ZeroTrust-X Task Plan

## Active tier

**P0 — deterministic ingestion, cleaning, unified events, detection, risk, and dashboard foundation**

## Completed

- [x] Confirm the four Track 2 data files and notes are present.
- [x] Perform an initial read-only schema and data-quality inventory.
- [x] Record malformed-value patterns and canonical join coverage in `findings.md`.

## Pending, in order

1. [x] Inspect repository state and available Python/runtime tooling.
2. [x] Create minimal project configuration and package layout.
3. [x] Add adversarial tests for initial normalization primitives.
4. [x] Implement explicit user-ID and categorical normalization.
5. [x] Implement initial multi-format timestamp parsing.
6. [x] Implement initial IP and risk validators.
7. [x] Implement source adapters for CSV, JSON, and XLSX.
8. [x] Implement provenance-preserving unified events and quarantine output.
9. [x] Write processed Parquet artifacts and a quality report; verify deterministic reruns.
10. [x] Add complete port, byte, hash, endpoint chronology, and duplicate validation.
11. [x] Add deterministic detection rules and reason-coded risk scoring.
12. [x] Add FastAPI health, summary, users, events, alerts, and data-quality routes.
13. [x] Build the polished P0 SOC dashboard using real API data.
14. [x] Run the full P0 suite and perform the self-roast/fix/retest loop.

## P1 backlog

- [ ] Add LangGraph investigation workflow with grounded read-only tools.
- [ ] Add programmatic citation/grounding validator and telemetry untrusted-data boundary.
- [ ] Add RBAC and audit logging.
- [ ] Add graph queries, employee portal, and deterministic live scenarios.

## Gate

Do not begin P1 (LangGraph, graph queries, RBAC, employee portal, or live scenarios) until every P0 test and acceptance criterion is green.
