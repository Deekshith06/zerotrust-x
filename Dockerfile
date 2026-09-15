FROM python:3.14-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 appuser
COPY data/processed ./data/processed
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "zerotrust_x.web:app", "--host", "0.0.0.0", "--port", "8000"]
