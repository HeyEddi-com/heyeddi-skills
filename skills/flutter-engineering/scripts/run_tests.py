#!/usr/bin/env python3
"""Run flutter test."""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Flutter tests")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    if not shutil.which("flutter"):
        hint = "Install the Flutter SDK (https://docs.flutter.dev/get-started/install), then rerun"
        emit(json.dumps({"status": "fail", "error": "flutter CLI not found", "hint": hint}, indent=2))
        sys.exit(1)

    output = run_command(["flutter", "test"], root, timeout=600)
    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(json.dumps({"status": "pass" if ok else "fail", "output": output[:8000]}, indent=2))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
