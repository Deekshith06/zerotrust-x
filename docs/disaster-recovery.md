# Disaster recovery

The local demonstration stores source files, generated Parquet artifacts, quality JSON, manifest JSON, and local audit JSONL. Back up source data and generated artifacts together so manifests remain meaningful.

The repository provides a local recovery verification command:

```bash
.venv/bin/python -m zerotrust_x.cli verify-recovery \
  --input-dir track2_cybersecurity_dataset_files \
  --processed-dir data/processed \
  --quarantine-dir data/quarantine \
  --destination /tmp/zerotrust-x-restore
```

It copies to a new destination, verifies the v2 artifact contract, compares declared source hashes, and rejects existing or corrupted bundles. This is local integrity evidence only; it does not provide immutable retention or production backup protection.

Production backup target: encrypted versioned object storage plus an external immutable audit sink. Restore procedure: provision a clean environment, restore source/artifact bundle, verify SHA-256 manifest, run readiness checks, then perform route and authorization smoke tests.

RPO: **not measured for production**.
RTO: **not measured for production**.

No production recovery guarantee is claimed until encrypted versioned backup, restore, corruption, and failover drills are executed in the target environment.
