"""Shared CLI helpers for HeyEddi skill scripts. Copied into each skill's scripts/."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def emit(data: Any) -> None:
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, indent=2))


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def resolve_project_root(arg: str | None) -> Path:
    root = Path(arg or os.environ.get("PROJECT_ROOT", ".")).resolve()
    if not root.is_dir():
        fail(f"project_root not found: {root}")
    return root


def run_command(cmd: list[str], cwd: Path, timeout: int = 600) -> str:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return f"[error] command not found: {cmd[0]}\n{exc}"
    except subprocess.TimeoutExpired:
        return f"[error] command timed out after {timeout}s: {' '.join(cmd)}"

    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return f"[exit {result.returncode}]\n{output}".strip()
    return output.strip() or "(success, no output)"
