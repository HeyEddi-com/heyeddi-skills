#!/usr/bin/env python3
"""Run flutter pub get for Flutter frontend."""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Flutter pub dependencies")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true", help="Run even if pubspec.lock exists")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    if not (root / "pubspec.yaml").is_file():
        emit(json.dumps({"status": "skip", "reason": "no pubspec.yaml"}, indent=2))
        return

    if not shutil.which("flutter"):
        emit(
            json.dumps(
                {
                    "status": "fail",
                    "error": "flutter CLI not found",
                    "hint": "Install the Flutter SDK (https://docs.flutter.dev/get-started/install), then rerun",
                },
                indent=2,
            )
        )
        sys.exit(1)

    if (root / "pubspec.lock").is_file() and not args.force:
        emit(json.dumps({"status": "ok", "skipped": True, "reason": "pubspec.lock present"}, indent=2))
        return

    output = run_command(["flutter", "pub", "get"], root, timeout=300)
    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(json.dumps({"status": "ok" if ok else "fail", "output": output[:8000]}, indent=2))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
