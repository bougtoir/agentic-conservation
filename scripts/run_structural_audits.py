"""Run parameter, budget-fairness, S3, and S0 structural audits."""

from __future__ import annotations

import argparse
from pathlib import Path

from agentic_conservation.audits import run_structural_audits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    run_structural_audits(Path(__file__).resolve().parents[1], args.mode, args.workers)


if __name__ == "__main__":
    main()
