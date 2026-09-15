FROM python:3.14-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md ./
COPY src ./src
COPY track2_cybersecurity_dataset_files ./track2_cybersecurity_dataset_files
COPY data/baselines ./data/baselines

RUN pip install --no-cache-dir . \
    && python -m zerotrust_x.cli ingest \
        --input-dir track2_cybersecurity_dataset_files \
        --output-dir data/processed \
        --quarantine-dir data/quarantine \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn zerotrust_x.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
