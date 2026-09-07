"""Load `.heyeddi/stack.json` and report missing required setup keys."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _skill_cli import emit, fail, resolve_project_root
from _stack_schema import missing_paths, questions_with_state


def stack_path(root: Path) -> Path:
    return root / ".heyeddi" / "stack.json"


def load_stack(root: Path) -> dict[str, Any]:
    path = stack_path(root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid stack.json: {exc}")
    if not isinstance(data, dict):
        fail("stack.json must be a JSON object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Load stack.json setup status")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    data = load_stack(root)
    missing = missing_paths(data)
    emit(
        {
            "path": str(stack_path(root)),
            "exists": stack_path(root).is_file(),
            "complete": len(missing) == 0,
            "missing": missing,
            "stack": data,
            "questions_pending": questions_with_state(data, missing_only=True),
        }
    )


if __name__ == "__main__":
    main()
