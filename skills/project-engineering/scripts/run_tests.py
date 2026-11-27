#!/usr/bin/env python3
"""Run npm test and return structured result."""
from __future__ import annotations

import argparse
import json

from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Run project tests")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--watch", action="store_true", help="Use vitest watch if available")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    pkg = root / "package.json"
    if not pkg.is_file():
        emit(json.dumps({"status": "skip", "reason": "no package.json"}, indent=2))
        return

    import json as json_mod

    data = json_mod.loads(pkg.read_text())
    if "test" not in data.get("scripts", {}):
        emit(json.dumps({"status": "skip", "reason": "no test script in package.json"}, indent=2))
        return

    cmd = ["npm", "test"]
    if args.watch:
        cmd = ["npm", "run", "test:watch"]
    output = run_command(cmd, root, timeout=300)
    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(json.dumps({"status": "pass" if ok else "fail", "output": output[:8000]}, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
