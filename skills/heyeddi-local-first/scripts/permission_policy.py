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
        "merge": ASK,
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
_LOCAL_HOST = re.compile(r"(?<![a-z0-9.])(localhost|127\.0\.0\.1|0\.0\.0\.0|::1)(?![a-z0-9])", re.I)


def find_stack(start: Path | None) -> Path | None:
    """Walk up from `start` to the nearest `.heyeddi/stack.json`."""
    cur = (start or Path.cwd()).resolve()
    for folder in (cur, *cur.parents):
        candidate = folder / ".heyeddi" / "stack.json"
        if candidate.is_file():
            return candidate
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
    """Preset, then legacy agent.commit/push, then explicit permissions, then hard limits."""
    agent = stack.get("agent") if isinstance(stack.get("agent"), dict) else {}
    preset = agent.get("preset")
    if preset not in PRESETS:
        preset = DEFAULT_PRESET
    policy = deepcopy(PRESETS[preset])
    legacy = {k: agent[k] for k in ("commit", "push") if _valid_level(agent.get(k))}
    if "preset" not in agent and "permissions" not in agent:
        policy = _overlay(policy, legacy)
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


def detect_env(text: str, stack: dict[str, Any]) -> str | None:
    """Return dev / staging / prod for a remote target, or None when nothing names one.

    Explicit `targets` in stack.json win over name heuristics:
        "targets": {"prod": ["acme-prod-123"], "staging": ["acme-stg"]}
    """
    targets = stack.get("targets")
    if isinstance(targets, dict):
        for env in ("prod", "staging", "dev"):
            names = targets.get(env)
            if isinstance(names, list):
                for name in names:
                    if isinstance(name, str) and name and name in text:
                        return env
    for env, pattern in _ENV_PATTERNS:
        if pattern.search(text):
            return env
    return None


def is_local_target(text: str) -> bool:
    return bool(_LOCAL_HOST.search(text))


def level_for(policy: dict[str, Any], action: str, env: str | None = None) -> str:
    if action in ("read", "write"):
        return policy[action][env or "prod"]
    return policy[action]
