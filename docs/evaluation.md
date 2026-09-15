# Evaluation and reproducibility

ZeroTrust-X uses synthetic Track 2 telemetry and has no verified incident ground truth. Results must therefore be reported as deterministic behavior checks, not threat-detection accuracy claims.

## Deterministic acceptance checks

- Ingestion produces 62,430 unified event rows.
- Ingestion produces 1,473 deterministic detections.
- The risk register contains 3,000 identities.
- The authoritative disposable post-reader-fix run contains 36,220 quarantine findings affecting 29,536 source rows; the earlier pre-fix audit baseline was 46,008 findings affecting 33,596 rows. These are findings, not rejected records. The checked-in `data/processed/data_quality.json` is stale at 35,952/29,298 and must not override the immutable baseline; regenerate checked-in outputs only through the versioned ingestion process.
- The canonical event schema is `unified-event-v2`: parsed department, ports, byte counts, endpoint hash, status, location, country, and threat flag are typed event fields while raw values remain in provenance payloads.
- A second ingestion produces the same artifact manifest.
- Raw input hashes remain unchanged.
- Invalid values retain source path, source row, source record ID, raw value and payload, raw-record SHA-256, iteration ID, rule version, classification, and reason code.
- Investigation citations are accepted only when IDs exist in collected evidence.

## Detection and anomaly semantics

Rules identify observed patterns such as repeated authentication failures, MFA failures, endpoint alerts, and denied network actions. Risk is a bounded, explainable score derived from those signals. The baseline anomaly route ranks event-count deviation from the median; it is not a trained model and does not prove compromise or intent.

## Reproducibility

`data/processed/manifest.json` records pipeline version, source SHA-256 values, output artifact hashes, and quality counts. Evaluation and artifact-consuming API paths require a valid manifest schema 2 contract with `unified-event-v2`, required output hashes, Parquet schemas, and consistent quality counts. The checked-in legacy `data/processed` set is intentionally not a valid readiness input. Compare manifests from two clean runs before treating a result as reproducible.
