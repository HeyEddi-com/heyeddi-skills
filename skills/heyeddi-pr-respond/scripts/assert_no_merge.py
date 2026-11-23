#!/usr/bin/env python3
"""Merge gate: refuse merge / auto_merge unless the user said authorize merge this turn,
or the project policy (.heyeddi/stack.json agent.permissions.merge) is auto."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _skill_cli import emit

AUTHORIZE_RE = re.compile(r"\bauthorize\s+merge\b", re.I)
MERGE_CMD_RE = re.compile(
    r"\b(gh\s+pr\s+merge|git\s+merge\b|enable.*auto[_-]?merge|auto_merge\s*:)",
    re.I,
)


def merge_policy(root: Path | None) -> str:
    """auto | ask | deny from .heyeddi/stack.json. Same rules as heyeddi-local-first permission_policy."""
    start = (root or Path.cwd()).resolve()
    for folder in (start, *start.parents):
        path = folder / ".heyeddi" / "stack.json"
        if not path.is_file():
            continue
        try:
            agent = json.loads(path.read_text(encoding="utf-8")).get("agent") or {}
        except (OSError, json.JSONDecodeError, AttributeError):
            return "ask"
        level = (agent.get("permissions") or {}).get("merge")
        if level in ("auto", "ask", "deny"):
            return level
        return "auto" if agent.get("preset") == "autonomous" else "ask"
    return "ask"


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

    policy = merge_policy(Path(args.project_root) if args.project_root else None)
    said = bool(AUTHORIZE_RE.search(args.user_text or ""))
    authorized = policy == "auto" or (policy == "ask" and said)
    planned = args.planned_command or ""
    looks_like_merge = bool(MERGE_CMD_RE.search(planned)) if planned else False
    issues: list[str] = []
    if args.check_yaml:
        from _skill_cli import resolve_project_root
        root = resolve_project_root(args.project_root)
        yaml_path = root / "eddi-ci.yaml"
        if yaml_path.is_file() and re.search(r"(?m)^\s*auto_merge\s*:", yaml_path.read_text(encoding="utf-8")):
            issues.append("eddi-ci.yaml contains auto_merge (forbidden)")

    payload = {
        "authorized": authorized,
        "merge_policy": policy,
        "looks_like_merge": looks_like_merge,
        "merge_allowed": authorized,
        "allow": ((not looks_like_merge) or authorized) and not issues,
        "issues": issues,
        "rule": (
            "Merge follows agent.permissions.merge in .heyeddi/stack.json. With ask (the default), "
            "merge only after the user says 'authorize merge' in the current turn. "
            "auto_merge in eddi-ci.yaml is never allowed. Commit and push follow their own policy."
        ),
    }
    emit(json.dumps(payload, indent=2))
    if (args.check and not payload["allow"]) or issues:
        print(
            "BLOCKED: merge-like command without 'authorize merge' in current turn"
            if not issues
            else "BLOCKED: " + "; ".join(issues),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
