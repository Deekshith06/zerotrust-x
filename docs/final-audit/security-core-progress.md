# Security-core implementation progress

## Locally implemented

- Aggregate evidence routes require SOC analyst/admin authentication.
- Unknown investigations fail with 404 rather than returning empty fabricated case state.
- Fractional port values are rejected instead of truncated.
- Quarantine output distinguishes finding count from affected source-row count, duplicate rows, source totals, and affected rows per source.
- `TenantStore` provides a durable SQLite repository boundary with tenant-owned composite keys and context-scoped reads/writes. It is an enforceable local contract and is not yet the authoritative store for Parquet API artifacts.
- `LocalAuditSink` provides sequence numbers, request/tenant context hooks, previous hashes, current hashes, and `verify_audit_chain`; API audit output now uses a separate `audit-chain.jsonl` path. This is tamper-evident, not filesystem immutable.
- `ExternalAuditSink` and `DistributedRateLimiter` are explicit integration contracts that fail closed by raising `NotImplementedError` until deployment infrastructure is configured.
- `LocalRateLimiter` provides process-local sliding-window limiting. It is not distributed and does not survive process restart.
- Request IDs are returned on normal and HTTP error responses.

## Still external or unverified

- OIDC/JWKS signature validation and browser authorization-code/PKCE flow.
- Wiring every existing Parquet query to the durable tenant store.
- Two-tenant production storage and graph traversal isolation.
- External WORM/object-lock audit retention.
- Shared rate-limit backend across workers/instances.
- Strict CSP without inline assets.
- Full LangGraph node/tool architecture with tenant-bound tool registry.
- Durable investigation state, analyst notes, recommendation approvals, and restart recovery.
- Dependency lockfile, SBOM, vulnerability scans, browser automation, load tests, and backup/restore drill.

The status remains **PRODUCTION-ORIENTED**. Local contracts must not be described as completed enterprise controls.
