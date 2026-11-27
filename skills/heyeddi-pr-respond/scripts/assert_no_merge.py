#!/usr/bin/env python3
"""Merge gate: production merges wait for the user's "authorize merge"; merges into other
branches follow the policy in .heyeddi/stack.json (auto under balanced)."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

from _skill_cli import emit

AUTHORIZE_RE = re.compile(r"\bauthorize\s+merge\b", re.I)
# Merge text that cannot be split into a command we understand: always production.
HIDDEN_MERGE_RE = re.compile(r"\bgh\s+pr\s+merge\b|\bgit\b[^;&|]*\smerge(?![-\w])", re.I)
AUTO_MERGE_RE = re.compile(r"enable.*auto[_-]?merge|auto_merge\s*:", re.I)
SHELLS = {"bash", "sh", "zsh", "eval"}
GIT_VALUE_FLAGS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
MOVES_GIT = ("-C", "--git-dir", "--work-tree")


def find_stack(start: Path) -> Path | None:
    """Nearest .heyeddi/stack.json; a linked worktree falls back to the main checkout's."""
    for folder in (start, *start.parents):
        candidate = folder / ".heyeddi" / "stack.json"
        if candidate.is_file():
            return candidate
    for folder in (start, *start.parents):
        marker = folder / ".git"
        if marker.is_file():
            gitdir = marker.read_text(encoding="utf-8").removeprefix("gitdir:").strip()
            main = (folder / gitdir).resolve()
            if main.parent.name == "worktrees":
                candidate = main.parents[2] / ".heyeddi" / "stack.json"
                return candidate if candidate.is_file() else None
        if marker.exists():
            break
    return None


def read_stack(root: Path | None) -> tuple[str, set[str], set[str]]:
    """(merge level, production branches, other shared branches)."""
    level, production, shared = "auto", {"main", "master"}, set()
    path = find_stack((root or Path.cwd()).resolve())
    if path is None:
        return level, production, shared
    try:
        stack = json.loads(path.read_text(encoding="utf-8"))
        agent = stack.get("agent") or {}
        git = stack.get("git") or {}
        environments = git.get("environments") or {}
        name = environments.get("production")
        shared = {v for v in [*environments.values(), git.get("default_branch")] if isinstance(v, str) and v}
        override = (agent.get("permissions") or {}).get("merge")
        preset = agent.get("preset")
    except (OSError, json.JSONDecodeError, AttributeError):
        return "ask", production, shared
    production = {name} if name else production
    if override in ("auto", "ask", "deny"):
        level = override
    elif preset == "cautious":
        level = "ask"
    return level, production, shared - production


def merge_policy(root: Path | None, base: str = "") -> str:
    """auto | ask | deny from .heyeddi/stack.json. Same rules as heyeddi-local-first permission_policy."""
    level, production, _ = read_stack(root)
    # Production (or an unnamed target) always waits for the user.
    if level == "auto" and (not base or base in production):
        return "ask"
    return level


def current_branch(root: Path | None) -> str:
    """Checked-out branch, or "" when git cannot say."""
    try:
        out = subprocess.run(
            ["git", "symbolic-ref", "--short", "-q", "HEAD"],
            cwd=root or Path.cwd(), capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _segments(command: str) -> list[list[str]] | None:
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token and set(token) <= set(";&|()"):
            segments.append([])
        else:
            segments[-1].append(token)
    return [s for s in segments if s]


def _switched_to(rest: list[str]) -> str | None:
    """Branch after `git checkout|switch`: a name, "" when unknown, None when only files change."""
    if "--" in rest:
        return None
    if "-" in rest:
        return ""
    words = [w for w in rest if not w.startswith("-")]
    return words[0] if words else ""


def merge_targets(command: str, root: Path | None, base: str) -> list[tuple[str, str]]:
    """Every merge in the command as (kind, target branch). "" means unknown: production."""
    segments = _segments(command)
    if segments is None:
        return [("hidden", "")] if "merge" in command else []
    found: list[tuple[str, str]] = []
    branch: str | None = None  # None: still the checked-out branch
    moved = False
    for words in segments:
        while words and re.match(r"^[A-Za-z_]\w*=", words[0]):
            words = words[1:]
        if not words:
            continue
        program, args = Path(words[0]).name, words[1:]
        if program in {"cd", "pushd"}:
            moved = True
        elif program in SHELLS:
            if any(HIDDEN_MERGE_RE.search(a) for a in args) or HIDDEN_MERGE_RE.search(" ".join(args)):
                found.append(("hidden", ""))
        elif program == "gh":
            if "pr" in args and "merge" in args:
                found.append(("gh", "" if "--admin" in args else base))
            elif args[:1] == ["api"] and any(re.search(r"/merges?\b", a) for a in args):
                found.append(("gh", ""))
        elif program == "git":
            elsewhere = False
            while args and args[0].startswith("-"):
                name = args[0].split("=", 1)[0]
                elsewhere = elsewhere or name in MOVES_GIT
                args = args[2:] if args[0] in GIT_VALUE_FLAGS else args[1:]
            if not args:
                continue
            sub, rest = args[0], args[1:]
            if sub in {"checkout", "switch"}:
                new = _switched_to(rest)
                branch = branch if new is None else new
            elif sub == "merge" and not {"--abort", "--quit"} & set(rest):
                target = "" if moved or elsewhere else (current_branch(root) if branch is None else branch)
                found.append(("git", target))
    return found


def merge_allowed(kind: str, target: str, root: Path | None, said: bool) -> bool:
    level, production, shared = read_stack(root)
    # A local merge into a feature branch is a branch update, not a release step.
    if kind == "git" and target and target not in production | shared:
        return True
    policy = merge_policy(root, target)
    return policy == "auto" or (policy == "ask" and said)


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
        "--base",
        default="",
        help="Target branch of the PR for gh pr merge; without it the merge is treated as production. "
        "git merge targets the checked-out branch",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the planned command merges somewhere that is not allowed",
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

    root = Path(args.project_root) if args.project_root else None
    policy = merge_policy(root, args.base)
    said = bool(AUTHORIZE_RE.search(args.user_text or ""))
    authorized = policy == "auto" or (policy == "ask" and said)
    planned = args.planned_command or ""
    targets = merge_targets(planned, root, args.base) if planned else []
    auto_merge = bool(AUTO_MERGE_RE.search(planned))
    looks_like_merge = bool(targets) or auto_merge
    allowed = all(merge_allowed(kind, target, root, said) for kind, target in targets)
    if auto_merge:
        allowed = allowed and authorized
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
        "allow": allowed and not issues,
        "merge_targets": [target or "unknown (treated as production)" for _, target in targets],
        "issues": issues,
        "rule": (
            "Below production, merge once the pre-merge gate passes (pass --base <branch>). "
            "A production merge waits for the user to say 'authorize merge' in the current turn. "
            "auto_merge in eddi-ci.yaml is never allowed."
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
