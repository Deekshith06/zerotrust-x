# Operations

## Local startup

1. Install `.venv` dependencies.
2. Run ingestion.
3. Start Uvicorn.
4. Check `/health` and `/ready`.
5. Review `data/processed/manifest.json`.

## Monitoring

The local metrics route exposes process-local observations only. Production operations require durable request, ingestion, detection, investigation, and connector metrics with sensitive fields minimized.

## Incident response

Preserve raw source files, manifest, quarantine output, audit records, and application logs. Do not modify source data during investigation. Export an evidence bundle with hashes and access audit. Human analysts remain responsible for consequential actions.