# Agent safety

The LLM is optional and never detects threats or assigns risk. It receives bounded, read-only evidence and may summarize only evidence returned by tools.

Controls:

- telemetry is untrusted data, not instructions;
- citations are validated against returned IDs;
- unsupported citations reject the report;
- tools do not expose arbitrary SQL, shell, filesystem, or network execution;
- no destructive action tools exist;
- recommendations require human review;
- malicious intent is never inferred from synthetic telemetry alone.

OIDC, tenant-aware durable state, model-provider controls, and external agent-run retention remain unverified integrations.