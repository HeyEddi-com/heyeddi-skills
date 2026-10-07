#!/usr/bin/env python3
"""Suggest the next HeyEddi @skill and concrete command after the current skill."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import find_hub_root
from _next_skill import suggest_next_skill
from _skill_cli import emit, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest next HeyEddi skill and command")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None)
    parser.add_argument("--current-skill", default=None, help="Skill that just finished (folder name)")
    parser.add_argument("--route", default=None, help="Route path when known (e.g. /settings)")
    parser.add_argument("--mode", default=None, help="Sub-command just finished (e.g. shape, craft, audit)")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)

    emit(
        suggest_next_skill(
            project_root,
            current_skill=args.current_skill,
            current_route=args.route,
            current_mode=args.mode,
            hub_root=hub_root,
        )
    )


if __name__ == "__main__":
    main()
