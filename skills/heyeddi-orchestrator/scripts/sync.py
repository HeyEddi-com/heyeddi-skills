#!/usr/bin/env python3
"""Full `.heyeddi/` sync: refresh index, init workflow if new, check skills updates."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import find_hub_root, write_skills_index
from _skill_cli import emit, resolve_project_root
from _skills_update import check_skills_update
from init_workflow_sync import scaffold_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync .heyeddi/ workspace for installed skills")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None)
    parser.add_argument("--skip-workflow", action="store_true")
    parser.add_argument(
        "--skip-update-check",
        action="store_true",
        help="Skip hub version check (still never auto-installs)",
    )
    parser.add_argument(
        "--force-update-check",
        action="store_true",
        help="Run update check even if throttled",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root, auto_sync=False)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)

    if args.dry_run:
        emit(
            {
                "dry_run": True,
                "would_write": [".heyeddi/skills-index.json", ".heyeddi/skills-index.md"],
                "would_check_skills_update": not args.skip_update_check,
            }
        )
        return

    payload = dict(write_skills_index(project_root, hub_root))

    workflow_readme = project_root / ".heyeddi" / "docs" / "workflow" / "README.md"
    if not args.skip_workflow and not workflow_readme.is_file():
        payload["workflow"] = scaffold_workflow(project_root)
        payload["workflow_initialized"] = workflow_readme.is_file()

    if not args.skip_update_check:
        payload["skills_update"] = check_skills_update(
            project_root,
            orchestrator_scripts=Path(__file__).resolve().parent,
            hub_root=hub_root,
            force=args.force_update_check,
        )
        if payload["skills_update"].get("ask_user"):
            payload["ask_user"] = True
            payload["user_block"] = payload["skills_update"].get("user_block")

    emit(payload)


if __name__ == "__main__":
    main()
