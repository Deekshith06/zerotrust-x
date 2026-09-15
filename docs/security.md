# Security model

ZeroTrust-X is a local operational reference implementation. The raw data is synthetic, and the local authentication adapter is intentionally not production authentication.

## Trust boundaries

Raw telemetry is untrusted input. Parsers validate fields, preserve raw values, and emit quarantine findings. Future agent context must wrap telemetry values in `<telemetry_field>` and never treat their contents as instructions.

The API exposes parameterized artifact queries only. No request can provide SQL, shell commands, or arbitrary filesystem paths. Investigation tools are read-only.

## Authorization

`EMPLOYEE` can read only their own timeline. `SOC_ANALYST` can investigate and inspect relationship graphs. `SOC_ADMIN` can inspect process-local metrics. Sensitive routes fail closed when the local compatibility header is missing or invalid.

Replace `X-Demo-Token` with a configured OIDC/JWKS provider before deployment. Add secure sessions, CSRF controls for browser mutations, tenant isolation, secret management, rate limiting, and production audit retention.

## Limitations

The project does not claim production readiness. It has no external identity provider, no distributed audit sink, no verified threat labels, and no destructive response actions. These limitations are intentional and documented.
