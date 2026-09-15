"""Deterministic relationship graph derived from indexed event evidence."""
from __future__ import annotations

from typing import Any

from zerotrust_x.query import ArtifactQuery

NODE_FIELDS = (
    ("hostname", "host"),
    ("device_id", "device"),
    ("source_ip", "ip"),
    ("destination_ip", "destination"),
    ("session_id", "session"),
)


def user_graph(query: ArtifactQuery, user_id: str, limit: int = 250) -> dict[str, Any]:
    """Build a bounded graph whose every node and edge is traceable to an event.

    Entities:
    - USER
    - DEVICE
    - HOSTNAME / HOST
    - IP
    - SESSION
    - ALERT / DETECTION
    - EVENT
    - COUNTRY
    - NETWORK DESTINATION
    """
    events = query.events_for_user(user_id, limit=max(1, min(limit, 500)))
    risk = query.user_risk(user_id)
    if not events and risk is None:
        return {"nodes": [], "edges": [], "user_id": user_id, "event_count": 0}

    user_node = f"user:{user_id}"
    nodes: dict[str, dict[str, Any]] = {
        user_node: {
            "id": user_node,
            "type": "user",
            "label": user_id,
            "event_ids": [],
            "risk_score": risk.get("risk_score") if risk else None,
            "risk_level": risk.get("risk_level") if risk else "low",
            "reason_codes": risk.get("reason_codes") if risk else [],
            "department": risk.get("department") if risk else None,
        }
    }
    edges: list[dict[str, Any]] = []

    for event in events:
        event_id = str(event.get("event_id"))
        event_node = f"event:{event_id}"
        nodes[event_node] = {
            "id": event_node,
            "type": "event",
            "label": event_id,
            "event_id": event_id,
            "event_type": event.get("event_type"),
            "source": event.get("source"),
            "timestamp": event.get("timestamp"),
            "severity": event.get("severity") or "low",
            "action": event.get("action") or "observed",
        }
        nodes[user_node]["event_ids"].append(event_id)
        edges.append({"source": user_node, "target": event_node, "kind": "observed", "event_id": event_id})

        for field, kind in NODE_FIELDS:
            value = event.get(field)
            if not value:
                continue
            node_id = f"{kind}:{value}"
            nodes.setdefault(node_id, {
                "id": node_id,
                "type": kind,
                "label": str(value),
                "event_ids": [],
                "source": event.get("source"),
            })
            nodes[node_id]["event_ids"].append(event_id)
            edges.append({"source": event_node, "target": node_id, "kind": field, "event_id": event_id})

        country = event.get("geo_country")
        if country and country.strip().upper() not in ("", "UNKNOWN", "UNRESOLVED", "NULL"):
            country_code = country.strip().upper()
            country_node = f"country:{country_code}"
            nodes.setdefault(country_node, {
                "id": country_node,
                "type": "country",
                "label": country_code,
                "country_code": country_code,
                "event_ids": [],
                "provenance": "explicit telemetry field",
            })
            nodes[country_node]["event_ids"].append(event_id)
            edges.append({"source": event_node, "target": country_node, "kind": "geo_country", "event_id": event_id})

    # Add detections / alerts
    detections = query.detections_for_user(user_id)
    for det in detections:
        det_id = str(det.get("detection_id") or det.get("rule_code"))
        det_node = f"alert:{det_id}"
        det_event_ids = [str(eid) for eid in (det.get("event_ids") or [])]
        nodes[det_node] = {
            "id": det_node,
            "type": "alert",
            "label": det.get("rule_code") or det_id,
            "severity": det.get("severity") or "high",
            "reason": det.get("reason") or "",
            "event_ids": det_event_ids,
        }
        edges.append({"source": user_node, "target": det_node, "kind": "detection", "detection_id": det_id})
        for eid in det_event_ids[:10]:
            event_node = f"event:{eid}"
            if event_node in nodes:
                edges.append({"source": det_node, "target": event_node, "kind": "alert_evidence", "event_id": eid})

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "user_id": user_id,
        "event_count": len(events),
        "alert_count": len(detections),
    }
