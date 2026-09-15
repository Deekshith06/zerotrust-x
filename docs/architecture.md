# Architecture

ZeroTrust-X is a modular monolith with a deterministic evidence pipeline and a read-only analyst console.

```text
CSV / JSON / XLSX
       ↓
source adapters → validation / normalization → provenance + quarantine
       ↓
canonical event artifacts (Parquet)
       ↓
deterministic rules → detections → explainable risk register
       ↓
FastAPI read-only queries → typed filtering/query service → industrial SOC dashboard
       ↓
grounded investigation state / optional LangGraph adapter → human analyst
```

The current local store is immutable Parquet output plus JSON quality/manifest files. This is appropriate for synthetic local operations and is not a substitute for a tenant-aware operational database or event lake at enterprise scale.

## Trust boundaries

- Raw files and telemetry fields are untrusted.
- API requests are untrusted until authenticated and authorized.
- Investigation tools are parameterized and read-only.
- The model, when optionally configured, cannot define detections or risk scores.
