"""Stable hashes and provenance helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize provenance payloads with one deterministic representation."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )


def record_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(record).encode()).hexdigest()
