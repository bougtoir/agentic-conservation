from __future__ import annotations

import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def command(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = [
        f"recorded_utc: {datetime.now(timezone.utc).isoformat()}",
        f"platform: {platform.platform()}",
        f"python: {platform.python_version()}",
        f"processor: {platform.processor()}",
        f"cpu_count: {os.cpu_count()}",
        "",
        "memory:",
        command(["free", "-h"]),
        "",
        "disk:",
        command(["df", "-h", str(root)]),
        "",
        "packages:",
        command(["python3", "-m", "pip", "freeze"]),
    ]
    (root / "provenance/vm_environment.txt").write_text("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
