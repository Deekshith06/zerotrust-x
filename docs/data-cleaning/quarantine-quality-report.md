# Phase 7 — Quarantine & Quality Metrics Report

**Report Version:** `1.1.0`  
**Execution Date:** 2026-09-14  
**Dataset Cleaning Iterations Executed:** 2 (historical report; independently re-verified on 2026-09-14)

---

## 1. Executive Summary

During the iterative data cleaning loop starting from raw files, false-positive analysis revealed that **9,788** quarantine findings under `BYTES_INVALID` were false positives caused by strict integer parsing failing on valid size-suffixed quantities (`38805.48 KB`, `43.63 MB`).

By updating the `parse_bytes` normalization rule to support standard data unit suffixes (`B`, `KB`, `MB`, `GB`, `TB`), **9,788 false-positive findings were eliminated**, reducing total quarantine findings from `46,008` to **`36,220`** and affected raw rows from `33,596` to **`29,536`**.

---

## 2. Quantitative Summary

| Metric | Raw Ingestion Baseline | Post-Iteration 2 Clean Baseline | Change |
| :--- | ---: | ---: | :--- |
| **Total Ingested Envelopes** | 62,430 | 62,430 | 0 (100% Preserved) |
| **Normalized Event Rows Output** | 62,430 | 62,430 | 0 (100% Preserved) |
| **Clean Records (0 Findings)** | 28,834 | 32,894 | +4,060 clean rows |
| **Affected Raw Rows (≥1 Finding)** | 33,596 | 29,536 | -4,060 affected rows |
| **Total Quarantine Findings** | 46,008 | 36,220 | -9,788 false-positive findings |
| **Duplicate Record Findings** | 1,430 | 1,430 | 0 (Unchanged) |
| **Threat Detections Generated** | 1,473 | 1,473 | 0 (Unchanged) |
| **Risk-Ranked User Identities** | 3,000 | 3,000 | 0 (Unchanged) |
| **Finding Density (Findings / Affected Row)** | 1.3694 | 1.2263 | -0.1431 |

---

## 3. Quarantine Reason Code Distribution

| Reason Code | Initial Count | Post-Fix Count | False Positives Eliminated | Finding Classification |
| :--- | ---: | ---: | ---: | :--- |
| `IP_ADDRESS_INVALID` | 19,860 | 19,860 | 0 | `VALID_AND_UNRECOVERABLE` |
| `BYTES_INVALID` | 9,788 | 0 | -9,788 | `FALSE_POSITIVE_RULE` (Fixed) |
| `PORT_OUT_OF_RANGE` | 6,732 | 6,732 | 0 | `VALID_AND_UNRECOVERABLE` |
| `BYTES_OUT_OF_RANGE` | 3,057 | 3,057 | 0 | `VALID_AND_UNRECOVERABLE` |
| `RISK_OUT_OF_RANGE` | 2,674 | 2,674 | 0 | `VALID_AND_UNRECOVERABLE` |
| `DUPLICATE_RECORD` | 1,430 | 1,430 | 0 | `DUPLICATE_FINDING` |
| `RISK_NON_NUMERIC` | 1,384 | 1,384 | 0 | `VALID_AND_UNRECOVERABLE` |
| `HASH_FORMAT_INVALID` | 815 | 815 | 0 | `VALID_AND_UNRECOVERABLE` |
| `RESOLUTION_BEFORE_DETECTION` | 268 | 268 | 0 | `VALID_AND_UNRECOVERABLE` |
| **Total Quarantine Findings** | **46,008** | **36,220** | **-9,788** | |

---

## 4. Source-Specific Affected Row Distribution

| Source Name | Ingested Records | Affected Rows (Initial) | Affected Rows (Post-Fix) | Clean Row Percentage |
| :--- | ---: | ---: | ---: | ---: |
| `firewall` | 30,600 | 21,538 | 17,478 | 42.9% |
| `iam` | 20,500 | 10,691 | 10,691 | 47.8% |
| `endpoint` | 8,240 | 1,277 | 1,277 | 84.5% |
| `identity` | 3,090 | 90 | 90 | 97.1% |
| **Total** | **62,430** | **33,596** | **29,536** | **52.7%** |

---

## 5. Summary Classification Matrix

* **`VALID_AND_UNRECOVERABLE`:** `34,790` findings (malformed octets, negative ports/bytes, non-numeric risk scores, invalid SHA-256 length, resolution timestamp precedes detection).
* **`VALID_AND_RECOVERABLE`:** `9,788` unit-suffixed byte values deterministically converted to integer bytes.
* **`FALSE_POSITIVE_RULE`:** `0` remaining (rule fixed in `parse_bytes`).
* **`DUPLICATE_FINDING`:** `1,430` primary key collisions per source.
