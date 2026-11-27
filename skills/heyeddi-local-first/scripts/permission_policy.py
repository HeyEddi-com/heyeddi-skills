"""Agent permission policy: one place that says what an agent may do without asking.

The policy lives in `.heyeddi/stack.json` under `agent`:

    "agent": {
      "preset": "balanced",              # cautious | balanced | autonomous
      "permissions": { ...overrides... }  # optional, same shape as a preset
    }

Levels: auto (do it), ask (one question to the user), deny (never).
Hard limits apply after the preset and overrides. No preset can lift them.
"""
from __future__ import annotations

import json
import re
import shlex
from copy import deepcopy
from pathlib import Path
from typing import Any

AUTO = "auto"
ASK = "ask"
DENY = "deny"
LEVELS = (AUTO, ASK, DENY)
_RANK = {AUTO: 0, ASK: 1, DENY: 2}

ACTIONS = ("commit", "push", "push_protected", "pr", "merge", "release")
ENVS = ("dev", "staging", "prod")
DEFAULT_PRESET = "balanced"

PRESETS: dict[str, dict[str, Any]] = {
    "cautious": {
        "commit": ASK,
        "push": ASK,
        "push_protected": ASK,
        "pr": ASK,
        "merge": ASK,
        "release": ASK,
        "read": {"dev": AUTO, "staging": ASK, "prod": ASK},
        "write": {"dev": ASK, "staging": DENY, "prod": DENY},
    },
    "balanced": {
        "commit": AUTO,
        "push": AUTO,
        "push_protected": ASK,
        "pr": AUTO,
        "merge": AUTO,
        "release": ASK,
        "read": {"dev": AUTO, "staging": AUTO, "prod": AUTO},
        "write": {"dev": AUTO, "staging": ASK, "prod": DENY},
    },
    "autonomous": {
        "commit": AUTO,
        "push": AUTO,
        "push_protected": AUTO,
        "pr": AUTO,
        "merge": AUTO,
        "release": AUTO,
        "read": {"dev": AUTO, "staging": AUTO, "prod": AUTO},
        "write": {"dev": AUTO, "staging": AUTO, "prod": ASK},
    },
}

# Hard limit: a prod write is never better than "ask", whatever the preset says.
PROD_WRITE_FLOOR = ASK

_ENV_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("prod", re.compile(r"(?<![a-z0-9])(prod|production|prd)(?![a-z0-9])", re.I)),
    ("staging", re.compile(r"(?<![a-z0-9])(staging|stage|stg|preprod|uat)(?![a-z0-9])", re.I)),
    ("dev", re.compile(r"(?<![a-z0-9])(dev|development|sandbox|test|qa)(?![a-z0-9])", re.I)),
)
# Flags whose value says where a command runs. Only these can make a command laxer.
_TARGET_FLAGS = frozenset({
    "--project", "--context", "--kube-context", "--cluster", "--host", "-h", "--profile",
    "--stack", "--environment", "--env", "--instance", "--database", "--dbname", "-d",
    "--site", "--target", "--server", "--url", "--account",
})
_LOCAL_HOST = re.compile(r"(?<![a-z0-9.])(localhost|127\.0\.0\.1|0\.0\.0\.0|::1)(?![a-z0-9])", re.I)


def find_stack(start: Path | None) -> Path | None:
    """Walk up from `start` to the nearest `.heyeddi/stack.json`."""
    cur = (start or Path.cwd()).resolve()
    for folder in (cur, *cur.parents):
        candidate = folder / ".heyeddi" / "stack.json"
        if candidate.is_file():
            return candidate
    # A linked worktree does not carry an ignored stack.json: read the main checkout's.
    for folder in (cur, *cur.parents):
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


def load_stack(start: Path | None) -> dict[str, Any]:
    path = find_stack(start)
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _valid_level(value: Any) -> bool:
    return isinstance(value, str) and value in LEVELS


def _overlay(base: dict[str, Any], patch: Any) -> dict[str, Any]:
    out = deepcopy(base)
    if not isinstance(patch, dict):
        return out
    for key, value in patch.items():
        if key in ("read", "write") and isinstance(value, dict):
            for env, level in value.items():
                if env in ENVS and _valid_level(level):
                    out[key][env] = level
        elif key in ACTIONS and _valid_level(value):
            out[key] = value
    return out


def resolve_policy(stack: dict[str, Any]) -> dict[str, Any]:
    """Preset, then explicit permissions, then hard limits.

    The old `agent.commit` / `agent.push` keys are ignored. Setup used to write
    `ask` into every repo, which stopped agents on routine commits and pushes.
    """
    agent = stack.get("agent") if isinstance(stack.get("agent"), dict) else {}
    preset = agent.get("preset")
    if preset not in PRESETS:
        preset = DEFAULT_PRESET
    policy = deepcopy(PRESETS[preset])
    policy = _overlay(policy, agent.get("permissions"))
    if _RANK[policy["write"]["prod"]] < _RANK[PROD_WRITE_FLOOR]:
        policy["write"]["prod"] = PROD_WRITE_FLOOR
    policy["preset"] = preset
    return policy


def protected_branches(stack: dict[str, Any]) -> set[str]:
    git = stack.get("git") if isinstance(stack.get("git"), dict) else {}
    names = {"main", "master"}
    envs = git.get("environments")
    if isinstance(envs, dict):
        for env, branch in envs.items():
            if env in ("production", "staging") and isinstance(branch, str) and branch:
                names.add(branch)
    default = git.get("default_branch")
    if isinstance(default, str) and default:
        names.add(default)
    return names


def shell_words(text: str) -> list[str] | None:
    """Shell words with quotes removed and `# comments` dropped. None when it will not parse."""
    try:
        return shlex.split(text, comments=True, posix=True)
    except ValueError:
        return None


def target_values(words: list[str]) -> list[str]:
    """Values that name where a command runs: target flags, connection URLs, URL env vars.

    Only these may make a command laxer (dev / staging / local). Labels, tags,
    descriptions, and comments never do.
    """
    out: list[str] = []
    for i, word in enumerate(words):
        name, sep, value = word.partition("=")
        if name in _TARGET_FLAGS:
            if sep:
                out.append(value)
            elif i + 1 < len(words):
                out.append(words[i + 1])
        elif "://" in word or (word.startswith("$") and "URL" in word.upper()):
            out.append(word)
    return out


def _env_of(value: str, stack: dict[str, Any]) -> str | None:
    targets = stack.get("targets")
    if isinstance(targets, dict):
        for env in ("prod", "staging", "dev"):
            names = targets.get(env)
            if isinstance(names, list) and any(isinstance(n, str) and n and n in value for n in names):
                return env
    for env, pattern in _ENV_PATTERNS:
        if pattern.search(value):
            return env
    return None


def detect_env(text: str, stack: dict[str, Any]) -> str | None:
    """Return dev / staging / prod for a remote target, or None when nothing names one.

    Fail closed. A prod name anywhere in the shell words makes it prod. Dev or
    staging come only from target values (`target_values`), and only when every
    target value agrees; an IP or an unnamed target means None (treated as prod).
    Explicit `targets` in stack.json win over name heuristics:
        "targets": {"prod": ["acme-prod-123"], "staging": ["acme-stg"]}
    """
    words = shell_words(text)
    if words is None:
        return None
    if any(_env_of(word, stack) == "prod" for word in words):
        return "prod"
    found = {_env_of(value, stack) for value in target_values(words)}
    if not found or None in found:
        return None
    return "staging" if "staging" in found else found.pop()


_DB_NAME_FLAGS = ("-d", "--dbname", "--database")
# Must not start with "-": that is the next flag (maybe the real --host), not a database name.
_PLAIN_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")


def _without_db_names(words: list[str], stack: dict[str, Any]) -> list[str]:
    """Drop `-d appdb`: a plain database name does not say which server is used.

    A connection string, a URL, or a name that says prod or staging is kept.
    """
    # A `host=` connection string anywhere may override the host flag: drop nothing.
    if any(re.search(r"\bhost(addr)?=", word) for word in words):
        return words
    out: list[str] = []
    skip = False
    for i, word in enumerate(words):
        if skip:
            skip = False
            continue
        flag, sep, value = word.partition("=")
        if flag in _DB_NAME_FLAGS:
            name = value if sep else (words[i + 1] if i + 1 < len(words) else "")
            if _PLAIN_NAME.fullmatch(name) and _env_of(name, stack) not in ("prod", "staging"):
                skip = not sep
                continue
        out.append(word)
    return out


def is_local_target(text: str, stack: dict[str, Any] | None = None) -> bool:
    """True only when every target value is a local host. Comments and labels do not count."""
    words = shell_words(text)
    if words is None:
        return False
    values = target_values(_without_db_names(words, stack or {}))
    return bool(values) and all(_LOCAL_HOST.search(value) for value in values)


def production_branches(stack: dict[str, Any]) -> set[str]:
    """Branches that deploy production. main and master when stack.json names none."""
    git = stack.get("git") if isinstance(stack.get("git"), dict) else {}
    envs = git.get("environments") if isinstance(git.get("environments"), dict) else {}
    name = envs.get("production")
    return {name} if isinstance(name, str) and name else {"main", "master"}


def ask_at_least(level: str) -> str:
    """Hard limit for production: never better than "ask", whatever the preset says."""
    return level if _RANK[level] >= _RANK[ASK] else ASK


def level_for(policy: dict[str, Any], action: str, env: str | None = None) -> str:
    if action in ("read", "write"):
        return policy[action][env or "prod"]
    return policy[action]
