#!/usr/bin/env python3
"""Claude Code PreToolUse hook: only the owner session writes in a claimed worktree.

Reads the hook event on stdin. A worktree with a session marker owned by
another session refuses file edits and any shell command that is not clearly
read-only. Moving ownership (`--user-approved`) always asks the user.

  worktree_guard.py             run as the hook
  worktree_guard.py --install   copy it and finish_guard.py into ~/.claude/hooks and register both

A shell command that builds a path at run time (variables, scripts) cannot be
seen from here. File tools and ordinary shell commands are covered.
"""
from __future__ import annotations

import json
import re
import shlex
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import session_worktree as sw  # noqa: E402

FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
_READ_ONLY = {"ls", "cat", "head", "tail", "grep", "rg", "wc", "pwd", "cd", "stat", "file", "diff", "which", "echo", "true"}
_READ_ONLY_GIT = {"status", "log", "diff", "show", "rev-parse", "ls-files", "ls-tree", "blame", "grep", "cat-file", "describe"}
_SEPARATORS = {"&&", "||", ";", "|", "&"}


def _owner_of(path: Path) -> str:
    """Owner of the worktree holding `path`, or "" when unclaimed or not a worktree."""
    for folder in (path, *path.parents):
        dot_git = folder / ".git"
        if dot_git.is_dir():
            marker = dot_git / sw.MARKER_NAME
        elif dot_git.is_file():
            gitdir = dot_git.read_text(encoding="utf-8").removeprefix("gitdir:").strip()
            marker = (folder / gitdir) / sw.MARKER_NAME
        else:
            continue
        if not marker.is_file():
            return ""
        try:
            return str(json.loads(marker.read_text(encoding="utf-8")).get("owner", ""))
        except (OSError, json.JSONDecodeError):
            return "unreadable marker"
    return ""


def _words(command: str) -> list[str] | None:
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return None


def _read_only(words: list[str] | None, command: str) -> bool:
    if words is None or "$(" in command or "`" in command or any(">" in w for w in words):
        return False
    segment: list[str] = []
    for word in [*words, ";"]:
        if word not in _SEPARATORS:
            segment.append(word)
            continue
        if segment:
            name, rest = Path(segment[0]).name, segment[1:]
            if name == "git":
                while len(rest) > 1 and rest[0] == "-C":
                    rest = rest[2:]
                if not rest or rest[0] not in _READ_ONLY_GIT or any(a.startswith("--output") for a in rest):
                    return False
            elif name not in _READ_ONLY:
                return False
        segment = []
    return True


def _foreign(paths: list[Path], session: str) -> tuple[Path, str] | None:
    for path in paths:
        owner = _owner_of(path)
        if owner and owner != session:
            return path, owner
    return None


def _deny(path: Path, owner: str) -> tuple[str, str]:
    return "deny", (
        f"{path} belongs to session {owner}. Only the owner writes there. "
        "Make your own worktree, or ask the user to hand it off."
    )


def decide(event: dict) -> tuple[str, str]:
    """("allow" | "ask" | "deny", reason)."""
    session = str(event.get("session_id", ""))
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    cwd = Path(event.get("cwd") or ".").resolve()
    if tool in FILE_TOOLS:
        raw = data.get("file_path") or data.get("notebook_path") or ""
        if not raw:
            return "allow", ""
        target = (cwd / raw).resolve()
        if target.name.startswith("heyeddi-session."):
            return "deny", "the session marker is changed only by session_worktree.py"
        hit = _foreign([target], session)
        return _deny(*hit) if hit else ("allow", "")
    if tool != "Bash":
        return "allow", ""
    command = str(data.get("command", ""))
    words = _words(command)
    if "session_worktree.py" in command and "--user-approved" in command:
        return "ask", "this lets a session into another session's worktree"
    if _read_only(words, command):
        return "allow", ""
    if sw.MARKER_NAME in command:
        return "deny", "the session marker is changed only by session_worktree.py"
    paths = [cwd]
    for word in words if words is not None else command.split():
        value = word.split("=", 1)[-1]
        if "/" in value or value.startswith((".", "~")):
            paths.append((cwd / Path(value).expanduser()).resolve())
        elif re.fullmatch(r"[\w.-]+", value) and (cwd / value).is_dir():
            paths.append((cwd / value).resolve())
    hit = _foreign(paths, session)
    return _deny(*hit) if hit else ("allow", "")


def install(claude_dir: Path) -> None:
    hooks = claude_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    for name in ("worktree_guard.py", "session_worktree.py", "finish_guard.py"):
        shutil.copy2(here / name, hooks / name)
    settings = claude_dir / "settings.json"
    data = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
    entries = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
    command = f'python3 "{hooks / "worktree_guard.py"}"'
    if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
        entries.append(
            {"matcher": "Bash|Edit|Write|NotebookEdit|MultiEdit", "hooks": [{"type": "command", "command": command}]}
        )
    stops = data["hooks"].setdefault("Stop", [])
    finish = f'python3 "{hooks / "finish_guard.py"}"'
    if not any(h.get("command") == finish for e in stops for h in e.get("hooks", [])):
        stops.append({"hooks": [{"type": "command", "command": finish}]})
    settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if "--install" in sys.argv[1:]:
        install(Path.home() / ".claude")
        print("worktree guard installed. Restart open sessions to load it.")
        return 0
    try:
        decision, reason = decide(json.load(sys.stdin))
    except Exception as exc:  # a broken guard must not silently let writes through
        print(f"worktree guard failed: {exc}", file=sys.stderr)
        return 2
    if decision != "allow":
        json.dump(
            {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                    "permissionDecisionReason": reason}},
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
