#!/usr/bin/env python3
"""Run flutter analyze and optional web build."""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Flutter analyze + build web")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    if not (root / "pubspec.yaml").is_file():
        emit(json.dumps({"status": "skip", "reason": "no pubspec.yaml"}, indent=2))
        return

    if not shutil.which("flutter"):
        hint = "Install the Flutter SDK (https://docs.flutter.dev/get-started/install), then rerun"
        emit(json.dumps({"status": "fail", "error": "flutter CLI not found", "hint": hint}, indent=2))
        sys.exit(1)

    steps: list[dict] = []
    analyze_out = run_command(["flutter", "analyze"], root, timeout=300)
    analyze_ok = not analyze_out.startswith("[exit") and not analyze_out.startswith("[error]")
    steps.append({"step": "analyze", "ok": analyze_ok, "output": analyze_out[:4000]})

    build_ok = True
    if not args.skip_build:
        build_out = run_command(["flutter", "build", "web", "--release"], root, timeout=900)
        build_ok = not build_out.startswith("[exit") and not build_out.startswith("[error]")
        steps.append({"step": "build_web", "ok": build_ok, "output": build_out[:4000]})

    status = "pass" if analyze_ok and build_ok else "fail"
    emit(json.dumps({"status": status, "steps": steps}, indent=2))
    if status == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
