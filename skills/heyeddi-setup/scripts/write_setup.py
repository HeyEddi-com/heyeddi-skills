"""Write / merge preference answers into `.heyeddi/stack.json`."""
from __future__ import annotations

import argparse
import json
from typing import Any

from _skill_cli import emit, fail, resolve_project_root
from _stack_schema import (
    apply_answers,
    deep_merge,
    ensure_prefs_defaults,
    missing_paths,
    stamp_setup,
)
from load_setup import load_stack, stack_path


def _parse_json(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"invalid --json: {exc}")
    if not isinstance(data, dict):
        fail("--json must be a JSON object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Write setup answers into stack.json")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--json",
        required=True,
        help='Answers object, e.g. \'{"git.preset":"main_staging_dev","git.custom_workflow":null}\'',
    )
    parser.add_argument(
        "--answers",
        action="store_true",
        help="Treat --json as flat question-id answers",
    )
    parser.add_argument(
        "--merge-stack",
        action="store_true",
        help="Treat --json as a nested stack.json patch (deep merge)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    patch = _parse_json(args.json)
    current = load_stack(root)

    nested_keys = {"git", "agent", "setup", "frontend", "backends", "tools"}
    answer_like = bool(patch) and all(
        isinstance(k, str)
        and (
            k
            in {
                "git.preset",
                "git.custom_workflow",
                "git.worktrees",
                "git.pr_base",
                "git.default_branch",
                "agent.commit",
                "agent.push",
                "preset",
                "custom_workflow",
            }
            or k.startswith("git.")
            or k.startswith("agent.")
        )
        for k in patch
    )
    if args.merge_stack:
        use_merge = True
    elif args.answers or answer_like:
        use_merge = False
    else:
        use_merge = any(
            k in nested_keys and isinstance(patch.get(k), (dict, list)) for k in patch
        )

    try:
        if use_merge:
            updated = deep_merge(current, patch)
        else:
            updated = apply_answers(current, patch)
        updated = ensure_prefs_defaults(updated)
        updated = stamp_setup(updated)
    except ValueError as exc:
        fail(str(exc))

    path = stack_path(root)
    missing = missing_paths(updated)
    if args.dry_run:
        emit(
            {
                "dry_run": True,
                "path": str(path),
                "complete": len(missing) == 0,
                "missing": missing,
                "stack": updated,
            }
        )
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    emit(
        {
            "written": str(path),
            "complete": len(missing) == 0,
            "missing": missing,
            "stack": updated,
        }
    )


if __name__ == "__main__":
    main()
