# Testing strategy

Current gates:

```bash
.venv/bin/ruff check src tests
.venv/bin/pytest -q
.venv/bin/python -m zerotrust_x.cli ingest --input-dir track2_cybersecurity_dataset_files --output-dir data/processed --quarantine-dir data/quarantine
.venv/bin/python scripts/benchmark_local.py --input-dir track2_cybersecurity_dataset_files --work-dir /tmp/zerotrust-x-benchmark
```

Tests cover normalization, malformed network/risk values, deterministic detection/risk, real-data ingestion, grounding and telemetry boundaries, RBAC, employee scope, graph/API routes, manifest/readiness behavior, dashboard contracts, strict artifact-contract failure matrices, tenant-store scope, and local recovery-bundle verification.

`requirements.lock` records the dependency versions used by the verified Python 3.14 environment; CI checks installed versions against it. The local benchmark is bounded and informational: it measures representative requests on a disposable artifact set and is not a production SLO or enterprise-scale performance claim.

Required deployment suites remain: OIDC/JWKS integration, signed connector replay protection, distributed rate limiting, image vulnerability scanning, production-scale load tests, encrypted backup/restore drills, and browser E2E against a real identity provider. These remain unverified until executed in their target environment.
