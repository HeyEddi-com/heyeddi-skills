#!/usr/bin/env python3
"""List installed HeyEddi skills: reads `.heyeddi/skills-index.json` when present."""
from __future__ import annotations

import argparse
from pathlib import Path

from _catalog import find_hub_root, get_catalog
from _skill_cli import emit, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Load HeyEddi skills catalog")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--hub-root", default=None, help="Override hub root (skills-registry.json)")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Rescan installed skills and rewrite .heyeddi/skills-index.*",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="With --refresh, scan only without writing the index",
    )
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    hub_root = Path(args.hub_root).resolve() if args.hub_root else find_hub_root(project_root)
    emit(
        get_catalog(
            project_root,
            hub_root,
            refresh=args.refresh,
            write_if_missing=not args.no_write,
        )
    )


if __name__ == "__main__":
    main()
