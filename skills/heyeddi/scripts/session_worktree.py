#!/usr/bin/env python3
"""Mark which agent sessions own and touch a git worktree.

The marker lives in the worktree's own git directory
(``.git/worktrees/<name>/heyeddi-session.json``, or ``.git/heyeddi-session.json``
in a plain checkout). Git never tracks that directory, so the marker can't be
committed and needs no ``.gitignore`` entry.

One session is the owner: the one that created or claimed the worktree first.
Only the owner writes. Every other session is read-only, including one recorded
as a contributor (``claim --user-approved``). ``worktree_guard.py`` enforces
this as a Claude Code hook.
Ownership moves only with ``handoff`` (by the owner, or with ``--user-approved``).

Usage:
  session_worktree.py claim   [--path P] [--task TEXT] [--pr URL] [--session ID]
  session_worktree.py check   [--path P] --action ACTION [--session ID]
  session_worktree.py handoff [--path P] --to ID [--session ID] [--user-approved]
  session_worktree.py list    [--path P] [--session ID]

Exit codes for ``check``: 0 allowed, 1 blocked, 2 no marker (read-only; report it).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None  # type: ignore[assignment]
    import msvcrt

MARKER_NAME = "heyeddi-session.json"
SESSION_ENV_VARS = ("HEYEDDI_SESSION_ID", "CLAUDE_CODE_SESSION_ID")
OWNER_ONLY_ACTIONS = frozenset({"merge", "delete", "force-push", "rebase", "handoff"})
WRITE_ACTIONS = frozenset({"commit", "push"})
ACTIONS = sorted(OWNER_ONLY_ACTIONS | WRITE_ACTIONS)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _git(path: Path, *args: str) -> str:
    # A GIT_DIR inherited from a hook would point -C at the wrong repository.
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    proc = subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.stdout.strip()


def resolve_session(explicit: str | None) -> str:
    if explicit:
        return explicit
    for name in SESSION_ENV_VARS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise SystemExit(
        "no session id: pass --session or set one of " + ", ".join(SESSION_ENV_VARS)
    )


def marker_path(worktree: Path) -> Path:
    git_dir = Path(_git(worktree, "rev-parse", "--absolute-git-dir"))
    return git_dir / MARKER_NAME


def load_marker(worktree: Path) -> dict[str, Any] | None:
    path = marker_path(worktree)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def _locked(worktree: Path) -> Iterator[None]:
    """Serialize read-modify-write so concurrent sessions never drop each other's entries."""
    lock_path = marker_path(worktree).with_suffix(".lock")
    with open(lock_path, "a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle, fcntl.LOCK_EX)
        else:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle, fcntl.LOCK_UN)
            else:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def _save(worktree: Path, marker: dict[str, Any]) -> None:
    path = marker_path(worktree)
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _branch(worktree: Path) -> str:
    try:
        return _git(worktree, "rev-parse", "--abbrev-ref", "HEAD")
    except subprocess.CalledProcessError:
        return ""


def _entry(marker: dict[str, Any], session: str) -> dict[str, Any] | None:
    for item in marker.get("sessions", []):
        if item.get("id") == session:
            return item
    return None


def role_of(marker: dict[str, Any] | None, session: str) -> str:
    if not marker:
        return "none"
    if marker.get("owner") == session:
        return "owner"
    if _entry(marker, session):
        return "contributor"
    return "none"


def claim(
    worktree: Path, session: str, *, task: str | None, pr: str | None, user_approved: bool = False
) -> dict[str, Any]:
    with _locked(worktree):
        marker = load_marker(worktree)
        if marker and role_of(marker, session) == "none" and not user_approved:
            return {
                "ok": False,
                "owner": marker["owner"],
                "reason": "another session owns this worktree. Make your own, or pass "
                "--user-approved only after the user asks you to work in this one",
            }
        return _claim(worktree, session, task=task, pr=pr)


def _claim(worktree: Path, session: str, *, task: str | None, pr: str | None) -> dict[str, Any]:
    marker = load_marker(worktree)
    now = _now()
    if marker is None:
        marker = {
            "version": 1,
            "owner": session,
            "task": task or "",
            "pr": pr or "",
            "branch": _branch(worktree),
            "sessions": [],
            "history": [{"at": now, "event": "created", "session": session}],
        }
    entry = _entry(marker, session)
    if entry is None:
        entry = {"id": session, "first_seen": now}
        marker["sessions"].append(entry)
    entry["last_seen"] = now
    entry["role"] = "owner" if marker["owner"] == session else "contributor"
    if task:
        if entry["role"] == "owner":
            marker["task"] = task
        else:
            entry["note"] = task
    if pr and entry["role"] == "owner":
        marker["pr"] = pr
    marker["branch"] = _branch(worktree) or marker.get("branch", "")
    _save(worktree, marker)
    return {"ok": True, "role": entry["role"], "owner": marker["owner"], "marker": str(marker_path(worktree))}


def check(worktree: Path, session: str, action: str) -> tuple[int, dict[str, Any]]:
    marker = load_marker(worktree)
    if marker is None:
        return 2, {
            "ok": False,
            "reason": "no session marker: treat as read-only and report it under Needs you",
        }
    role = role_of(marker, session)
    if role == "owner":
        return 0, {"ok": True, "role": role}
    if role == "contributor":
        reason = f"only the owner writes here; ask the user for a handoff from session {marker['owner']}"
    else:
        reason = (
            f"session is not in this worktree's marker (owner {marker['owner']}); "
            "treat it as read-only unless the user hands it off"
        )
    return 1, {"ok": False, "role": role, "reason": reason}


def handoff(
    worktree: Path, session: str, to: str, *, user_approved: bool
) -> tuple[int, dict[str, Any]]:
    with _locked(worktree):
        return _handoff(worktree, session, to, user_approved=user_approved)


def _handoff(
    worktree: Path, session: str, to: str, *, user_approved: bool
) -> tuple[int, dict[str, Any]]:
    marker = load_marker(worktree)
    if marker is None:
        return 2, {"ok": False, "reason": "no session marker to hand off"}
    if marker["owner"] != session and not user_approved:
        return 1, {
            "ok": False,
            "reason": f"only the owner ({marker['owner']}) or the user can move ownership",
        }
    now = _now()
    previous = marker["owner"]
    marker["owner"] = to
    for item in marker["sessions"]:
        item["role"] = "owner" if item["id"] == to else "contributor"
    if _entry(marker, to) is None:
        marker["sessions"].append({"id": to, "role": "owner", "first_seen": now, "last_seen": now})
    marker.setdefault("history", []).append(
        {"at": now, "event": "handoff", "from": previous, "to": to, "by": session, "user_approved": user_approved}
    )
    _save(worktree, marker)
    return 0, {"ok": True, "owner": to, "previous": previous}


def list_worktrees(any_path: Path, session: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current: dict[str, str] = {}
    for line in _git(any_path, "worktree", "list", "--porcelain").splitlines() + [""]:
        if line:
            key, _, value = line.partition(" ")
            current[key] = value
            continue
        if current.get("worktree") and "bare" not in current:
            path = Path(current["worktree"])
            marker = load_marker(path) if path.is_dir() else None
            rows.append(
                {
                    "path": str(path),
                    "branch": current.get("branch", "").removeprefix("refs/heads/"),
                    "owner": (marker or {}).get("owner", ""),
                    "task": (marker or {}).get("task", ""),
                    "pr": (marker or {}).get("pr", ""),
                    "mine": role_of(marker, session) if session else "unknown",
                }
            )
        current = {}
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("claim", "check", "handoff", "list"):
        p = sub.add_parser(name)
        p.add_argument("--path", default=".")
        p.add_argument("--session")
        if name == "claim":
            p.add_argument("--task")
            p.add_argument("--pr")
        if name == "check":
            p.add_argument("--action", required=True, choices=ACTIONS)
        if name == "handoff":
            p.add_argument("--to", required=True)
        if name in ("claim", "handoff"):
            p.add_argument("--user-approved", action="store_true")
    args = parser.parse_args(argv)
    path = Path(args.path).resolve()

    if args.cmd == "list":
        session = args.session
        if session is None:
            session = next((os.environ[v] for v in SESSION_ENV_VARS if os.environ.get(v)), None)
        print(json.dumps(list_worktrees(path, session), indent=2))
        return 0

    session = resolve_session(args.session)
    if args.cmd == "claim":
        result = claim(path, session, task=args.task, pr=args.pr, user_approved=args.user_approved)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    if args.cmd == "check":
        code, result = check(path, session, args.action)
    else:
        code, result = handoff(path, session, args.to, user_approved=args.user_approved)
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
