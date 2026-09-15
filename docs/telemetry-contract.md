# Telemetry contract

Canonical event fields include `event_id`, `source`, `source_row`, `source_record_id`, `raw_record_sha256`, `event_type`, `event_time`/`timestamp`, `user_id`, entity fields, normalized action/protocol, quality status, reason codes, and raw payload provenance.

Production adapters should additionally provide `tenant_id`, `connector_id`, `ingestion_id`, `received_at`, and `schema_version`. These fields are integration requirements and are not fabricated for the current synthetic source files.

Adapters must validate payload size, authentication/signature, source identifiers, timestamps, idempotency, and schema before canonicalization. Invalid records are quarantined with raw value and source reference.