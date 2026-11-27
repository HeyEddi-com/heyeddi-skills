#!/usr/bin/env python3
"""Decide whether an agent may run a command: allow, ask, or deny.

One gate for commit, push, PR, merge, release, and reads or writes against
dev / staging / prod. The policy comes from `.heyeddi/stack.json`
(see permission_policy.py). Infra writes reuse classify_command.

Exit codes with --check: 0 allow, 2 ask (one question, then rerun with
--approved), 1 deny (never run it, not even through a script).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classify_command import (  # noqa: E402
    ACTION_DENY,
    _basename,
    _substitutions,
    _tokenize,
    _unwrap,
    classify,
    split_segments,
)
from permission_policy import (  # noqa: E402
    ASK,
    AUTO,
    DENY,
    _RANK,
    ask_at_least,
    production_branches,
    detect_env,
    is_local_target,
    level_for,
    load_stack,
    protected_branches,
    resolve_policy,
)

_REMOTE_CLIS = {"gcloud", "kubectl", "bq", "gsutil", "aws", "helm", "firebase", "firebase-tools", "gam", "pulumi"}
_REMOTE_LOCAL_SUBS = {
    "config", "auth", "components", "help", "version", "info", "topic", "cheat-sheet",
    "completion", "login", "logout", "emulators:start", "emulators:exec", "init",
}
_DB_CLIS = {"psql", "mysql", "mariadb", "mongosh", "mongo", "redis-cli", "cqlsh"}
_SQL_WRITE = re.compile(
    r"\b(insert|update|delete|drop|truncate|alter|create|grant|revoke|merge|upsert|replace|copy)\b"
    r"|\.(insert|update|delete|drop|remove|replace)\w*\(",
    re.I,
)
_DESTRUCTIVE = re.compile(r"\b(destroy|delete|drop|truncate|flushall|flushdb|rm)\b", re.I)
_PUBLISH = {
    ("npm", "publish"), ("pnpm", "publish"), ("yarn", "publish"), ("bun", "publish"),
    ("cargo", "publish"), ("twine", "upload"), ("gem", "push"), ("poetry", "publish"),
    ("uv", "publish"), ("flutter", "pub"), ("dart", "pub"),
}
_GH_PR_READ = {"view", "list", "checks", "diff", "status", "checkout"}
_GH_RELEASE_READ = {"view", "list", "download"}


@dataclass
class Verdict:
    decision: str
    action: str = "local"
    env: str | None = None
    reason: str = "local command"
    hard_limit: bool = False
    details: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision,
            "action": self.action,
            "env": self.env,
            "reason": self.reason,
            "hard_limit": self.hard_limit,
        }


def _current_branch(cwd: Path | None) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


_MERGE_VALUE_FLAGS = {"-R", "--repo", "-b", "--body", "-F", "--body-file", "-t", "--subject",
                      "-A", "--author-email", "--match-head-commit"}


def _pr_base(selector: str, repo: str, cwd: Path | None) -> str:
    """Target branch of a PR, or "" when gh cannot say."""
    cmd = ["gh", "pr", "view", *([selector] if selector else []), "--json", "baseRefName", "-q", ".baseRefName"]
    if repo:
        cmd += ["--repo", repo]
    try:
        out = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _merge(tokens: list[str], policy: dict, stack: dict, cwd: Path | None, moved: bool) -> Verdict:
    """`gh pr merge`: free below production once the pre-merge gate passes; production asks."""
    selector = repo = ""
    args = iter(tokens[3:])
    for word in args:
        name, sep, value = word.partition("=")
        if name in _MERGE_VALUE_FLAGS:
            value = value if sep else next(args, "")
            if name in {"-R", "--repo"}:
                repo = value
        elif not word.startswith("-") and not selector:
            selector = word
    level = level_for(policy, "merge")
    if "--admin" in tokens:
        return Verdict(ask_at_least(level), "merge", None, "gh pr merge --admin skips required checks")
    # After a `cd` the PR lives somewhere this gate cannot see.
    base = "" if moved else _pr_base(selector, repo, cwd)
    production = production_branches(stack) | ({"main", "master"} if repo or "://" in selector else set())
    if not base or base in production:
        reason = f"merge into production branch {base}" if base else "merge into an unknown branch (treated as production)"
        return Verdict(ask_at_least(level), "merge", "prod", reason)
    return Verdict(level, "merge", None, f"merge into {base}: run pre_merge_gate --signoff first, exit 0 required")


def _gated(policy: dict, action: str, reason: str, env: str | None = None) -> Verdict:
    return Verdict(level_for(policy, action, env), action, env, reason)


def _hard(action: str, reason: str, env: str | None = None) -> Verdict:
    return Verdict(DENY, action, env, reason, hard_limit=True)


def _git(tokens: list[str], policy: dict, stack: dict, cwd: Path | None) -> Verdict | None:
    args = [t for t in tokens[1:]]
    while args and args[0] in {"-C", "-c"} and len(args) > 1:
        args = args[2:]
    if not args:
        return None
    sub, rest = args[0], args[1:]
    if sub == "commit":
        return _gated(policy, "commit", "git commit")
    if sub != "push":
        return None
    force = any(t in {"-f", "--force", "--force-with-lease", "--mirror"} or t.startswith("--force") for t in rest)
    deleting = "--delete" in rest or "-d" in rest
    positional = [t for t in rest if not t.startswith("-")]
    refspecs = positional[1:]
    if "--tags" in rest or any("refs/tags/" in r or re.fullmatch(r"\+?v?\d+(\.\d+)*\S*", r) for r in refspecs):
        return _gated(policy, "release", "git push of a tag")
    protected = protected_branches(stack)
    targets: list[str] = []
    for ref in refspecs or [_current_branch(cwd)]:
        if ref.startswith("+"):
            force = True
            ref = ref[1:]
        dest = ref.split(":", 1)[-1]
        if ref.startswith(":"):
            deleting = True
        targets.append(dest.removeprefix("refs/heads/"))
    hits = [t for t in targets if t in protected]
    if hits and (force or deleting):
        return _hard("push_protected", f"force push or delete on protected branch {hits[0]}")
    if set(targets) & production_branches(stack):
        return Verdict(ask_at_least(policy["push_protected"]), "push_protected", "prod", "push to the production branch")
    if hits:
        return _gated(policy, "push_protected", f"push to protected branch {hits[0]}")
    return _gated(policy, "push", "git push to a feature branch")


def _gh(tokens: list[str], policy: dict, stack: dict, segment: str, cwd: Path | None, moved: bool) -> Verdict | None:
    if len(tokens) < 2:
        return None
    group = tokens[1]
    sub = tokens[2] if len(tokens) > 2 else ""
    if group == "pr":
        if sub == "merge":
            return _merge(tokens, policy, stack, cwd, moved)
        if sub in _GH_PR_READ or not sub:
            return None
        return _gated(policy, "pr", f"gh pr {sub}")
    if group == "release":
        if sub in _GH_RELEASE_READ or not sub:
            return None
        return _gated(policy, "release", f"gh release {sub}")
    if group == "repo" and sub in {"delete", "archive", "rename"}:
        return _hard("repo", f"gh repo {sub}")
    if group in {"workflow", "run"} and sub in {"run", "rerun", "cancel"}:
        return _gated(policy, "pr", f"gh {group} {sub}")
    if group == "api":
        method = "GET"
        for i, tok in enumerate(tokens):
            if tok in {"-X", "--method"} and i + 1 < len(tokens):
                method = tokens[i + 1].upper()
            elif tok.startswith(("-X", "--method=")) and len(tok) > 2:
                method = tok.split("=", 1)[-1].removeprefix("-X").upper()
        if method == "GET" and any(t in {"-f", "-F", "--field", "--raw-field", "--input"} for t in tokens):
            method = "POST"
        if method == "GET":
            return None
        if "/merge" in segment:
            return Verdict(ask_at_least(level_for(policy, "merge")), "merge", "prod", f"gh api {method} merge: use gh pr merge")
        if "/releases" in segment or "/git/refs/tags" in segment:
            return _gated(policy, "release", f"gh api {method} release")
        if "/git/refs" in segment and method in {"DELETE", "PATCH"}:
            return _gated(policy, "push_protected", f"gh api {method} on a git ref")
        return _gated(policy, "pr", f"gh api {method}")
    return None


def _db(tokens: list[str], segment: str, policy: dict, stack: dict) -> Verdict:
    binary = _basename(tokens[0])
    remote_hint = any(
        t.startswith(("-h", "--host")) or "://" in t or t.startswith("$") or "_URL" in t.upper()
        for t in tokens[1:]
    )
    env = detect_env(segment, stack)
    if is_local_target(segment) or (env is None and not remote_hint):
        return Verdict(AUTO, "local", None, f"{binary} on a local database")
    env = env or "prod"
    payload_flags = {"-c", "--command", "-e", "--execute", "--eval", "-f", "--file"}
    has_payload = any(t in payload_flags or t.startswith("--eval=") for t in tokens)
    if binary == "redis-cli":
        words = {t.lower() for t in tokens[1:]}
        writes = bool(words & {"set", "del", "flushall", "flushdb", "hset", "lpush", "rpush", "expire", "rename"})
    elif has_payload:
        writes = bool(_SQL_WRITE.search(segment))
    else:
        writes = True  # an interactive session can do anything
    if not writes:
        return _gated(policy, "read", f"{binary} read on {env}", env)
    if env == "prod" and _DESTRUCTIVE.search(segment):
        return _hard("write", f"destructive {binary} statement on prod", env)
    return _gated(policy, "write", f"{binary} write on {env}", env)


def _segment(segment: str, policy: dict, stack: dict, cwd: Path | None, moved: bool = False) -> Verdict | None:
    raw = _tokenize(segment)
    if len(raw) >= 2 and (_basename(raw[0]), raw[1]) in _PUBLISH:
        return _gated(policy, "release", f"{_basename(raw[0])} {raw[1]}")
    tokens = _unwrap(raw)
    if not tokens:
        return None
    binary = _basename(tokens[0])
    if binary == "git":
        return _git(tokens, policy, stack, cwd)
    if binary == "gh":
        return _gh(tokens, policy, stack, segment, cwd, moved)
    if binary in _DB_CLIS:
        return _db(tokens, segment, policy, stack)
    if binary == "gcloud" and "sql" in tokens and "connect" in tokens:
        return _db(["psql", *tokens[1:], "--host"], segment, policy, stack)
    infra = classify(segment, cwd=cwd)
    if infra.action == ACTION_DENY:
        env = detect_env(segment, stack) or "prod"
        if env == "prod" and _DESTRUCTIVE.search(segment):
            return _hard("write", f"{infra.reason} (destructive, prod)", env)
        return _gated(policy, "write", f"{infra.reason} ({env})", env)
    if binary in _REMOTE_CLIS:
        sub = next((t for t in tokens[1:] if not t.startswith("-")), "")
        if sub in _REMOTE_LOCAL_SUBS or binary == "terraform":
            return None
        env = detect_env(segment, stack) or "prod"
        return _gated(policy, "read", f"{binary} read ({env})", env)
    return None


def check(command: str, cwd: Path | None = None, stack: dict | None = None) -> Verdict:
    stack = stack if stack is not None else load_stack(cwd)
    policy = resolve_policy(stack)
    worst = Verdict(AUTO)
    for piece in [command, *_substitutions(command)]:
        moved = False
        for segment in split_segments(piece):
            moved = moved or segment.split()[:1] in (["cd"], ["pushd"])
            verdict = _segment(segment, policy, stack, cwd, moved)
            if verdict is None:
                continue
            if _RANK[verdict.decision] > _RANK[worst.decision] or worst.action == "local":
                worst = verdict
            if worst.decision == DENY:
                return worst
    return worst


_NEXT = {
    AUTO: "Run it. No question needed.",
    ASK: "Ask the user once, then rerun with --approved and continue. Batch this question with any other open question.",
    DENY: "Do not run it, not through bash -c, a script, or an API. Hand the step to the user or the deploy pipeline and keep working on the rest.",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent permission gate (allow / ask / deny)")
    parser.add_argument("--command", required=True)
    parser.add_argument("--cwd", default="")
    parser.add_argument("--approved", action="store_true", help="The user said yes to this action in the current turn")
    parser.add_argument("--check", action="store_true", help="Exit 0 allow, 2 ask, 1 deny")
    args = parser.parse_args(argv)
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    verdict = check(args.command, cwd=cwd)
    if args.approved and verdict.decision == ASK:
        verdict.decision = AUTO
        verdict.reason += " (approved by the user)"
    payload = verdict.as_dict()
    payload["policy"] = resolve_policy(load_stack(cwd))["preset"]
    payload["next"] = _NEXT[verdict.decision]
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if not args.check:
        return 0
    return {AUTO: 0, ASK: 2, DENY: 1}[verdict.decision]


if __name__ == "__main__":
    raise SystemExit(main())
