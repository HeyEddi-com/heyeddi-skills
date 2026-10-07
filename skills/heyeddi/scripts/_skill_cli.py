"""Shared CLI helpers."""
from __future__ import annotations

import json
import os
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
