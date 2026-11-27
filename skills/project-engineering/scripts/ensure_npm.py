#!/usr/bin/env python3
"""Install npm dependencies when node_modules is missing or forced."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensure npm dependencies")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true", help="Run npm install even if node_modules exists")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    pkg = root / "package.json"
    if not pkg.is_file():
        emit(json.dumps({"status": "skip", "reason": "no package.json"}, indent=2))
        return

    node_modules = root / "node_modules"
    if node_modules.is_dir() and not args.force:
        emit(json.dumps({"status": "ok", "action": "skipped", "reason": "node_modules present"}, indent=2))
        return

    cmd = ["npm", "ci"] if (root / "package-lock.json").is_file() else ["npm", "install"]
    output = run_command(cmd, root, timeout=600)
    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(
        json.dumps(
            {
                "status": "ok" if ok else "fail",
                "command": " ".join(cmd),
                "output": output[:4000],
            },
            indent=2,
        )
    )
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
