#!/usr/bin/env python3
"""Install Python backend dependencies (Poetry or pip)."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _project_detect import fastapi_root
from _skill_cli import emit, resolve_project_root, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensure Python backend deps")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    api_root = fastapi_root(root)

    if not (api_root / "pyproject.toml").is_file():
        emit(json.dumps({"status": "skip", "reason": "no backend/pyproject.toml"}, indent=2))
        return

    if shutil.which("poetry"):
        # --all-extras installs the dev tools (pytest, ruff) the gates run.
        cmd = ["poetry", "install", "--all-extras"]
        if args.force:
            cmd.append("--sync")
        output = run_command(cmd, api_root, timeout=600)
    elif (api_root / "requirements.txt").is_file():
        cmd = [shutil.which("pip3") or "pip", "install", "-r", "requirements.txt"]
        output = run_command(cmd, api_root, timeout=600)
    else:
        cmd = [shutil.which("pip3") or "pip", "install", "-e", ".[dev]"]
        output = run_command(cmd, api_root, timeout=600)

    ok = not output.startswith("[exit") and not output.startswith("[error]")
    emit(
        json.dumps(
            {
                "status": "ok" if ok else "fail",
                "backend_root": str(api_root),
                "command": " ".join(cmd),
                "output": output[:4000],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
