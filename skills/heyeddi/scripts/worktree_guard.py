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
# Redirects that write nowhere. A backslash before one changes its meaning, so it must follow a space.
_NO_WRITE_REDIRECT = re.compile(r"(?<!\S)(?:[12]?>{1,2}[ \t]*/dev/null|&>[ \t]*/dev/null|[12]?>&[12])(?=$|[\s;&|])")
_GH_PR_LOOK = {"view", "list", "checks", "diff", "status"}
_WORKTREE_ADD_FLAGS = {"--detach", "-d", "--track", "--no-track", "-q", "--quiet", "--lock", "--checkout", "--no-checkout"}
_FETCH_FLAGS = {"--all", "--prune", "-p", "--tags", "-t", "--no-tags", "-q", "--quiet", "-v", "--verbose"}
_CLAIM_FLAGS = {"--path", "--task", "--pr", "--session"}  # exact: argparse accepts abbreviations
_BRANCH_LOOK_FLAGS = {"--list", "-a", "--all", "-r", "--remotes", "--show-current", "-v", "-vv", "--verbose", "--no-color"}


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


def _words(command: str, comments: bool = True) -> list[str] | None:
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    if not comments:  # newlines are already gone, so a comment would hide every later line
        lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:
        return None


def _resolve(base: Path, value: str, moved: bool) -> Path | None:
    """A path argument, or None when it cannot be known (relative after a `cd`, or a variable)."""
    path = Path(value).expanduser()
    if "$" in value or (moved and not path.is_absolute()):
        return None
    return (base / path).resolve()


def _not_foreign(path: Path | None, session: str) -> bool:
    return path is not None and _owner_of(path) in ("", session)


def _adds_own_worktree(args: list[str], base: Path, session: str, moved: bool) -> bool:
    """`git worktree add` that creates a new folder outside any foreign worktree."""
    positional: list[str] = []
    words = iter(args)
    for word in words:
        if word == "-b":  # -b fails on an existing branch; -B and -f would move or reuse one.
            next(words, "")
        elif word.startswith("-"):
            if word not in _WORKTREE_ADD_FLAGS:
                return False
        else:
            positional.append(word)
    return len(positional) in (1, 2) and _not_foreign(_resolve(base, positional[0], moved), session)


def _safe_git(args: list[str], base: Path, session: str, moved: bool) -> bool:
    while len(args) > 1 and args[0] == "-C":
        entered = _resolve(base, args[1], moved)
        if entered is None:
            return False
        base, args = entered, args[2:]
    if not args:
        return False
    sub, rest = args[0], args[1:]
    if sub == "grep" and any(a.startswith(("-O", "--open-files-in-pager")) for a in rest):
        return False
    if sub in _READ_ONLY_GIT:
        return not any(a.startswith("--output") for a in rest)
    if sub == "worktree" and rest:
        if rest[0] == "list":
            return all(a in {"--porcelain", "-v", "--verbose", "-z"} for a in rest[1:])
        return rest[0] == "add" and _adds_own_worktree(rest[1:], base, session, moved)
    if sub == "fetch":  # Remote-tracking refs only: no refspec may write a local branch.
        return all(a in _FETCH_FLAGS or re.fullmatch(r"[A-Za-z0-9_][\w./-]*", a) for a in rest)
    if sub == "branch":
        flags = [a for a in rest if a.startswith("-")]
        return all(f in _BRANCH_LOOK_FLAGS for f in flags) and (len(flags) == len(rest) or "--list" in flags)
    return False


def _safe_session_script(args: list[str], base: Path, session: str, moved: bool) -> bool:
    """`session_worktree.py list | check`, or `claim` of a worktree that is not someone else's."""
    if len(args) < 2 or args[0].startswith("-"):
        return False
    script = _resolve(base, args[0], moved)
    if script is None or script.name != "session_worktree.py":
        return False
    try:
        if script.read_bytes() != Path(sw.__file__).read_bytes():
            return False
        # A module beside the script must not shadow one it imports.
        if any(p.stem in sys.stdlib_module_names for p in script.parent.iterdir()):
            return False
    except OSError:
        return False
    sub, rest = args[1], args[2:]
    if sub in {"list", "check"}:
        return True
    flags = [a for a in rest if a.startswith("-")]
    if sub != "claim" or "--path" not in rest[:-1] or any(f not in _CLAIM_FLAGS for f in flags):
        return False
    paths = [rest[i + 1] for i, a in enumerate(rest[:-1]) if a == "--path"]
    return all(_not_foreign(_resolve(base, p, moved), session) for p in paths)


def _read_only(command: str, cwd: Path, session: str) -> bool:
    """True when nothing here can change another session's worktree."""
    if "$(" in command or "`" in command or "<(" in command:
        return False
    words = _words(_NO_WRITE_REDIRECT.sub(" ", command), comments=False)
    if words is None or any(">" in w for w in words):
        return False
    segment: list[str] = []
    moved = False
    for word in [*words, ";"]:
        if word not in _SEPARATORS:
            segment.append(word)
            continue
        if segment:
            name, rest = Path(segment[0]).name, segment[1:]
            if name == "git":
                if not _safe_git(rest, cwd, session, moved):
                    return False
            elif name == "gh":
                if len(rest) < 2 or rest[0] != "pr" or rest[1] not in _GH_PR_LOOK:
                    return False
            elif name in {"python", "python3"}:
                if not _safe_session_script(rest, cwd, session, moved):
                    return False
            elif name not in _READ_ONLY or (name == "rg" and any(a.startswith("--pre") for a in rest)):
                return False
            moved = moved or name == "cd"
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
    if _read_only(command, cwd, session):
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
