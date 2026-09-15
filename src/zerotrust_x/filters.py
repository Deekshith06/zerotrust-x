"""Canonical, bounded filter contract for immutable SOC artifacts."""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import polars as pl


class Dataset(StrEnum):
    EVENTS = "events"
    DETECTIONS = "detections"
    USER_RISK = "user_risk"


@dataclass(frozen=True)
class FieldSpec:
    kind: str
    operators: frozenset[str]
    sortable: bool = True


FIELD_REGISTRY: dict[Dataset, dict[str, FieldSpec]] = {
    Dataset.EVENTS: {
        "event_id": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "source": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "source_path": FieldSpec("string", frozenset({"eq", "in"})),
        "source_record_id": FieldSpec("string", frozenset({"eq", "in"})),
        "event_type": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "timestamp": FieldSpec("timestamp", frozenset({"eq", "gte", "lte", "in"})),
        "user_id": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "hostname": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "device_id": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "session_id": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "source_ip": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "destination_ip": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "src_port": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
        "dst_port": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
        "protocol": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "action": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "bytes_sent": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
        "bytes_received": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
        "department": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "severity": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "status": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "risk_score": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
        "quality_status": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "geo_country": FieldSpec("string", frozenset({"eq", "neq", "in"})),
    },
    Dataset.DETECTIONS: {
        "detection_id": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "user_id": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "rule_code": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "severity": FieldSpec("string", frozenset({"eq", "neq", "in"})),
    },
    Dataset.USER_RISK: {
        "user_id": FieldSpec("string", frozenset({"eq", "neq", "in", "contains"})),
        "risk_level": FieldSpec("string", frozenset({"eq", "neq", "in"})),
        "risk_score": FieldSpec("number", frozenset({"eq", "gte", "lte"})),
    },
}

PRIMARY_KEYS = {
    Dataset.EVENTS: "event_id",
    Dataset.DETECTIONS: "detection_id",
    Dataset.USER_RISK: "user_id",
}
MAX_CLAUSES = 12
MAX_VALUES = 25
MAX_STRING = 256
MAX_LIMIT = 200
MAX_OFFSET = 100_000
_TIMESTAMP_PATTERN = re.compile(r"\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00\Z")


@dataclass(frozen=True)
class FilterClause:
    field: str
    op: str
    value: Any


@dataclass(frozen=True)
class FilterSpec:
    dataset: Dataset
    clauses: tuple[FilterClause, ...] = ()
    sort_by: str | None = None
    descending: bool = False
    offset: int = 0
    limit: int = 50

    @classmethod
    def from_json(
        cls,
        dataset: Dataset,
        raw: str | None = None,
        *,
        sort_by: str | None = None,
        descending: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> FilterSpec:
        try:
            dataset = Dataset(dataset)
        except (TypeError, ValueError) as exc:
            raise ValueError("dataset must be one of: events, detections, user_risk") from exc
        if not 0 <= offset <= MAX_OFFSET:
            raise ValueError(f"offset must be between 0 and {MAX_OFFSET}")
        if not 1 <= limit <= MAX_LIMIT:
            raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
        fields = FIELD_REGISTRY[dataset]
        if sort_by is not None and (sort_by not in fields or not fields[sort_by].sortable):
            raise ValueError("sort_by is not allowed for this dataset")
        try:
            values = [] if raw in (None, "") else json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("filters must be a JSON array") from exc
        if not isinstance(values, list) or len(values) > MAX_CLAUSES:
            raise ValueError(f"filters must contain at most {MAX_CLAUSES} clauses")
        clauses: list[FilterClause] = []
        for item in values:
            if not isinstance(item, dict) or set(item) != {"field", "op", "value"}:
                raise ValueError("each filter must contain field, op, and value")
            field, op, value = item["field"], item["op"], item["value"]
            if field not in fields:
                raise ValueError(f"filter field is not allowed: {field}")
            spec = fields[field]
            if op not in spec.operators:
                raise ValueError(f"operator {op!r} is not allowed for {field}")
            if op == "in":
                if not isinstance(value, list) or not value or len(value) > MAX_VALUES:
                    raise ValueError(f"in values must contain 1-{MAX_VALUES} items")
                typed = tuple(_validate_value(spec.kind, v) for v in value)
            else:
                typed = _validate_value(spec.kind, value)
            clauses.append(FilterClause(field, op, typed))
        return cls(dataset, tuple(clauses), sort_by, bool(descending), offset, limit)

    def as_json(self) -> str:
        return json.dumps(
            [{"field": c.field, "op": c.op, "value": list(c.value) if isinstance(c.value, tuple) else c.value} for c in self.clauses],
            separators=(",", ":"),
            sort_keys=True,
        )


def _validate_value(kind: str, value: Any) -> Any:
    if kind in {"string", "timestamp"}:
        if not isinstance(value, str) or not value or len(value) > MAX_STRING:
            raise ValueError(f"value must be a non-empty string of at most {MAX_STRING} characters")
        if kind == "timestamp":
            if not _TIMESTAMP_PATTERN.fullmatch(value):
                raise ValueError("timestamp must match YYYY-MM-DDTHH:MM:SS+00:00")
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
            except ValueError as exc:
                raise ValueError("timestamp must be a valid UTC datetime") from exc
        return value
    if kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("numeric value must be finite")
        return value
    raise ValueError("unsupported filter field type")


def compile_filters(spec: FilterSpec, columns: set[str]) -> pl.Expr:
    expression: pl.Expr | None = None
    for clause in spec.clauses:
        if clause.field not in columns:
            raise ValueError(f"artifact is missing filter field: {clause.field}")
        col = pl.col(clause.field)
        value = clause.value
        if clause.op == "eq":
            current = col == value
        elif clause.op == "neq":
            current = col != value
        elif clause.op == "in":
            current = col.is_in(value)
        elif clause.op == "contains":
            current = col.cast(pl.Utf8).str.contains(value, literal=True)
        elif clause.op == "gte":
            current = col >= value
        elif clause.op == "lte":
            current = col <= value
        else:
            raise ValueError(f"unsupported operator: {clause.op}")
        expression = current if expression is None else expression & current
    return expression if expression is not None else pl.lit(True)
