# Quarantine-quality report

**Review date:** 2026-09-14  
**Input:** supplied Track 2 raw files  
**Method:** independent read of generated `quarantine.parquet`, `events.parquet`, and source row totals.

## Verified totals

The original pre-fix audit baseline and the current post-fix baseline are both retained below. The post-fix figures are the values currently emitted by `src/zerotrust_x/pipeline.py`.

| Metric | Historical pre-fix baseline | Current post-fix baseline |
|---|---:|---:|
| Input records | 62,430 | 62,430 |
| Persisted event rows | 62,430 | 62,430 |
| Quarantine findings | 46,008 | 36,220 |
| Unique affected source rows | 33,596 | 29,536 |
| Findings per affected source row | 1.3694 | 1.2263 |
| Duplicate findings | 1,430 | 1,430 |
| Non-duplicate affected source rows | 32,862 | 28,106 |
| Maximum findings for one source row | 6 | 6 |

Both values are **finding counts**, not counts of rejected records. The pipeline persists every source row as an event and records quality findings alongside it. A claim that either total represents rejected records would be false.

### Current post-fix rule totals

| Rule | Findings |
|---|---:|
| IP_ADDRESS_INVALID | 19,860 |
| PORT_OUT_OF_RANGE | 6,732 |
| BYTES_OUT_OF_RANGE | 3,057 |
| RISK_OUT_OF_RANGE | 2,674 |
| DUPLICATE_RECORD | 1,430 |
| RISK_NON_NUMERIC | 1,384 |
| HASH_FORMAT_INVALID | 815 |
| RESOLUTION_BEFORE_DETECTION | 268 |
| **Total** | **36,220** |

## Findings per record

| Findings on one source row | Number of rows |
|---:|---:|
| 1 | 23,287 |
| 2 | 8,425 |
| 3 | 1,675 |
| 4 | 200 |
| 5 | 8 |
| 6 | 1 |

Multiple findings are not automatically duplicates: a row can independently contain malformed IP, bytes, port, risk, hash, and chronology values. The current schema retains one row per field/rule finding, allowing those defects to be distinguished. The report should show both affected-record counts and finding counts.

The current pipeline also emits `classification_counts`: 34,790 `VALID_AND_UNRECOVERABLE` findings and 1,430 `DUPLICATE_FINDING` findings. The historical report's 9,788 `VALID_AND_RECOVERABLE` byte values are preserved as a pre-fix review record; they do not appear as current findings after the parser change.

## Source rates

| Source | Input | Findings | Affected rows | Affected-row rate | Findings / affected row |
|---|---:|---:|---:|---:|---:|
| firewall | 30,600 | 32,070 | 21,538 | 70.3856% | 1.4890 |
| iam | 20,500 | 12,525 | 10,691 | 52.1512% | 1.1715 |
| endpoint | 8,240 | 1,323 | 1,277 | 15.4976% | 1.0360 |
| identity | 3,090 | 90 | 90 | 2.9126% | 1.0000 |
| **overall** | **62,430** | **46,008** | **33,596** | **53.8139%** | **1.3694** |

## Findings by rule

| Rule | Findings |
|---|---:|
| IP_ADDRESS_INVALID | 19,860 |
| BYTES_INVALID | 9,788 |
| PORT_OUT_OF_RANGE | 6,732 |
| BYTES_OUT_OF_RANGE | 3,057 |
| RISK_OUT_OF_RANGE | 2,674 |
| DUPLICATE_RECORD | 1,430 |
| RISK_NON_NUMERIC | 1,384 |
| HASH_FORMAT_INVALID | 815 |
| RESOLUTION_BEFORE_DETECTION | 268 |

## Interpretation

- The largest source-specific problem is malformed firewall/network data, especially invalid IP and bytes values.
- Findings can cascade in the presentation sense when one record contains several independent bad fields, but the current implementation does not emit fabricated dependency rules: every row comes from a field-specific parser or duplicate-ID check.
- “Recoverable” versus “unrecoverable” is not currently modeled. Values such as malformed ports and hashes are preserved in raw payloads but normalized fields become null; no automatic repair is claimed.
- The pipeline does not reject bad rows from persistence. It emits normalized events with quality status and writes findings to quarantine. This is an explicit preserve-and-quarantine policy.
- Ground truth for whether source anomalies are intentional, recoverable, or operationally harmful is unavailable.
