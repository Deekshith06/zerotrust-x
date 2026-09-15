"""Explicit environment configuration and production safety gates."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    environment: str = "demo"
    input_dir: Path = Path("track2_cybersecurity_dataset_files")
    processed_dir: Path = Path("data/processed")
    quarantine_dir: Path = Path("data/quarantine")
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    tenant_id: str = "TENANT_LOCAL"
    cors_origins: tuple[str, ...] = ()
    rate_limit_per_minute: int = 120
    max_query_limit: int = 1000
    audit_path: Path = Path("data/audit.jsonl")

    @property
    def production_mode(self) -> bool:
        return self.environment.casefold() in {"production", "staging"}

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.production_mode and not self.oidc_issuer:
            errors.append("OIDC_ISSUER is required outside demo mode")
        if self.production_mode and not self.oidc_audience:
            errors.append("OIDC_AUDIENCE is required outside demo mode")
        if self.rate_limit_per_minute < 1:
            errors.append("RATE_LIMIT_PER_MINUTE must be positive")
        if self.max_query_limit < 1 or self.max_query_limit > 10_000:
            errors.append("MAX_QUERY_LIMIT must be between 1 and 10000")
        if self.production_mode and not self.cors_origins:
            errors.append("ZEROTRUST_CORS_ORIGINS is required outside demo mode")
        return errors


def load_settings() -> Settings:
    origins = tuple(item.strip() for item in os.getenv("ZEROTRUST_CORS_ORIGINS", "").split(",") if item.strip())
    settings = Settings(
        environment=os.getenv("ZEROTRUST_ENV", "demo"),
        input_dir=Path(os.getenv("ZEROTRUST_INPUT_DIR", "track2_cybersecurity_dataset_files")),
        processed_dir=Path(os.getenv("ZEROTRUST_PROCESSED_DIR", "data/processed")),
        quarantine_dir=Path(os.getenv("ZEROTRUST_QUARANTINE_DIR", "data/quarantine")),
        oidc_issuer=os.getenv("OIDC_ISSUER"),
        oidc_audience=os.getenv("OIDC_AUDIENCE"),
        tenant_id=os.getenv("ZEROTRUST_TENANT_ID", "TENANT_LOCAL"),
        cors_origins=origins,
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "120")),
        max_query_limit=int(os.getenv("MAX_QUERY_LIMIT", "1000")),
        audit_path=Path(os.getenv("ZEROTRUST_AUDIT_PATH", "data/audit.jsonl")),
    )
    errors = settings.validate()
    if errors:
        raise RuntimeError("Invalid ZeroTrust-X configuration: " + "; ".join(errors))
    return settings
