"""Pure, conservative normalization helpers."""

from __future__ import annotations

import ipaddress
import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

_MISSING = {"", "na", "n/a", "null", "none", "unknown", "not available", "-"}


def text(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value).strip()
    return None if result.casefold() in _MISSING else result


def normalize_user_id(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    compact = re.sub(r"[^A-Za-z0-9]", "", raw).upper()
    if compact.isdigit():
        return f"EMP{compact}"
    if re.fullmatch(r"EMP\d+", compact):
        return compact
    return None


def normalize_hostname(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    result = raw.strip().upper().replace("_", "-")
    for suffix in (".CORP.LOCAL", ".LOCAL"):
        if result.endswith(suffix):
            result = result[: -len(suffix)]
    return result or None


def normalize_department(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = re.sub(r"[^a-z0-9]", "", raw.casefold())
    mappings = {
        "it": "information_technology", "informationtech": "information_technology",
        "itdept": "information_technology", "itsupport": "information_technology",
        "hr": "human_resources", "hrdept": "human_resources", "humanresource": "human_resources",
        "finance": "finance", "fin": "finance", "financedept": "finance",
        "ops": "operations", "opsteam": "operations", "operations": "operations",
        "sales": "sales", "businesssales": "sales",
        "rnd": "research_development", "researchanddevelopment": "research_development",
        "rd": "research_development", "rampd": "research_development",
        "mkt": "marketing", "marketing": "marketing",
        "purch": "procurement", "purchase": "procurement", "procurementteam": "procurement",
        "legal": "legal", "legaldept": "legal", "support": "support",
    }
    return mappings.get(key, raw.casefold().strip().replace(" ", "_"))


def normalize_event_type(value: Any) -> str:
    raw = text(value)
    if raw is None:
        return "other"
    key = re.sub(r"[^a-z0-9]", "", raw.casefold())
    if "mfa" in key and ("fail" in key or "invalid" in key):
        return "mfa_failed"
    if any(token in key for token in ("failed", "failure", "invalidcredentials")):
        return "login_failed"
    success_event = any(token in key for token in ("success", "successful"))
    auth_event = any(token in key for token in ("login", "logon", "auth", "sso"))
    if success_event and auth_event:
        return "login_success"
    if "privilege" in key:
        return "privilege_action"
    if "session" in key:
        return "session_action"
    if any(token in key for token in ("account", "password")):
        return "account_action"
    if "device" in key or "mfaenrollment" in key:
        return "device_action"
    return "other"


def normalize_bool(value: Any) -> bool | None:
    raw = text(value)
    if raw is None:
        return None
    if raw.casefold() in {"true", "t", "yes", "y", "1", "pass", "passed"}:
        return True
    if raw.casefold() in {"false", "f", "no", "n", "0", "fail", "failed"}:
        return False
    return None


def normalize_action(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold()
    if key in {"allow", "allowed", "permit", "permitted", "pass", "accepted", "accept"}:
        return "allow"
    if key in {"deny", "denied", "drop", "block", "blocked", "reject", "rejected"}:
        return "deny"
    return "unknown"


def normalize_protocol(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().replace("/", "")
    mapping = {
        "tcp": "tcp", "6": "tcp", "udp": "udp", "17": "udp",
        "icmp": "icmp", "1": "icmp", "ping": "icmp",
    }
    return mapping.get(key, "other")


def parse_ip(value: Any) -> tuple[str | None, str]:
    raw = text(value)
    if raw is None:
        return None, "missing"
    try:
        return str(ipaddress.ip_address(raw)), "valid"
    except ValueError:
        return None, "invalid"


def parse_port(value: Any) -> tuple[int | None, str]:
    raw = text(value)
    if raw is None:
        return None, "missing"
    try:
        candidate = raw.replace(",", "")
        number = int(candidate)
    except (ValueError, TypeError):
        return None, "invalid"
    if not 0 <= number <= 65535:
        return None, "out_of_range"
    return number, "valid"


def parse_bytes(value: Any) -> tuple[int | None, str]:
    raw = text(value)
    if raw is None:
        return None, "missing"
    m = re.fullmatch(r"([+-]?[0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)?", raw)
    if m:
        num_str, unit = m.groups()
        try:
            num = float(num_str)
            unit_upper = (unit or "B").upper()
            multipliers = {
                "B": 1, "BYTES": 1, "BYTE": 1,
                "KB": 1024, "K": 1024, "KIB": 1024,
                "MB": 1024**2, "M": 1024**2, "MIB": 1024**2,
                "GB": 1024**3, "G": 1024**3, "GIB": 1024**3,
                "TB": 1024**4, "T": 1024**4, "TIB": 1024**4,
            }
            if unit_upper in multipliers:
                bytes_val = int(num * multipliers[unit_upper])
                return (bytes_val, "valid") if bytes_val >= 0 else (None, "out_of_range")
        except (ValueError, TypeError):
            pass
    try:
        number = int(Decimal(raw.replace(",", "")))
        return (number, "valid") if number >= 0 else (None, "out_of_range")
    except (InvalidOperation, ValueError):
        return None, "invalid"



def parse_risk(value: Any) -> tuple[float | None, str]:
    raw = text(value)
    if raw is None:
        return None, "missing"
    candidate = raw.removesuffix("/100").strip()
    try:
        number = float(candidate)
    except ValueError:
        return None, "non_numeric"
    if not 0 <= number <= 100:
        return None, "out_of_range"
    return number, "valid"


def parse_sha256(value: Any) -> tuple[str | None, str]:
    raw = text(value)
    if raw is None:
        return None, "missing"
    return (raw.lower(), "valid") if re.fullmatch(r"[0-9a-fA-F]{64}", raw) else (None, "invalid")


def parse_timestamp(value: Any) -> tuple[datetime | None, str, str | None]:
    raw = text(value)
    if raw is None:
        return None, "missing", None
    if re.fullmatch(r"\d{10}(?:\.\d+)?", raw):
        return datetime.fromtimestamp(float(raw), tz=UTC), "epoch_seconds", None
    formats = (
        ("iso", None),
        ("ymd_slash", "%Y/%m/%d %H:%M:%S"),
        ("ymd_slash_date", "%Y/%m/%d"),
        ("dmy_slash", "%d/%m/%Y %H:%M:%S"),
        ("dmy_slash_short", "%d/%m/%Y %H:%M"),
        ("dmy_slash_date", "%d/%m/%Y"),
        ("mdy_dash_ampm", "%m-%d-%Y %I:%M:%S %p"),
        ("dmy_dash_ampm", "%d-%m-%Y %I:%M:%S %p"),
        ("dmy_dash", "%d-%m-%Y %H:%M:%S"),
        ("dmy_dash_date", "%d-%m-%Y"),
        ("month_name", "%d-%b-%Y %H:%M:%S"),
        ("month_name_date", "%d-%b-%Y"),
    )
    for label, fmt in formats:
        try:
            parsed = (
                datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if fmt is None
                else datetime.strptime(raw, fmt)
            )
            return parsed.replace(tzinfo=parsed.tzinfo or UTC), label, None
        except ValueError:
            continue
    for fmt in ("%B %d, %Y %H:%M:%S", "%b %d, %Y %H:%M:%S", "%B %d, %Y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            return parsed, "month_name", None
        except ValueError:
            continue
    return None, "unparsed", "TIMESTAMP_UNPARSED"


def normalize_date(value: Any) -> date | None:
    parsed, _, _ = parse_timestamp(value)
    return parsed.date() if parsed else None


def normalize_device_criticality(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().strip()
    mapping = {
        "c": "critical", "critical": "critical",
        "h": "high", "high": "high",
        "m": "medium", "medium": "medium",
        "l": "low", "low": "low",
    }
    return mapping.get(key, key)


def normalize_severity(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().strip()
    mapping = {
        "c": "critical", "critical": "critical", "crit": "critical", "severe": "critical", "p1": "critical",
        "h": "high", "high": "high", "major": "high", "p2": "high",
        "m": "medium", "medium": "medium", "moderate": "medium", "p3": "medium",
        "l": "low", "low": "low", "minor": "low", "p4": "low",
    }
    return mapping.get(key, key)


def normalize_status(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().strip().replace(" ", "_")
    mapping = {
        "new": "new", "n": "new",
        "open": "open", "o": "open",
        "in_progress": "in_progress", "inp": "in_progress", "wip": "in_progress", "investigating": "in_progress",
        "resolved": "resolved", "r": "resolved",
        "closed": "closed",
        "unassigned": "unassigned",
        "fp": "false_positive", "not_malicious": "false_positive", "false_positive": "false_positive",
        "active": "active", "live": "active", "a": "active", "working": "active", "enabled": "active",
        "d": "inactive", "disabled": "inactive", "deactivated": "inactive", "inactive": "inactive",
        "l": "on_leave", "leave": "on_leave", "lwp": "on_leave", "ooo": "on_leave", "on_leave": "on_leave",
        "left": "terminated", "exited": "terminated", "terminated": "terminated", "resigned": "terminated",
        "blocked": "blocked",
    }
    return mapping.get(key, key)



def normalize_location(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().strip().replace("_", " ")
    mapping = {
        "work from home": "work_from_home",
        "branch office": "branch_office",
        "head office": "head_office",
        "regional office": "regional_office",
        "data center": "data_center",
        "remote": "remote",
        "warehouse": "warehouse",
    }
    return mapping.get(key, key.replace(" ", "_"))


def normalize_geo_country(value: Any) -> str | None:
    raw = text(value)
    if raw is None:
        return None
    key = raw.casefold().strip()
    mapping = {
        "us": "US", "united states": "US", "usa": "US",
        "in": "IN", "ind": "IN", "india": "IN",
        "ru": "RU", "russia": "RU",
        "cn": "CN", "china": "CN",
    }
    return mapping.get(key, raw.upper())



