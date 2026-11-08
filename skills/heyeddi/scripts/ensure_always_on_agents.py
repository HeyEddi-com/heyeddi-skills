#!/usr/bin/env python3
"""Install/update thin always-on AGENTS.md + Cursor alwaysApply rule."""
from __future__ import annotations

import argparse

from _always_on_agents import ensure_always_on_agents
from _skill_cli import emit, resolve_project_root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write AGENTS.md managed section + .cursor/rules/heyeddi-always-on.mdc"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if managed files are missing or stale vs templates",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root, auto_sync=False)

    if args.check:
        from pathlib import Path

        from _always_on_agents import END, START, _TEMPLATES, _read_template

        agents = root / "AGENTS.md"
        rule = root / ".cursor" / "rules" / "heyeddi-always-on.mdc"
        problems: list[str] = []
        if not agents.is_file() or START not in agents.read_text(encoding="utf-8"):
            problems.append("AGENTS.md missing managed HeyEddi block")
        if not rule.is_file():
            problems.append(".cursor/rules/heyeddi-always-on.mdc missing")
        elif rule.read_text(encoding="utf-8") != _read_template("heyeddi-always-on.mdc"):
            problems.append(".cursor/rules/heyeddi-always-on.mdc stale")
        # Touch templates path so --check fails closed if pack is incomplete
        if not (_TEMPLATES / "AGENTS.section.md").is_file():
            problems.append("templates/always-on incomplete")
        payload = {"ok": not problems, "problems": problems, "markers": [START, END]}
        emit(payload)
        if problems:
            raise SystemExit(1)
        return

    emit(ensure_always_on_agents(root))


if __name__ == "__main__":
    main()
