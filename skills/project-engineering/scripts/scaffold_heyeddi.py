#!/usr/bin/env python3
"""Scaffold `.heyeddi/`: README, stack config, and folders for skill artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _heyeddi_paths import heyeddi_dir
from _skill_cli import emit, resolve_project_root

SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent / "scaffold" / "heyeddi"
GITIGNORE_SNIPPET = (
    Path(__file__).resolve().parent.parent / "scaffold" / "gitignore-heyeddi-pr-scratch.snippet"
)

FILE_MAP = {
    "README.md": "README.md",
    "docs/README.md": "docs/README.md",
    "product.md": "product.md",
    "design.md": "design.md",
}


def _append_gitignore_snippet(root: Path, *, dry_run: bool) -> str | None:
    """Ensure consumer .gitignore ignores ephemeral pr-* scratch files."""
    if not GITIGNORE_SNIPPET.is_file():
        return None
    snippet = GITIGNORE_SNIPPET.read_text(encoding="utf-8")
    marker = "HeyEddi PR / CI skill scratch"
    gitignore = root / ".gitignore"
    if gitignore.is_file():
        existing = gitignore.read_text(encoding="utf-8")
        if marker in existing or "pr-*-tracking.md" in existing:
            return None
        if dry_run:
            return ".gitignore (append pr-* scratch rules)"
        gitignore.write_text(existing.rstrip() + "\n\n" + snippet.lstrip(), encoding="utf-8")
        return ".gitignore (appended pr-* scratch rules)"
    if dry_run:
        return ".gitignore (create with pr-* scratch rules)"
    gitignore.write_text(snippet.lstrip(), encoding="utf-8")
    return ".gitignore (created with pr-* scratch rules)"


def merge_stack(dest: Path, template: Path, *, dry_run: bool) -> bool:
    """Add missing keys from the template. Never replace a value the project set."""
    defaults = json.loads(template.read_text(encoding="utf-8"))
    current: dict = {}
    if dest.is_file():
        try:
            current = json.loads(dest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
    merged = {**defaults, **current}
    if merged == current:
        return False
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return True


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
    stack_src = SCAFFOLD_ROOT / "stack.json"
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

    gi = _append_gitignore_snippet(root, dry_run=args.dry_run)
    if gi:
        created.append(gi)

    emit(
        json.dumps(
            {
                "status": "ok",
                "dry_run": args.dry_run,
                "created": created,
                "skipped": skipped,
                "hint": (
                    "Save durable docs under .heyeddi/docs/; "
                    "never commit ephemeral pr-* scratch (gitignored)."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
