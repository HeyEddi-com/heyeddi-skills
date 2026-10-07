#!/usr/bin/env python3
"""Suggest HeyEddi skills for a user prompt (and optional skill-routing.json)."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import suggest_skills as build_suggestions
from _catalog import find_hub_root
from _skill_cli import emit, fail, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest skills for a task")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None)
    parser.add_argument("--user-prompt", default=None)
    parser.add_argument("--prompt-file", default=None)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--refresh", action="store_true", help="Rescan and rewrite skills index before suggesting")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)

    prompt = args.user_prompt or ""
    if args.prompt_file:
        path = Path(args.prompt_file)
        if not path.is_file():
            path = project_root / args.prompt_file
        if not path.is_file():
            fail(f"prompt file not found: {args.prompt_file}")
        prompt = path.read_text(errors="replace")

    if not prompt.strip():
        fail("Provide --user-prompt or --prompt-file")

    emit(
        build_suggestions(
            project_root,
            prompt,
            hub_root=hub_root,
            limit=max(1, args.limit),
            refresh_index=args.refresh,
        )
    )


if __name__ == "__main__":
    main()
