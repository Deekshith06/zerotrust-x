"""Deterministic report grounding and untrusted telemetry boundaries."""
from __future__ import annotations

import re
from typing import Any

_CITATION = re.compile(r"\b(?:evt|FW|IAM|EPA|EMP)[A-Za-z0-9_-]+\b")


def telemetry_boundary(value: Any) -> str:
    """Mark a telemetry value as data, never as an executable instruction."""
    text = str(value).replace("</telemetry_field>", "&lt;/telemetry_field&gt;")
    return f"<telemetry_field>{text}</telemetry_field>"


def cited_ids(text: str) -> set[str]:
    return set(_CITATION.findall(text))


def validate_report(report: str, tool_results: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    valid_ids = {
        str(value)
        for result in tool_results
        for key, value in result.items()
        if key in {"event_id", "user_id", "device_id", "hostname", "source_record_id"} and value
    }
    missing = sorted(citation for citation in cited_ids(report) if citation not in valid_ids)
    return not missing, missing
