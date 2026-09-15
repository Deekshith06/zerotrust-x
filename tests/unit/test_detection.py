from zerotrust_x.detection import detect, score_users


def test_detection_and_risk_are_deterministic():
    events = [
        {"event_id": "a", "user_id": "EMP1", "event_type": "login_failed", "action": None},
        {"event_id": "b", "user_id": "EMP1", "event_type": "login_failed", "action": None},
        {"event_id": "c", "user_id": "EMP1", "event_type": "login_failed", "action": None},
        {"event_id": "d", "user_id": "EMP1", "event_type": "mfa_failed", "action": None},
    ]
    detections = detect(events)
    risks = score_users(events, detections)
    assert {d.rule_code for d in detections} == {"MULTIPLE_FAILED_LOGINS", "MFA_FAILURE"}
    assert risks[0].risk_score == 32
    assert risks[0].risk_level == "medium"
    assert "MFA_FAILURE" in risks[0].reason_codes
