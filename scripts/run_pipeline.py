from __future__ import annotations

import argparse
from pathlib import Path

from agentic_conservation.analysis import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run_pipeline(root, args.mode)


if __name__ == "__main__":
    main()
