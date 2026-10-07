#!/usr/bin/env python3
"""Write `.heyeddi/skills-index.json` and `.heyeddi/skills-index.md`."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import find_hub_root, write_skills_index
from _skill_cli import emit, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Write project skills index under .heyeddi/")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Report plan without writing")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root, auto_sync=False)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)

    if args.dry_run:
        emit(
            {
                "dry_run": True,
                "would_write": [
                    ".heyeddi/skills-index.json",
                    ".heyeddi/skills-index.md",
                ],
                "hub_root": str(hub_root) if hub_root else None,
            }
        )
        return

    emit(write_skills_index(project_root, hub_root))


if __name__ == "__main__":
    main()
