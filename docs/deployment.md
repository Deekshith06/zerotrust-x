# Deployment

## Local

```bash
.venv/bin/python -m zerotrust_x.cli ingest \
  --input-dir track2_cybersecurity_dataset_files \
  --output-dir data/processed \
  --quarantine-dir data/quarantine
.venv/bin/python -m uvicorn zerotrust_x.web:app --host 127.0.0.1 --port 8000
```

## Container

`Dockerfile` and `docker-compose.yml` provide a non-root, read-only dashboard image using prebuilt artifacts. Ingestion should run as a separate controlled job before starting the app. Do not bake secrets into images.

## Production prerequisites

Before production use, configure a real OIDC provider, TLS at the deployment boundary, tenant-aware durable storage, external immutable audit retention, a distributed rate-limit backend, secret injection, resource limits, image/dependency scanning, and tested backup/restore. These controls are not claimed merely because the local container starts.