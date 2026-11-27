#!/usr/bin/env python3
"""Scaffold `.heyeddi/` for Flutter projects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _heyeddi_paths import heyeddi_dir
from _project_detect import merge_stack
from _skill_cli import emit, resolve_project_root

SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent.parent / "project-engineering" / "scaffold" / "heyeddi"

FILE_MAP = {
    "README.md": "README.md",
    "docs/README.md": "docs/README.md",
    "product.md": "product.md",
    "design.md": "design.md",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold .heyeddi workspace folder")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    base = heyeddi_dir(root)

    created: list[str] = []
    skipped: list[str] = []

    for rel, template_name in FILE_MAP.items():
        dest = base / rel
        src = SCAFFOLD_ROOT / template_name
        if not src.is_file():
            continue
        if dest.exists() and not args.force:
            skipped.append(f".heyeddi/{rel}")
            continue
        if args.dry_run:
            created.append(f".heyeddi/{rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text())
        created.append(f".heyeddi/{rel}")

    stack_dest = base / "stack.json"
    stack_src = Path(__file__).resolve().parent.parent / "scaffold" / "stack-flutter.json"
    if stack_src.is_file():
        if merge_stack(stack_dest, stack_src, dry_run=args.dry_run):
            created.append(".heyeddi/stack.json")
        else:
            skipped.append(".heyeddi/stack.json")

    for sub in ("docs", "designs", "audits"):
        d = base / sub
        if not d.is_dir():
            if not args.dry_run:
                base.mkdir(parents=True, exist_ok=True)
                d.mkdir(parents=True, exist_ok=True)
            created.append(f".heyeddi/{sub}/")

    emit(json.dumps({"status": "ok", "dry_run": args.dry_run, "created": created, "skipped": skipped}, indent=2))


if __name__ == "__main__":
    main()
