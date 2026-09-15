"""Measured process-local observability for the local deployment."""
from __future__ import annotations

import json
import logging
import time
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

COUNTERS: Counter[str] = Counter()
LATENCIES: list[float] = []
logger = logging.getLogger("zerotrust_x")


def request_id() -> str:
    return f"req-{uuid4().hex[:12]}"


@contextmanager
def measure(operation: str) -> Iterator[str]:
    started = time.perf_counter()
    run_id = request_id()
    try:
        yield run_id
        COUNTERS[f"{operation}.success"] += 1
    except Exception:
        COUNTERS[f"{operation}.error"] += 1
        raise
    finally:
        elapsed = time.perf_counter() - started
        LATENCIES.append(elapsed)
        logger.info(json.dumps({"operation": operation, "request_id": run_id, "latency_seconds": elapsed}))


def metrics() -> dict[str, object]:
    return {
        "scope": "process_local",
        "counters": dict(COUNTERS),
        "observations": len(LATENCIES),
        "latency_seconds_total": round(sum(LATENCIES), 6),
    }
