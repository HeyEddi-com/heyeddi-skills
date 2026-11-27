#!/usr/bin/env python3
"""Run pytest in backend/ via project-engineering."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _skill_cli import emit, resolve_project_root

PE_SCRIPT = Path(__file__).resolve().parent.parent.parent / "project-engineering" / "scripts" / "run_backend_tests.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend pytest")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    if not PE_SCRIPT.is_file():
        emit(json.dumps({"status": "skip", "reason": "project-engineering not available"}, indent=2))
        return

    proc = subprocess.run(
        [sys.executable, str(PE_SCRIPT), "--project-root", str(root)],
        capture_output=True,
        text=True,
    )
    emit(proc.stdout or proc.stderr)
    if proc.returncode != 0:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
