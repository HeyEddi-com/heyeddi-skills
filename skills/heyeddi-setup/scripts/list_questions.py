"""List setup questions with current values (for ask / re-run)."""
from __future__ import annotations

import argparse

from _skill_cli import emit, resolve_project_root
from _stack_schema import questions_with_state
from load_setup import load_stack


def main() -> None:
    parser = argparse.ArgumentParser(description="List stack.json setup questions")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="Only questions whose required keys are missing or invalid",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="All questions (default on re-run; same as not passing --missing-only)",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    data = load_stack(root)
    missing_only = bool(args.missing_only) and not args.all
    # Default: all questions so re-run can confirm every preference.
    if not args.missing_only and not args.all:
        missing_only = False
    questions = questions_with_state(data, missing_only=missing_only)
    emit(
        {
            "path": str(root / ".heyeddi" / "stack.json"),
            "missing_only": missing_only,
            "count": len(questions),
            "questions": questions,
        }
    )


if __name__ == "__main__":
    main()
