"""Verify `.heyeddi/stack.json` has all required setup keys."""
from __future__ import annotations

import argparse

from _skill_cli import emit, fail, resolve_project_root
from _stack_schema import REQUIRED_PATHS, missing_paths
from load_setup import load_stack, stack_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify stack.json setup completeness")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when required keys are missing or invalid",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    data = load_stack(root)
    missing = missing_paths(data)
    payload = {
        "path": str(stack_path(root)),
        "exists": stack_path(root).is_file(),
        "complete": len(missing) == 0,
        "missing": missing,
        "required": list(REQUIRED_PATHS),
    }
    emit(payload)
    if args.check and missing:
        fail(f"setup incomplete: missing {', '.join(missing)}")


if __name__ == "__main__":
    main()
