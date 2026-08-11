#!/usr/bin/env python3
"""Hard gate: refuse posting PR replies while fixes are still local-only.

HeyEddi debate / re-review reads remote HEAD. Claiming "Fixed" before
commit+push makes the bot correctly say it cannot verify the change.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from _skill_cli import emit, resolve_project_root

# Session scratch + common noise — never block the gate.
_EPHEMERAL_RE = re.compile(
    r"(^|/)\.heyeddi/docs/pr-\d+(-ci)?-"
    r"(comments|tracking|replies|posted|context|review)"
    r"(\.|$)|"
    r"(^|/)\.heyeddi/docs/pr-\d+-ci-|"
    r"(^|/)\.coverage$|"
    r"(^|/)\.pytest_cache/|"
    r"(^|/)\.mypy_cache/|"
    r"(^|/)\.ruff_cache/|"
    r"(^|/)\.venv/|"
    r"(^|/)node_modules/|"
    r"(^|/)\.DS_Store$"
)


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out.rstrip("\n")


def _is_ephemeral(path: str) -> bool:
    return bool(_EPHEMERAL_RE.search(path.replace("\\", "/")))


def _dirty_paths(root: Path) -> list[str]:
    code, out = _git(root, "status", "--porcelain", "-u")
    if code != 0:
        return [f"git status failed: {out[:200]}"]
    dirty: list[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        # porcelain: XY PATH or XY ORIG -> PATH
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        path = path.strip('"')
        if _is_ephemeral(path):
            continue
        dirty.append(path)
    return dirty


def _unpushed_count(root: Path) -> tuple[int | None, str | None]:
    """Return (commits_ahead, error). None ahead means unknown/no upstream."""
    code, _ = _git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return None, "not a git repository"
    code, _ = _git(root, "rev-parse", "--abbrev-ref", "@{u}")
    if code != 0:
        return None, "no upstream configured (push with -u first)"
    code, out = _git(root, "rev-list", "--count", "@{u}..HEAD")
    if code != 0:
        return None, f"rev-list failed: {out[:200]}"
    try:
        return int(out.strip() or "0"), None
    except ValueError:
        return None, f"bad rev-list output: {out[:80]}"


def evaluate(root: Path) -> dict:
    dirty = _dirty_paths(root)
    ahead, up_err = _unpushed_count(root)
    issues: list[str] = []
    if dirty:
        preview = ", ".join(dirty[:8])
        more = f" (+{len(dirty) - 8} more)" if len(dirty) > 8 else ""
        issues.append(
            f"uncommitted changes (excluding ephemeral .heyeddi PR scratch): {preview}{more}"
        )
    if up_err:
        issues.append(up_err)
    elif ahead and ahead > 0:
        issues.append(f"{ahead} local commit(s) not pushed to upstream")
    return {
        "ok": not issues,
        "dirty_paths": dirty,
        "unpushed_commits": ahead,
        "issues": issues,
        "rule": (
            "Commit + push code fixes to the PR branch BEFORE post_thread_replies. "
            "Debate/re-review only sees remote HEAD. Use --allow-unpushed only for "
            "decline-only sessions with no code changes (evals: --dry-run skips gate)."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assert code fixes are committed and pushed before posting replies"
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when dirty tree or unpushed commits block posting",
    )
    parser.add_argument(
        "--allow-unpushed",
        action="store_true",
        help="Skip gate (decline-only / no code change). Prefer not to use after fixes.",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    if args.allow_unpushed:
        payload = {
            "ok": True,
            "skipped": True,
            "reason": "allow-unpushed",
            "rule": evaluate(root)["rule"],
        }
        emit(json.dumps(payload, indent=2))
        return

    payload = evaluate(root)
    emit(json.dumps(payload, indent=2))
    if args.check and not payload["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
