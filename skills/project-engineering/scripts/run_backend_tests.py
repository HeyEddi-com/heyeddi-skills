#!/usr/bin/env python3
"""Run pytest in the FastAPI backend."""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from _project_detect import fastapi_root
from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend pytest")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    api_root = fastapi_root(root)

    if not (api_root / "tests").is_dir():
        emit(json.dumps({"status": "skip", "reason": "no backend tests/"}, indent=2))
        return

    if shutil.which("poetry") and (api_root / "pyproject.toml").is_file():
        cmd = ["poetry", "run", "pytest", "-q"]
    else:
        cmd = [shutil.which("pytest") or "python3", "-m", "pytest", "-q"]

    output = run_command(cmd, api_root, timeout=300)
    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(json.dumps({"status": "pass" if ok else "fail", "output": output[:8000]}, indent=2))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
