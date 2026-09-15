"""Deterministic SOC investigation graph with optional LangGraph adapter."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from zerotrust_x.grounding import validate_report
from zerotrust_x.query import ArtifactQuery


@dataclass
class InvestigationState:
    user_id: str
    question: str
    investigation_id: str = field(default_factory=lambda: f"inv-{uuid4().hex[:12]}")
    plan: list[str] = field(default_factory=list)
    tools_completed: list[str] = field(default_factory=list)
    hypothesis: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    quality_warnings: list[str] = field(default_factory=list)
    report: str = ""
    grounded: bool = False
    status: str = "created"


def intake(state: InvestigationState) -> InvestigationState:
    state.status = "planned"
    state.plan = ["retrieve identity risk", "retrieve timeline", "retrieve detections", "verify citations"]
    q_norm = (state.question or "").lower()
    if "timeline" in q_norm:
        state.hypothesis = f"Analyzing chronological authentication, endpoint, and firewall telemetry sequence for {state.user_id}."
    elif "device" in q_norm or "asset" in q_norm:
        state.hypothesis = f"Correlating assigned workstations, mobile assets, and device criticality for {state.user_id}."
    elif "ip" in q_norm or "network" in q_norm or "geo" in q_norm:
        state.hypothesis = f"Tracing source and destination IPs, egress traffic, and explicit telemetry country for {state.user_id}."
    elif "alert" in q_norm or "why" in q_norm or "risk" in q_norm:
        state.hypothesis = f"Evaluating deterministic risk contributors and rule detections for {state.user_id}."
    else:
        state.hypothesis = f"Evaluating multi-source evidence baseline and anomalous behavioral patterns for {state.user_id}."
    return state


def evidence_collection(state: InvestigationState, query: ArtifactQuery) -> InvestigationState:
    state.evidence = query.events_for_user(state.user_id)
    state.tools_completed.append("query_timeline")

    detections = query.detections_for_user(state.user_id)
    state.evidence += detections
    state.tools_completed.append("query_detections")

    risk = query.user_risk(state.user_id)
    if risk:
        state.evidence.append(risk)
    state.tools_completed.append("query_user")

    if not state.evidence:
        state.missing_information.append("No indexed evidence was found for this identity.")

    # Quality check for IP validity and GeoIP
    ips_with_invalid = [
        str(row.get("source_ip"))
        for row in state.evidence
        if row.get("quality_reason_codes") and "IP_ADDRESS_INVALID" in str(row.get("quality_reason_codes"))
    ]
    if ips_with_invalid:
        state.quality_warnings.append(
            f"IP address validation flagged in quarantine for {len(ips_with_invalid)} records associated with this session."
        )

    countries = {
        row.get("geo_country")
        for row in state.evidence
        if row.get("geo_country") and str(row.get("geo_country")).upper() not in ("", "UNKNOWN", "UNRESOLVED", "NULL")
    }
    if not countries:
        state.quality_warnings.append(
            "No explicit geo_country telemetry present in events for this user. External GeoIP enrichment is offline/unavailable; location remains UNKNOWN / UNRESOLVED."
        )

    state.status = "evidence_collected"
    return state


def correlate(state: InvestigationState) -> InvestigationState:
    risk = next((row for row in state.evidence if "risk_score" in row and "risk_level" in row), None)
    detections = [row for row in state.evidence if "detection_id" in row]
    q_norm = (state.question or "").lower()

    if risk:
        reasons = risk.get("reason_codes") or []
        state.findings = [f"Deterministic risk is {risk['risk_score']}/100 ({risk['risk_level']})."]
        state.findings.extend(f"Reason code: {reason}." for reason in reasons)
    else:
        state.findings = ["The available evidence is insufficient for a deterministic risk assessment."]

    if "device" in q_norm:
        devices = sorted({str(r.get("device_id")) for r in state.evidence if r.get("device_id") and r.get("device_id") != "None"})
        if devices:
            state.findings.append(f"Correlated devices: {', '.join(devices)}.")
        else:
            state.findings.append("No explicit device identifiers associated in indexed events.")

    if "alert" in q_norm or "why" in q_norm:
        if detections:
            det_summaries = [f"{d.get('rule_code')}: {d.get('reason')}" for d in detections]
            state.findings.extend(det_summaries)
        else:
            state.findings.append("No deterministic detection rules fired for this identity.")

    state.tools_completed.append("query_graph")
    state.status = "correlated"
    return state


def report(state: InvestigationState) -> InvestigationState:
    ids = [str(row.get("event_id")) for row in state.evidence if row.get("event_id")]
    state.citations = ids
    citation_text = ", ".join(ids[:12]) if ids else "none"
    state.report = (
        f"Investigation {state.investigation_id} for {state.user_id}.\n\n"
        f"Assessment\n- " + "\n- ".join(state.findings) + "\n\n"
        f"Evidence identifiers\n- {citation_text}\n\n"
        "This assessment describes observed telemetry and does not establish malicious intent."
    )
    valid, unsupported = validate_report(state.report, state.evidence)
    state.grounded = valid
    state.tools_completed.append("verify_citations")
    if unsupported:
        state.contradictions.append(f"Unsupported citations: {', '.join(unsupported)}")
        state.status = "rejected"
    else:
        state.status = "complete"
    return state


def investigate(user_id: str, question: str, processed_dir: Path) -> InvestigationState:
    state = intake(InvestigationState(user_id=user_id, question=question))
    state = evidence_collection(state, ArtifactQuery(processed_dir))
    state = correlate(state)
    return report(state)


def compile_langgraph():
    """Return a LangGraph builder when installed; local fallback stays dependency-free."""
    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        return None
    graph = StateGraph(dict)
    graph.add_node("intake", lambda state: {**state, "status": "planned"})
    graph.set_entry_point("intake")
    graph.add_edge("intake", END)
    return graph.compile()
