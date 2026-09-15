"""Command-line entry point for the P0 pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from zerotrust_x.pipeline import run_pipeline
from zerotrust_x.recovery import verify_recovery_bundle


def main() -> None:
    parser = argparse.ArgumentParser(prog="zerotrust-x")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest = subparsers.add_parser("ingest", help="ingest and normalize Track 2 files")
    ingest.add_argument("--input-dir", type=Path, required=True)
    ingest.add_argument("--output-dir", type=Path, required=True)
    ingest.add_argument("--quarantine-dir", type=Path, required=True)
    recover = subparsers.add_parser("verify-recovery", help="copy and verify a local artifact bundle")
    recover.add_argument("--input-dir", type=Path, required=True)
    recover.add_argument("--processed-dir", type=Path, required=True)
    recover.add_argument("--quarantine-dir", type=Path, required=True)
    recover.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "ingest":
        result = run_pipeline(args.input_dir, args.output_dir, args.quarantine_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.command == "verify-recovery":
        result = verify_recovery_bundle(
            args.input_dir, args.processed_dir, args.quarantine_dir, args.destination
        )
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
