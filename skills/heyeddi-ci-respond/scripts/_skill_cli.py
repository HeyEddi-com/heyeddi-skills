"""Shared CLI helpers."""
from __future__ import annotations

import json
import os
import shutil
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


def resolve_project_root(arg: str | None, *, auto_sync: bool = True) -> Path:
    root = Path(arg or os.environ.get("PROJECT_ROOT", ".")).resolve()
    if not root.is_dir():
        fail(f"project_root not found: {root}")
    if auto_sync:
        try:
            from _auto_sync import ensure_heyeddi  # noqa: PLC0415

            ensure_heyeddi(root)
        except Exception as exc:  # noqa: BLE001: never block skill tools on sync
            print(f"heyeddi auto-sync skipped: {exc}", file=sys.stderr)
    return root


def run_command(cmd: list[str], cwd: Path, timeout: int = 600) -> str:
    """Run a fixed argv command without a shell.

    The executable is resolved to an absolute path via ``shutil.which`` so the
    call never depends on a relative PATH lookup, and ``shell`` is always off  - 
    there is no string interpolation into a shell.
    """
    if not cmd:
        return "[error] empty command"
    executable = shutil.which(cmd[0])
    if executable is None:
        return f"[error] command not found: {cmd[0]}"
    try:
        result = subprocess.run(
            [executable, *cmd[1:]],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return f"[error] command timed out after {timeout}s: {cmd[0]}"

    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return f"[exit {result.returncode}]\n{output}".strip()
    return output.strip() or "(success, no output)"
