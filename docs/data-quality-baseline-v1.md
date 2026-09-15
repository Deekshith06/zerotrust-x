# ZeroTrust-X Data Quality Baseline v1

**Dataset version:** `data-quality-v1`  
**Created:** 2026-09-14  
**Status:** `CLEAN_WITH_DOCUMENTED_EXCEPTIONS`  
**Freeze policy:** Downstream systems consume this baseline as-is. Changes to cleaning rules or baseline metrics require a new dataset and pipeline version.

## Frozen metrics

| Metric | Value |
|---|---:|
| Raw records | 62,430 |
| Normalized events | 62,430 |
| Quality findings | 36,220 |
| Affected source rows | 29,536 |
| Duplicate findings | 1,430 |
| Detections | 1,473 |
| Risk identities | 3,000 |
| Tests | 24 passed |

Findings are field-level quality observations, not rejected records. Every source row remains represented in the normalized event artifact.

## Frozen source hashes

| Source | SHA-256 |
|---|---|
| `track2_dataset_notes.txt` | `f52b4a5dead99547c6270f3f76ea0a15c6ffb1b258e4fafe6d9c7c2702143ce3` |
| `track2_endpoint_alerts.xlsx` | `cd43513e3e6d3ed7ada3e6db884aaf5e2167668041e5d492ace799fa2a5e9f92` |
| `track2_firewall_logs.csv` | `1a2833a93832d53dd6c5e1204769bf1a72b0d5069d7ba17508fa6f11e381608c` |
| `track2_iam_audit_trail.json` | `316acf81d46734caa9fc8d9fe3c9794d9ae5aa6bc29782e2028a655b344fc687` |
| `track2_identity_asset_master.csv` | `b5a70c3d4936857d8210fe098adcda78819d9e7465bdf8e635c5475ce1fab117` |

## Rule and pipeline versions

- Pipeline version: `0.1.0`
- Normalization rule version: `normalize-2026-09-14-v2`
- Baseline version: `data-quality-v1`
- Quality classifications: `DUPLICATE_FINDING`, `VALID_AND_UNRECOVERABLE`

Current findings remain quarantined with raw values, raw payloads, source provenance, record hashes, iteration IDs, rule versions, and reason codes. No malformed value was silently deleted, guessed, or replaced with an ambiguous repair.

## Known exceptions

- Invalid IP addresses
- Ports outside `0..65535`
- Negative byte counts
- Risk values outside `0..100`
- Non-numeric risk labels
- Invalid endpoint SHA-256 values
- Endpoint resolution timestamps earlier than detection timestamps
- Duplicate source identifiers

These exceptions are retained for evidence and must not be treated as proof of malicious behavior. The source data is synthetic and has no verified incident ground truth.

## Downstream contract

Entity resolution, unified-event consumers, correlation, deterministic detection, risk scoring, and investigation must reference `data-quality-v1` and must not modify raw sources, normalized artifacts, or quarantine findings. Any change affecting a frozen metric requires a new baseline version, updated hashes, regression evidence, and an explicit migration note.
