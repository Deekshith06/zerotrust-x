# Track 2 Dataset Findings

**Inspection date:** 2026-09-14  
**Status:** Initial read-only inventory complete  
**Dataset status:** Synthetic educational telemetry; not evidence of malicious intent.

## Available files

| File | Records | Columns / keys | Initial status |
|---|---:|---|---|
| `track2_firewall_logs.csv` | 30,600 | 15 columns; 30,000 distinct `log_id` values | Available; duplicates and malformed network values present |
| `track2_iam_audit_trail.json` | 20,500 | 15 keys; 20,000 distinct `event_id` values | Available; duplicates, malformed IPs/risk values, and missing fields present |
| `track2_endpoint_alerts.xlsx` | 8,240 | 15 columns; 8,000 distinct `alert_id` values | Available; duplicate IDs, timestamp inconsistencies, and missing fields present |
| `track2_identity_asset_master.csv` | 3,090 | 12 columns; 3,000 distinct `user_id` values | Available; duplicate records and missing asset attributes present |
| `track2_dataset_notes.txt` | 61 lines | Dataset guidance | Available |

## Firewall observations

- 600 exact duplicate rows / duplicate groups; 600 excess `log_id` records.
- Missing-ish values include: `timestamp` 3,598 (11.76%), `hostname` 1,799 (5.88%), `src_ip` 3,670 (11.99%), `dst_ip` 3,550 (11.60%), `src_port` 3,958 (12.93%), `dst_port` 4,079 (13.33%), `bytes_sent` 3,615 (11.81%), `bytes_received` 3,654 (11.94%), `session_id` 4,602 (15.04%), and `rule_name` 9,195 (30.05%).
- Timestamp families include ISO, day-first slash, day-first dash/text, Unix epoch, month-name text, and year-first slash formats.
- Invalid non-empty IP values: `src_ip` 11,893 (38.87%); `dst_ip` 11,249 (36.76%). Observed examples include incomplete octets, five-octet values, hyphenated values, and `999.999.999.999`.
- Invalid ports: source 3,383; destination 3,349. Observed negatives and values above 65,535.
- `protocol` has 12 variants, `action` has 13, and `threat_flag` has 8; explicit categorical mappings are required.

## IAM observations

- 500 exact duplicate groups / excess records; 20,000 distinct `event_id` values.
- Missing-ish values: `timestamp` 2,465 (12.02%), `username` 868 (4.23%), `department` 5,758 (28.09%), `source_ip` 2,408 (11.75%), `hostname` 1,201 (5.86%), `device_id` 3,612 (17.62%), `session_id` 8,677 (42.33%), `mfa_passed` 4,933 (24.06%), `failure_reason` 15,523 (75.72%), `risk_score` 1,177 (5.74%), and `geo_location` 5,133 (25.04%).
- Timestamp families include ISO, day-first slash/dash, month-name text, and Unix epoch formats.
- Invalid source IP values: 7,967 (38.86%).
- Invalid risk values: 4,058 (19.80%). Values include textual severity labels, negatives, and values above 100. These must not be silently clamped or interpreted as numeric risk.
- `event_type` has 22 variants and requires explicit normalization to canonical categories.

## Endpoint observations

- Sheet: `endpoint_alerts`; 8,240 records and 15 columns.
- 240 excess duplicate `alert_id` records; duplicated IDs may not be exact duplicate rows.
- Missing-ish values: `detected_timestamp` 1,006 (12.21%), `resolved_timestamp` 2,405 (29.19%), `hostname` 503 (6.10%), `file_path` 1,675 (20.33%), `process_name` 1,495 (18.14%), `sha256` 1,484 (18.01%), `assigned_to` 3,138 (38.08%), and `device_criticality` 1,299 (15.76%).
- Detected and resolved timestamps use multiple formats, including US month-day AM/PM values.
- At least 236 rows have a parsed `resolved_timestamp` earlier than `detected_timestamp`; preserve both raw values and quarantine or flag the temporal inconsistency.
- A limited parser left 1,761 timestamp values unparsed; the implementation must support the observed US month-day AM/PM formats.
- User and categorical fields were not missing-ish in the initial profile.

## Identity / asset observations

- 90 excess duplicate records / duplicate groups; 3,000 distinct canonical `user_id` values.
- Missing-ish values: `username` 125 (4.05%), `location` 574 (18.58%), `hostname` 174 (5.63%), `device_id` 583 (18.87%), `hire_date` 337 (10.91%), `termination_date` 2,712 (87.77%) under broad sentinel handling, and `manager_username` 897 (29.03%).
- Hire dates use ISO, day-first slash, dash/text, Unix epoch, year-first slash, and other text formats.
- Canonicalization must handle variants such as `EMP 10194`, bare numeric IDs, and device values such as `dev 11850` without unsafe fuzzy matching.

## Canonical join coverage

Canonicalization used `EMP` + digits for user IDs and uppercase hostnames with `_` → `-` plus `.CORP.LOCAL` removal.

| Join | Left keys | Right keys | Overlap |
|---|---:|---:|---:|
| IAM user ↔ identity user | 2,983 | 3,000 | 2,983 |
| Endpoint user ↔ identity user | 2,799 | 3,000 | 2,799 |
| Endpoint hostname ↔ identity hostname | 2,759 | 2,829 | 2,599 |
| Firewall hostname ↔ identity hostname | 3,000 | 2,829 | 2,829 |

These are distinct canonical key sets, not row-level match rates. Raw-format joins will under-match. Every entity match must retain `match_method`, `match_confidence`, and source references.

## Initial implementation decisions

1. Use a modular monolith with FastAPI and a small server-rendered dashboard.
2. Keep raw files immutable.
3. Write processed events to Parquet and maintain a local analytical/query store for the API.
4. Preserve raw values and normalization metadata wherever practical.
5. Treat duplicate records as a data-quality condition; deduplicate only through deterministic source identifiers and retain lineage.
6. Quarantine invalid fields/records with explicit reason codes instead of dropping them.
7. Defer LangGraph, anomaly ML, and advanced UI until the deterministic P0 pipeline is green.
8. Use the actual dataset schema as authoritative; do not invent absent fields.

## Initial reason-code candidates

```text
DUPLICATE_RECORD
MISSING_REQUIRED_TIMESTAMP
TIMESTAMP_UNPARSED
TIMEZONE_UNCERTAIN
IP_OCTET_COUNT_INVALID
IP_ADDRESS_INVALID
PORT_OUT_OF_RANGE
RISK_OUT_OF_RANGE
RISK_NON_NUMERIC
HASH_FORMAT_INVALID
RESOLUTION_BEFORE_DETECTION
UNKNOWN_REFERENCE
AMBIGUOUS_ENTITY_MATCH
```

## Next work

Write tests for user-ID normalization, timestamp parsing, IP/port validation, risk-score parsing, duplicate lineage, and quarantine behavior. Then implement the smallest reproducible ingestion → cleaning → unified-event pipeline.
