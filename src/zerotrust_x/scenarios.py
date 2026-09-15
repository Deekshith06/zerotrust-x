"""Demonstration scenarios mapped to immutable Parquet telemetry.

Provides a discreet, evidence-backed scenario control lab for demonstrating:
1. Normal Login (NORMAL)
2. Account Compromise (SUSPICIOUS)
3. MFA Abuse (SUSPICIOUS)
4. Endpoint Incident (HIGH)
5. Multi-source Correlated Incident (CRITICAL)

All identities, devices, IPs, and event types referenced map to actual records
in the frozen dataset without fabricating fake metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScenarioStep:
    step_number: int
    timestamp_offset: str
    phase: str
    source: str
    event_type: str
    description: str
    entity_id: str
    severity: str
    evidence_id: str | None = None


@dataclass(frozen=True)
class ScenarioDefinition:
    id: str
    title: str
    category: str  # NORMAL, SUSPICIOUS, HIGH, CRITICAL
    target_user: str
    description: str
    expected_risk: int
    expected_risk_level: str
    expected_detections: list[str]
    steps: list[ScenarioStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "target_user": self.target_user,
            "description": self.description,
            "expected_risk": self.expected_risk,
            "expected_risk_level": self.expected_risk_level,
            "expected_detections": self.expected_detections,
            "steps": [
                {
                    "step_number": s.step_number,
                    "timestamp_offset": s.timestamp_offset,
                    "phase": s.phase,
                    "source": s.source,
                    "event_type": s.event_type,
                    "description": s.description,
                    "entity_id": s.entity_id,
                    "severity": s.severity,
                    "evidence_id": s.evidence_id,
                }
                for s in self.steps
            ],
        }


SCENARIOS: dict[str, ScenarioDefinition] = {
    "normal-login": ScenarioDefinition(
        id="normal-login",
        title="Normal Employee Login",
        category="NORMAL",
        target_user="EMP10001",
        description="Standard corporate authentication workflow. Single IP, valid MFA token, expected departmental workstation.",
        expected_risk=10,
        expected_risk_level="low",
        expected_detections=[],
        steps=[
            ScenarioStep(
                step_number=1,
                timestamp_offset="00:00",
                phase="Authentication",
                source="iam",
                event_type="login_success",
                description="Employee initiates SSO authentication from internal network.",
                entity_id="EMP10001",
                severity="low",
                evidence_id="IAM00000001",
            ),
            ScenarioStep(
                step_number=2,
                timestamp_offset="00:01",
                phase="Identity Verification",
                source="identity",
                event_type="identity_record",
                description="Identity directory confirms department and active credentials.",
                entity_id="EMP10001",
                severity="low",
                evidence_id="ID00000001",
            ),
            ScenarioStep(
                step_number=3,
                timestamp_offset="00:02",
                phase="Endpoint Session",
                source="endpoint",
                event_type="device_action",
                description="Assigned corporate workstation DEV10001 binds session.",
                entity_id="DEV10001",
                severity="low",
                evidence_id="EPA00000001",
            ),
        ],
    ),
    "account-compromise": ScenarioDefinition(
        id="account-compromise",
        title="Account Credential Stuffing & Takeover",
        category="SUSPICIOUS",
        target_user="EMP10522",
        description="Multiple rapid failed authentications from anomalous IP followed by unauthorized privileged action.",
        expected_risk=92,
        expected_risk_level="critical",
        expected_detections=["MULTIPLE_FAILED_LOGINS"],
        steps=[
            ScenarioStep(
                step_number=1,
                timestamp_offset="00:00",
                phase="Authentication",
                source="iam",
                event_type="login_failed",
                description="Failed authentication attempt from external IP address.",
                entity_id="EMP10522",
                severity="medium",
                evidence_id="IAM00002536",
            ),
            ScenarioStep(
                step_number=2,
                timestamp_offset="00:01",
                phase="Authentication",
                source="iam",
                event_type="login_failed",
                description="Second failed attempt with credential mismatch.",
                entity_id="EMP10522",
                severity="medium",
                evidence_id="IAM00015413",
            ),
            ScenarioStep(
                step_number=3,
                timestamp_offset="00:02",
                phase="Authentication",
                source="iam",
                event_type="login_failed",
                description="Third failed attempt triggers MULTIPLE_FAILED_LOGINS detection.",
                entity_id="EMP10522",
                severity="high",
                evidence_id="IAM00015985",
            ),
            ScenarioStep(
                step_number=4,
                timestamp_offset="00:04",
                phase="Privilege Escalation",
                source="iam",
                event_type="privilege_action",
                description="Subsequent session attempts unassigned administrative action.",
                entity_id="EMP10522",
                severity="high",
                evidence_id="IAM00007214",
            ),
        ],
    ),
    "mfa-abuse": ScenarioDefinition(
        id="mfa-abuse",
        title="MFA Fatigue & Token Bypass",
        category="SUSPICIOUS",
        target_user="EMP11411",
        description="Repeated MFA push notifications rejected by employee followed by anomalous secondary token validation.",
        expected_risk=94,
        expected_risk_level="critical",
        expected_detections=["MFA_FAILURE", "MULTIPLE_FAILED_LOGINS"],
        steps=[
            ScenarioStep(
                step_number=1,
                timestamp_offset="00:00",
                phase="MFA Challenge",
                source="iam",
                event_type="mfa_failed",
                description="Push notification rejected or expired on mobile device.",
                entity_id="EMP11411",
                severity="high",
                evidence_id="IAM00010041",
            ),
            ScenarioStep(
                step_number=2,
                timestamp_offset="00:01",
                phase="MFA Challenge",
                source="iam",
                event_type="mfa_failed",
                description="Second rapid MFA rejection recorded within 60 seconds.",
                entity_id="EMP11411",
                severity="high",
                evidence_id="IAM00005213",
            ),
            ScenarioStep(
                step_number=3,
                timestamp_offset="00:03",
                phase="Detection Engine",
                source="detection",
                event_type="rule_trigger",
                description="Deterministic rule MFA_FAILURE fired for EMP11411.",
                entity_id="det-mfa-EMP11411",
                severity="high",
                evidence_id="det-mfa-EMP11411",
            ),
        ],
    ),
    "endpoint-incident": ScenarioDefinition(
        id="endpoint-incident",
        title="Endpoint EDR Threat & Lateral Egress",
        category="HIGH",
        target_user="EMP10892",
        description="EDR agent logs suspicious binary execution, unquoted service path tampering, and outbound network beaconing.",
        expected_risk=88,
        expected_risk_level="high",
        expected_detections=["ENDPOINT_ALERT"],
        steps=[
            ScenarioStep(
                step_number=1,
                timestamp_offset="00:00",
                phase="Endpoint Execution",
                source="endpoint",
                event_type="endpoint_alert",
                description="EDR sensor identifies suspicious script host execution bypassing policy.",
                entity_id="DEV77305",
                severity="high",
                evidence_id="EPA00001579",
            ),
            ScenarioStep(
                step_number=2,
                timestamp_offset="00:02",
                phase="Network Egress",
                source="firewall",
                event_type="network_activity",
                description="Firewall logs high-volume egress attempt on non-standard port.",
                entity_id="FW00001234",
                severity="medium",
                evidence_id="FW00001234",
            ),
        ],
    ),
    "multi-source-correlated": ScenarioDefinition(
        id="multi-source-correlated",
        title="Multi-Source Correlated Advanced Attack Chain",
        category="CRITICAL",
        target_user="EMP11411",
        description="Full-chain correlation across IAM auth failures, MFA fatigue, host privilege breach, and denied firewall egress.",
        expected_risk=100,
        expected_risk_level="critical",
        expected_detections=["MULTIPLE_FAILED_LOGINS", "MFA_FAILURE", "ENDPOINT_ALERT"],
        steps=[
            ScenarioStep(
                step_number=1,
                timestamp_offset="00:00",
                phase="IAM Infiltration",
                source="iam",
                event_type="login_failed",
                description="Burst of 24 authentication failures observed from anomalous IP 203.0.113.45.",
                entity_id="EMP11411",
                severity="high",
                evidence_id="IAM00013267",
            ),
            ScenarioStep(
                step_number=2,
                timestamp_offset="00:02",
                phase="MFA Abuse",
                source="iam",
                event_type="mfa_failed",
                description="Repeated MFA push denials logged, triggering MFA_FAILURE rule.",
                entity_id="EMP11411",
                severity="high",
                evidence_id="IAM00010041",
            ),
            ScenarioStep(
                step_number=3,
                timestamp_offset="00:03",
                phase="Host Intrusion",
                source="endpoint",
                event_type="endpoint_alert",
                description="EDR alert on device DEV77305: privilege boundary violation.",
                entity_id="DEV77305",
                severity="critical",
                evidence_id="EPA00001579",
            ),
            ScenarioStep(
                step_number=4,
                timestamp_offset="00:04",
                phase="Network Perimeter",
                source="firewall",
                event_type="network_activity",
                description="Firewall denies outbound connection to external IP with explicit country telemetry (IN).",
                entity_id="FW00007890",
                severity="high",
                evidence_id="FW00007890",
            ),
            ScenarioStep(
                step_number=5,
                timestamp_offset="00:05",
                phase="Risk Escalation",
                source="correlation",
                event_type="risk_update",
                description="Correlation engine escalates EMP11411 risk to 100/100 (CRITICAL).",
                entity_id="EMP11411",
                severity="critical",
                evidence_id="EMP11411",
            ),
            ScenarioStep(
                step_number=6,
                timestamp_offset="00:06",
                phase="AI Investigation",
                source="agent",
                event_type="grounded_investigation",
                description="AI SOC investigator verifies 82 citations; report completed and grounded.",
                entity_id="inv-11411",
                severity="critical",
                evidence_id="inv-11411",
            ),
        ],
    ),
}


def list_scenarios() -> list[dict[str, Any]]:
    return [s.to_dict() for s in SCENARIOS.values()]


def get_scenario(scenario_id: str) -> dict[str, Any] | None:
    scenario = SCENARIOS.get(scenario_id)
    return scenario.to_dict() if scenario else None
