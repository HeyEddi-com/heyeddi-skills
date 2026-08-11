#!/usr/bin/env python3
"""Hard gate: refuse merge / auto_merge unless user said authorize merge this turn."""
from __future__ import annotations

import argparse
import json
import re
import sys

from _skill_cli import emit

AUTHORIZE_RE = re.compile(r"\bauthorize\s+merge\b", re.I)
MERGE_CMD_RE = re.compile(
    r"\b(gh\s+pr\s+merge|git\s+merge\b|enable.*auto[_-]?merge|auto_merge\s*:)",
    re.I,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assert agent will not merge without explicit authorize merge"
    )
    parser.add_argument(
        "--user-text",
        default="",
        help="Current-turn user message (must contain 'authorize merge' to allow merge intents)",
    )
    parser.add_argument(
        "--planned-command",
        default="",
        help="Optional command the agent is about to run",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when planned command looks like merge without authorization",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Optional project root to scan eddi-ci.yaml for auto_merge",
    )
    parser.add_argument(
        "--check-yaml",
        action="store_true",
        help="Fail when eddi-ci.yaml contains auto_merge",
    )
    args = parser.parse_args()

    authorized = bool(AUTHORIZE_RE.search(args.user_text or ""))
    planned = args.planned_command or ""
    looks_like_merge = bool(MERGE_CMD_RE.search(planned)) if planned else False
    issues: list[str] = []
    if args.check_yaml:
        from pathlib import Path
        from _skill_cli import resolve_project_root
        root = resolve_project_root(args.project_root)
        yaml_path = root / "eddi-ci.yaml"
        if yaml_path.is_file() and re.search(r"(?m)^\s*auto_merge\s*:", yaml_path.read_text(encoding="utf-8")):
            issues.append("eddi-ci.yaml contains auto_merge (forbidden)")

    payload = {
        "authorized": authorized,
        "looks_like_merge": looks_like_merge,
        "merge_allowed": authorized,
        "allow": ((not looks_like_merge) or authorized) and not issues,
        "issues": issues,
        "rule": (
            "Never gh pr merge / never enable auto_merge unless the user said "
            "'authorize merge' in the current turn. Push is separate and still "
            "requires an explicit ask."
        ),
    }
    emit(json.dumps(payload, indent=2))
    if (args.check and not payload["allow"]) or issues:
        print(
            "BLOCKED: merge-like command without 'authorize merge' in current turn",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
