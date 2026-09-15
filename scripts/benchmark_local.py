"""Bounded local benchmark; measurements are not production SLO evidence."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from fastapi.testclient import TestClient

from zerotrust_x.api import create_app
from zerotrust_x.pipeline import run_pipeline


def _measure(client: TestClient, path: str, repeats: int) -> dict[str, float | int | str]:
    samples: list[float] = []
    status = 0
    for _ in range(repeats):
        started = time.perf_counter()
        response = client.get(path, headers={"X-Demo-Token": "analyst-demo"})
        samples.append((time.perf_counter() - started) * 1000)
        status = response.status_code
        if status != 200:
            raise RuntimeError(f"benchmark request failed: {status}")
    return {
        "path": path,
        "status": status,
        "repeats": repeats,
        "min_ms": round(min(samples), 3),
        "median_ms": round(statistics.median(samples), 3),
        "max_ms": round(max(samples), 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20:
        raise SystemExit("--repeats must be between 1 and 20")
    processed = args.work_dir / "processed"
    quarantine = args.work_dir / "quarantine"
    run_pipeline(args.input_dir, processed, quarantine, iteration_id="local-benchmark")
    client = TestClient(create_app(processed))
    paths = (
        "/api/summary",
        "/api/v1/events?limit=25",
        "/api/graph/EMP10001",
        "/api/investigations/EMP10001",
    )
    print(json.dumps({"scope": "local-only", "measurements": [_measure(client, path, args.repeats) for path in paths]}, indent=2))


if __name__ == "__main__":
    main()
