# Data Quality Baseline v1.0

> Historical report retained for audit lineage. The authoritative frozen baseline is [`docs/data-quality-baseline-v1.md`](data-quality-baseline-v1.md) and `data/baselines/data-quality-v1.json`.

**Pipeline Version:** `v1.0`  
**Baseline Date:** 2026-09-14  
**Pipeline Status:** Historical pre-fix snapshot; superseded by `data-quality-v1`

---

## Executive Summary

The data cleaning, normalization, and quality quarantining pipeline has achieved full deterministic stability across all four Track 2 dataset sources. 

```text
62,430 raw records
        ↓
62,430 normalized events
        ↓
36,220 current quality findings
        ↓
29,536 current affected rows
        ↓
1,473 detections
        ↓
3,000 risk profiles
```

* **Test Suite:** 24 / 24 tests passing
* **Reproducibility:** 100% bit-level deterministic match across independent execution runs (identical Parquet hashes, JSON manifests, and metric summaries).

---

## 1. Input Dataset Hashes & Record Counts

| Dataset File | Format | Record Count | SHA-256 Digest |
| :--- | :--- | ---: | :--- |
| `track2_firewall_logs.csv` | CSV | 30,600 | `b9f3bd0be4bd5121b61c77f80dbcaef7e8f504ca035dbb1328eb9bcf5ec77649` |
| `track2_iam_audit_trail.json` | JSON | 20,500 | `ecff61cf2c351b8c08169fb641a99ef526315266858a74ec49a94bd19c72eef0` |
| `track2_endpoint_alerts.xlsx` | XLSX | 8,240 | `1a64fbb5e3ebfb0a67fa6db6bcfa4fcd8e3dc5ef6b39bfadfbef201cff356f98` |
| `track2_identity_asset_master.csv` | CSV | 3,090 | `50edeb9b80cecfecfaab74cf8f117c2f6d2e057fcdff1712a7dbdf9f0ea1e1eb` |
| **Total Ingested Envelopes** | | **62,430** | |

---

## 2. Ingestion & Affected-Row Summary

Each source record envelope produces exactly one `UnifiedEvent` (1:1 record preserving full lineage and raw payload). Corrupt fields generate structured `QualityIssue` findings in `quarantine.parquet`.

| Source Name | Total Records Ingested | Clean Records (0 Findings) | Affected Rows (≥1 Finding) | Total Quality Findings |
| :--- | ---: | ---: | ---: | ---: |
| `firewall` | 30,600 | 9,062 | 21,538 | 32,842 |
| `iam` | 20,500 | 9,809 | 10,691 | 11,544 |
| `endpoint` | 8,240 | 6,963 | 1,277 | 1,532 |
| `identity` | 3,090 | 3,000 | 90 | 90 |
| **Total** | **62,430** | **28,834** | **33,596** | **46,008** |

> [!IMPORTANT]
> **Separation of Metrics:** Quarantine findings (`46,008`) measure individual field/validation anomalies across the dataset, while affected rows (`33,596`) count distinct raw rows containing at least one anomaly. The average finding density is **1.369 findings per affected row**.

---

## 3. Quarantine Reason-Code Distribution

| Reason Code | Count | Validation Rule & Scope |
| :--- | ---: | :--- |
| `IP_ADDRESS_INVALID` | 19,860 | Octet structure validation (e.g. `999.999.999.999`, 5 octets, hyphens). |
| `BYTES_INVALID` | 9,788 | Non-numeric or unparseable byte string formats in firewall logs. |
| `PORT_OUT_OF_RANGE` | 6,732 | Source or destination port integer outside valid range `0..65535`. |
| `BYTES_OUT_OF_RANGE` | 3,057 | Negative byte transfer counts (`bytes_sent`, `bytes_received`). |
| `RISK_OUT_OF_RANGE` | 2,674 | Risk score value numeric but outside permissible `0..100` range. |
| `DUPLICATE_RECORD` | 1,430 | Primary key collision per source dataset identifier. |
| `RISK_NON_NUMERIC` | 1,384 | Non-numeric severity labels (e.g. `"High"`, `"Critical"`) in numeric risk fields. |
| `HASH_FORMAT_INVALID` | 815 | SHA-256 process checksum not matching exactly 64 hexadecimal characters. |
| `RESOLUTION_BEFORE_DETECTION` | 268 | Alert resolution timestamp occurring chronologically before detection timestamp. |
| **Total Findings** | **46,008** | |

---

## 4. Deduplication Methodology Audit

`DUPLICATE_RECORD` checks are strictly scoped to genuine primary key uniqueness per source dataset:

* `firewall`: Keyed by `log_id` (600 excess duplicate records).
* `iam`: Keyed by `event_id` (500 excess duplicate records).
* `endpoint`: Keyed by `alert_id` (240 excess duplicate records).
* `identity`: Keyed by `user_id` (90 excess duplicate records in the identity master table).

> [!NOTE]
> Repeated user occurrences across events (e.g. multiple login attempts or network sessions for user `EMP10194`) are **NOT** treated as duplicates. `user_id` is only used as a primary key for deduplication within the identity master catalog where each row represents one distinct master identity record.

---

## 5. Normalization & Quarantine Architecture

The pipeline follows a strict **Preserve + Annotate + Quarantine** model rather than destructive deletion:

1. **Raw Preservation:** Original raw string representations and dictionaries are preserved in `payload.raw` and `timestamp_raw`.
2. **Standard Normalization:**
   - **User ID:** Standardized to `EMP` + digits (e.g. `EMP10194`).
   - **Hostnames:** Strips domain suffixes (`.CORP.LOCAL`), uppercase normalization, `-` conversion.
   - **Timestamps:** Multi-format parser handling ISO 8601, day-first slash/dash, Unix epoch, and US month-day AM/PM strings.
   - **Risk Scores & Network Values:** Normalized to canonical integers; invalid values are set to `None` with `quality_status = "normalized"` and annotated with explicit `quality_reason_codes`.
3. **Quality Status:**
   - `clean`: All record fields passed strict validation rules.
   - `normalized`: One or more fields contained malformed data, populated in quarantine with explicit reason codes.

---

## 6. Deterministic Reproducibility Verification

Independent pipeline runs against identical source files produce bit-level matching artifacts:

* `events.parquet`: `0a9c351edc6c9828881ac1fa690ff676928b46696a0ddad7cfd24a2c962ec141`
* `quarantine.parquet`: `3c6d1d2b8b9a4c8e7f1a9e8d7f6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c`
* `detections.parquet`: `694b0ed17b9b8cf4d42c024a753dcc6943fcaa21a1d1fd087350eecbf933b25c`
* `user_risk.parquet`: `038a9671e7e93551e8fe39b56954b6ab7e71c6cf6a8559d1327825c7fade3508`
* `data_quality.json`: `a165aa6e95129a873dc76cbb3d08b559f64fc2a7bea74f527d0807b413b1190f`
* `manifest.json`: `1158c303da43d4d643340765fd9610e3749dce6987308cea8263bbd83a4a9ac0`

---

## 7. Known Baseline Limitations

1. **Synthetic Data Characteristics:** Dataset timestamps and IP addresses contain intentional synthetic noise and missing fields.
2. **Quarantine Retention:** Non-standard fields are preserved in raw JSON payloads and quarantined rather than pruned, maintaining 100% lineage traceability for SOC auditing.

---

**DATA PIPELINE BASELINE v1.0 FROZEN**
