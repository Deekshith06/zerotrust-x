"""Safe typed query functions over immutable Parquet artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl

from zerotrust_x.filters import PRIMARY_KEYS, FilterSpec, compile_filters


class ArtifactQueryError(RuntimeError):
    """Base error for a query that cannot safely read an artifact."""


class ArtifactMissingError(ArtifactQueryError):
    """The requested artifact is not available."""


class ArtifactMalformedError(ArtifactQueryError):
    """The artifact cannot be decoded as a valid Parquet dataset."""


class ArtifactSchemaError(ArtifactQueryError):
    """The artifact does not satisfy the expected query schema."""


def _json_safe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: (list(value) if isinstance(value, (list, tuple)) else value) for key, value in row.items()}
        for row in rows
    ]


class ArtifactQuery:
    def __init__(self, directory: Path):
        self.directory = directory

    def _read(self, name: str) -> pl.DataFrame:
        path = self.directory / name
        if not path.exists():
            return pl.DataFrame()
        try:
            return pl.read_parquet(path)
        except (OSError, pl.exceptions.PolarsError) as exc:
            raise ArtifactMalformedError from exc

    def query(self, spec: FilterSpec, scope_user_id: str | None = None) -> dict[str, Any]:
        name = f"{spec.dataset.value}.parquet"
        path = self.directory / name
        if not path.exists():
            raise ArtifactMissingError
        try:
            lazy = pl.scan_parquet(path)
            schema = set(lazy.collect_schema().names())
        except (OSError, pl.exceptions.PolarsError) as exc:
            raise ArtifactMalformedError from exc
        try:
            expression = compile_filters(spec, schema)
        except ValueError as exc:
            raise ArtifactSchemaError(str(exc)) from exc
        if scope_user_id is not None:
            if "user_id" not in schema:
                raise ArtifactSchemaError("artifact has no user scope")
            expression = expression & (pl.col("user_id") == scope_user_id)
        filtered = lazy.filter(expression)
        sort_by = spec.sort_by or PRIMARY_KEYS[spec.dataset]
        if sort_by not in schema:
            raise ArtifactSchemaError("artifact is missing sort field")
        tie_breaker = PRIMARY_KEYS[spec.dataset]
        if tie_breaker not in schema:
            raise ArtifactSchemaError("artifact is missing primary key")
        sort_fields = [sort_by] if sort_by == tie_breaker else [sort_by, tie_breaker]
        try:
            total = filtered.select(pl.len()).collect().item()
            page = (
                filtered.sort(sort_fields, descending=[spec.descending] * len(sort_fields), nulls_last=True)
                .slice(spec.offset, spec.limit)
                .collect()
            )
        except (OSError, pl.exceptions.PolarsError, TypeError) as exc:
            raise ArtifactMalformedError from exc
        return {
            "items": _json_safe_rows(page.to_dicts()),
            "filtered_count": total,
            "offset": spec.offset,
            "limit": spec.limit,
            "has_more": spec.offset + page.height < total,
            "sort": {"by": sort_by, "descending": spec.descending, "nulls_last": True},
            "filters": json.loads(spec.as_json()),
        }

    def user_risk(self, user_id: str) -> dict[str, Any] | None:
        rows = self._read("user_risk.parquet").filter(pl.col("user_id") == user_id).to_dicts()
        return rows[0] if rows else None

    def events_for_user(self, user_id: str, limit: int = 500) -> list[dict[str, Any]]:
        frame = self._read("events.parquet").filter(pl.col("user_id") == user_id)
        if "timestamp" in frame.columns:
            frame = frame.sort(["timestamp", "event_id"])
        return frame.head(limit).to_dicts()

    def detections_for_user(self, user_id: str) -> list[dict[str, Any]]:
        return self._read("detections.parquet").filter(pl.col("user_id") == user_id).to_dicts()

    def relationships(self, user_id: str) -> dict[str, list[str]]:
        events = self.events_for_user(user_id)
        return {
            "devices": sorted({str(r["device_id"]) for r in events if r.get("device_id")}),
            "hostnames": sorted({str(r["hostname"]) for r in events if r.get("hostname")}),
            "source_ips": sorted({str(r["source_ip"]) for r in events if r.get("source_ip")}),
            "destinations": sorted({str(r["destination_ip"]) for r in events if r.get("destination_ip")}),
            "sessions": sorted({str(r["session_id"]) for r in events if r.get("session_id")}),
        }
