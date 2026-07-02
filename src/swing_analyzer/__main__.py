from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    health_path = Path(__file__).resolve().parent / "app" / "health.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(health_path),
        "--server.address",
        "localhost",
        "--server.headless",
        "true",
    ]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
