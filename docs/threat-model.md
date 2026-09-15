# Threat model

ZeroTrust-X treats all telemetry as untrusted data. The following is a local threat model, not a certification.

| Threat | Preconditions / path | Impact | Existing control | Missing / next control | Test |
|---|---|---|---|---|---|
| Unauthenticated API access | Request protected route without token | Evidence disclosure | Fail-closed local compatibility authentication | OIDC middleware | Missing-token tests |
| IDOR / scope escape | Employee requests another user timeline | PII/evidence disclosure | `can_read_user` self-scope | Durable tenant/resource authorization | Employee cross-user test |
| Cross-tenant access | Tenant claim differs from resource | Tenant data disclosure | `TenantContext` contract | Tenant-aware persistent store and fixtures | Cross-tenant repository test |
| Malicious telemetry | Log contains instruction-like text | Agent manipulation | Boundary escaping and citation validation | Isolated model context and adversarial suite | Prompt-injection test |
| Poisoned values | Invalid IP/risk/hash/timestamp | False correlation or score | Validation and quarantine | Connector signatures and provenance policy | Quality reason-code tests |
| Replay/duplicates | Re-submit source event | Inflated detections | Source/event duplicate handling | Signed ingestion, idempotency store | Replay test planned |
| Resource exhaustion | Oversized or expensive query | Availability loss | Query bounds and bounded graph | Distributed rate limiter and request size middleware | Load test unverified |
| Audit tampering | User modifies local audit file | Accountability loss | Append-only application writer | External immutable retention | File-permission/retention integration |
| Prompt overreach | Agent invents unsupported conclusion | Incorrect response | Deterministic detector and grounded validator | Human review and critic loop | Unsupported citation test |
| Supply-chain compromise | Vulnerable dependency/image | Code or data compromise | Minimal dependency set and lint/tests | Lockfile, SCA, signed image scanning | CI security scan |
| Privacy leakage | Dashboard exposes unnecessary identifiers | Employee privacy harm | Role-scoped routes and synthetic data | Minimization/retention policy and redaction | Output review |

## Security principles

- Authentication is not authorization.
- Every durable resource must carry tenant context.
- The AI agent is read-only and never the source of truth for telemetry or risk.
- Consequential actions require explicit human approval and a separate audited executor.
- “Suspicious activity detected” is acceptable; claims of malicious intent require independent evidence.
