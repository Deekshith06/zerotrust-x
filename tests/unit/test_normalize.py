from datetime import UTC

from zerotrust_x.normalize import (
    normalize_action,
    normalize_event_type,
    normalize_user_id,
    parse_bytes,
    parse_ip,
    parse_port,
    parse_risk,
    parse_timestamp,
)


def test_user_ids_use_explicit_canonical_form():
    assert normalize_user_id("EMP-12345") == "EMP12345"
    assert normalize_user_id("emp_12345") == "EMP12345"
    assert normalize_user_id("12345") == "EMP12345"
    assert normalize_user_id("employee-12345") is None


def test_invalid_network_values_are_not_repaired():
    assert parse_ip("10.232.175") == (None, "invalid")
    assert parse_port("65535") == (65535, "valid")
    assert parse_port("65535.5") == (None, "invalid")
    assert parse_port("65536") == (None, "out_of_range")


def test_unit_suffixed_byte_quantities_are_valid():
    assert parse_bytes("38805.48 KB") == (39736811, "valid")
    assert parse_bytes("43.63 MB") == (45749370, "valid")
    assert parse_bytes("1024 B") == (1024, "valid")
    assert parse_bytes("-50 MB") == (None, "out_of_range")
    assert parse_bytes("not_bytes") == (None, "invalid")


def test_risk_never_clamps_or_maps_labels():
    assert parse_risk("57/100") == (57.0, "valid")
    assert parse_risk("-3") == (None, "out_of_range")
    assert parse_risk("High") == (None, "non_numeric")


def test_event_and_action_normalization():
    assert normalize_event_type("MFA_FAILED") == "mfa_failed"
    assert normalize_event_type("Successful Login") == "login_success"
    assert normalize_action("DROP") == "deny"


def test_timestamp_formats_are_explicit_and_aware():
    parsed, fmt, error = parse_timestamp("09-08-2026 09:36:51 AM")
    assert parsed and parsed.tzinfo == UTC
    assert fmt == "mdy_dash_ampm"
    assert error is None

    parsed, fmt, error = parse_timestamp("not a timestamp")
    assert parsed is None and fmt == "unparsed" and error == "TIMESTAMP_UNPARSED"

