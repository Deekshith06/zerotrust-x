# Control status matrix

This matrix distinguishes repository evidence from deployment-dependent controls. `PRODUCTION-ORIENTED` is the truthful overall status.

| Control | Status | Local evidence | External prerequisite / boundary |
|---|---|---|---|
| Track 2 ingestion and normalization | IMPLEMENTED LOCALLY | 67-test suite, deterministic 62,430-row disposable runs | Synthetic data only |
| Provenance, quarantine, and raw preservation | IMPLEMENTED LOCALLY | Quarantine schema, source hashes, frozen baseline checks | No external retention claim |
| Artifact integrity and readiness | IMPLEMENTED LOCALLY | v2 manifest/hash/schema/quality validator and failure matrix | Local filesystem integrity only |
| Deterministic detection and bounded risk | IMPLEMENTED LOCALLY | Rule tests, stable detections/risk outputs | No verified incident labels |
| Grounded investigation | IMPLEMENTED LOCALLY | Read-only evidence collection and citation validation | No response automation |
| Dashboard and bounded filtering | IMPLEMENTED LOCALLY | API/web tests and live HTTP smoke check | Browser E2E remains unverified |
| Local RBAC/self-scope | IMPLEMENTED LOCALLY | Demo-token role and employee-scope tests | Demo adapter is not production identity |
| Tenant context/store boundary | IMPLEMENTED LOCALLY | Tenant context and cross-tenant store tests | Durable deployed isolation unverified |
| Local audit chain | IMPLEMENTED LOCALLY | Hash-chain verification tests | External WORM retention unverified |
| Local rate limiting | IMPLEMENTED LOCALLY | Process-local limiter tests | Distributed backend unverified |
| Local recovery verification | IMPLEMENTED LOCALLY | Copy, hash, corruption, and incomplete-bundle tests | Encrypted/versioned production backups unverified |
| Local benchmark | IMPLEMENTED LOCALLY | Bounded benchmark script over disposable artifacts | Enterprise p95/p99/load unverified |
| Dependency version evidence | IMPLEMENTED LOCALLY | `requirements.lock` and CI version check | Image scan/signing still external |
| OIDC/JWKS/SCIM | CONTRACT ONLY | Production settings fail closed without issuer/audience | Real provider, rotation, sessions, lifecycle |
| Durable multi-tenant deployment | UNVERIFIED | Local store boundary only | Tenant-aware storage and operations |
| External immutable audit retention | UNVERIFIED | `ExternalAuditSink` contract only | WORM/object-lock service and retrieval drill |
| Distributed rate limiting | UNVERIFIED | `DistributedRateLimiter` contract only | Shared backend and failure testing |
| Browser E2E with real identity | UNVERIFIED | Server-rendered shell tests only | Real browser and IdP |
| Production performance/availability | UNVERIFIED | Local benchmark only | Representative deployment/load/failover |
| Production backup RPO/RTO | UNVERIFIED | Local recovery verification only | Encrypted backup and measured drills |
| Image vulnerability/SBOM/provenance | UNVERIFIED | CI secret and dependency checks | Scanner, registry, signing policy |
| Threat-label accuracy | UNVERIFIED | Synthetic data and deterministic behavior checks | Independently verified labels |

No status in this matrix is a production certification or a maliciousness claim.
