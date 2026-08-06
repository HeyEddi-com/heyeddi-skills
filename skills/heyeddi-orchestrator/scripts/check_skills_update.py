#!/usr/bin/env python3
"""Check whether the HeyEddi skills hub has a newer release. Never auto-installs."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import find_hub_root
from _skill_cli import emit, resolve_project_root
from _skills_update import DEFAULT_REPO, check_skills_update


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect HeyEddi skills updates and ask the user before installing"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo for releases")
    parser.add_argument(
        "--latest",
        default=None,
        help="Override latest version (evals/offline; skips gh)",
    )
    parser.add_argument("--force", action="store_true", help="Ignore 24h throttle")
    parser.add_argument(
        "--dismiss",
        action="store_true",
        help="Dismiss nag for --latest (or last seen latest)",
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Kill switch: stop update checks (writes sync-state)",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Re-enable update checks after --disable",
    )
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)
    scripts_dir = Path(__file__).resolve().parent

    payload = check_skills_update(
        project_root,
        orchestrator_scripts=scripts_dir,
        hub_root=hub_root,
        latest_override=args.latest,
        repo=args.repo,
        force=args.force,
        dismiss=args.dismiss,
        disable=args.disable,
        enable=args.enable,
    )
    emit(payload)


if __name__ == "__main__":
    main()
