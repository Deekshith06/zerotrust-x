"""Explainable robust baseline anomaly scores; not trained ground truth."""
from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any


def baseline_scores(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: defaultdict[str, int] = defaultdict(int)
    for event in events:
        if event.get("user_id"):
            counts[str(event["user_id"])] += 1
    if not counts:
        return []
    center = median(counts.values())
    result = []
    for user_id, count in sorted(counts.items()):
        deviation = abs(count - center) / max(center, 1)
        score = round(min(100.0, deviation * 100), 2)
        result.append({
            "user_id": user_id,
            "event_count": count,
            "baseline_median_event_count": center,
            "anomaly_score": score,
            "contributing_feature": "event_count_deviation_from_median",
        })
    return sorted(result, key=lambda row: (-row["anomaly_score"], row["user_id"]))
