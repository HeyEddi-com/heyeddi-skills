"""Canonical `.heyeddi/stack.json` prefs schema for @heyeddi-setup.

Tech keys (frontend, backends, package manager, CI) are owned by scaffold /
engineering / CI skills and are NOT required by setup verify.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

SETUP_SCHEMA_VERSION = 1

GIT_PRESETS = ("main_staging_dev", "main_dev", "custom")
ASK_AUTO = ("ask", "auto")

# Env maps for presets (always include production + staging).
PRESET_ENVIRONMENTS: dict[str, dict[str, str]] = {
    "main_staging_dev": {
        "production": "main",
        "staging": "staging",
        "dev": "dev",
    },
    "main_dev": {
        "production": "main",
        "staging": "dev",
    },
}

PRESET_PR_BASE: dict[str, str] = {
    "main_staging_dev": "dev",
    "main_dev": "dev",
}

PRESET_DEFAULT_BRANCH: dict[str, str] = {
    "main_staging_dev": "dev",
    "main_dev": "dev",
}

# Required after @heyeddi-setup (prefs only).
REQUIRED_PATHS: tuple[str, ...] = (
    "git.preset",
    "git.pr_base",
    "git.default_branch",
    "git.environments.production",
    "git.environments.staging",
    "git.worktrees",
    "git.custom_workflow",
    "agent.commit",
    "agent.push",
    "setup.version",
    "setup.updated",
)

DEFAULTS: dict[str, Any] = {
    "git": {
        "preset": "main_staging_dev",
        "default_branch": "dev",
        "pr_base": "dev",
        "environments": dict(PRESET_ENVIRONMENTS["main_staging_dev"]),
        "worktrees": False,
        "custom_workflow": None,
    },
    "agent": {
        "commit": "ask",
        "push": "ask",
    },
    "setup": {
        "version": SETUP_SCHEMA_VERSION,
        "updated": "",
    },
}

QUESTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "git.preset",
        "path": "git.preset",
        "prompt": "Env / branch layout? (always at least production + staging)",
        "choices": ["main_staging_dev", "main_dev"],
        "hints": {
            "main_staging_dev": "prod←main, staging←staging, dev←dev (default)",
            "main_dev": "prod←main, staging←dev (no separate staging branch)",
        },
        "group": "git",
    },
    {
        "id": "git.custom_workflow",
        "path": "git.custom_workflow",
        "prompt": "Different workflow than the preset? (no / describe: gitflow, trunk+tags, …)",
        "choices": [None, "custom"],
        "allow_freeform": True,
        "hints": {
            "null": "Use the preset as-is",
            "custom": "Store a short description; sets preset to custom",
        },
        "group": "git",
    },
    {
        "id": "git.worktrees",
        "path": "git.worktrees",
        "prompt": "Use git worktrees for parallel features?",
        "choices": [True, False],
        "group": "git",
    },
    {
        "id": "agent.commit",
        "path": "agent.commit",
        "prompt": "Agent may commit without asking?",
        "choices": list(ASK_AUTO),
        "hints": {"ask": "confirm first", "auto": "commit on feature branches OK"},
        "group": "agent",
    },
    {
        "id": "agent.push",
        "path": "agent.push",
        "prompt": "Agent may push without asking?",
        "choices": list(ASK_AUTO),
        "hints": {"ask": "confirm first", "auto": "push feature branches OK"},
        "group": "agent",
    },
)


def get_path(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def set_path(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur = data
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def environments_for_preset(preset: str) -> dict[str, str] | None:
    return deepcopy(PRESET_ENVIRONMENTS.get(preset))


def apply_preset(data: dict[str, Any], preset: str) -> dict[str, Any]:
    """Fill git.environments / pr_base / default_branch from a known preset."""
    out = deepcopy(data)
    if preset == "custom":
        set_path(out, "git.preset", "custom")
        return out
    envs = environments_for_preset(preset)
    if envs is None:
        raise ValueError(f"unknown git.preset: {preset!r}")
    set_path(out, "git.preset", preset)
    set_path(out, "git.environments", envs)
    set_path(out, "git.pr_base", PRESET_PR_BASE[preset])
    set_path(out, "git.default_branch", PRESET_DEFAULT_BRANCH[preset])
    if get_path(out, "git.custom_workflow") is None:
        set_path(out, "git.custom_workflow", None)
    return out


def normalize_custom_workflow(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None if raw is False else "custom"
    if isinstance(raw, str):
        low = raw.strip().lower()
        if low in ("", "no", "none", "null", "n", "false", "default", "preset"):
            return None
        if low in ("yes", "y", "true", "custom"):
            return "custom"
        return raw.strip()
    return None


def validate_value(path: str, value: Any) -> str | None:
    if path == "git.preset":
        if value not in GIT_PRESETS:
            return f"git.preset must be one of {GIT_PRESETS}"
        return None
    if path in ("git.default_branch", "git.pr_base"):
        if not isinstance(value, str) or not value.strip():
            return f"{path} must be a non-empty string"
        return None
    if path == "git.environments.production" or path == "git.environments.staging":
        if not isinstance(value, str) or not value.strip():
            return f"{path} must be a non-empty branch name"
        return None
    if path == "git.environments.dev":
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            return "git.environments.dev must be a non-empty branch name when set"
        return None
    if path == "git.worktrees":
        if not isinstance(value, bool):
            return "git.worktrees must be true or false"
        return None
    if path == "git.custom_workflow":
        if value is None:
            return None
        if not isinstance(value, str):
            return "git.custom_workflow must be null or a string"
        return None
    if path in ("agent.commit", "agent.push"):
        if value not in ASK_AUTO:
            return f"{path} must be ask or auto"
        return None
    if path == "setup.version":
        # bool is a subclass of int; reject True/False explicitly
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            return "setup.version must be a positive int"
        return None
    if path == "setup.updated":
        if not isinstance(value, str) or not value.strip():
            return "setup.updated must be a non-empty date string"
        return None
    return f"unknown path: {path}"


def missing_paths(data: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for path in REQUIRED_PATHS:
        value = get_path(data, path)
        # custom_workflow may be explicitly null
        if path == "git.custom_workflow":
            if "git" not in data or not isinstance(data.get("git"), dict):
                missing.append(path)
                continue
            if "custom_workflow" not in data["git"]:
                missing.append(path)
                continue
            err = validate_value(path, value)
            if err:
                missing.append(path)
            continue
        if value is None:
            missing.append(path)
            continue
        err = validate_value(path, value)
        if err:
            missing.append(path)
    # production + staging always required inside environments object
    envs = get_path(data, "git.environments")
    if not isinstance(envs, dict):
        if "git.environments.production" not in missing:
            missing.append("git.environments.production")
        if "git.environments.staging" not in missing:
            missing.append("git.environments.staging")
    return missing


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, val in patch.items():
        if key in out and isinstance(out[key], dict) and isinstance(val, dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = deepcopy(val)
    return out


def apply_answers(data: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    """Apply question-id or dotted-path answers onto stack data."""
    out = deepcopy(data)
    pending = dict(answers)

    preset_key = None
    if "git.preset" in pending:
        preset_key = "git.preset"
    elif "preset" in pending:
        preset_key = "preset"
    if preset_key is not None:
        out = apply_preset(out, str(pending.pop(preset_key)).strip())

    custom_key = None
    if "git.custom_workflow" in pending:
        custom_key = "git.custom_workflow"
    elif "custom_workflow" in pending:
        custom_key = "custom_workflow"
    if custom_key is not None:
        custom = normalize_custom_workflow(pending.pop(custom_key))
        set_path(out, "git.custom_workflow", custom)
        if custom is not None:
            set_path(out, "git.preset", "custom")
            envs = get_path(out, "git.environments")
            if not isinstance(envs, dict):
                set_path(
                    out,
                    "git.environments",
                    {"production": "main", "staging": "staging"},
                )
            else:
                envs = dict(envs)
                if not envs.get("production"):
                    envs["production"] = "main"
                if not envs.get("staging"):
                    envs["staging"] = envs.get("dev") or "staging"
                set_path(out, "git.environments", envs)
            if not get_path(out, "git.pr_base"):
                set_path(out, "git.pr_base", "dev")
            if not get_path(out, "git.default_branch"):
                set_path(out, "git.default_branch", "dev")

    for key, raw in pending.items():
        path = key
        for q in QUESTIONS:
            if q["id"] == key:
                path = q["path"]
                break
        value: Any = raw
        if path == "git.worktrees":
            if isinstance(raw, str):
                low = raw.strip().lower()
                if low in ("yes", "true", "1", "y"):
                    value = True
                elif low in ("no", "false", "0", "n"):
                    value = False
                else:
                    raise ValueError(f"invalid git.worktrees: {raw!r}")
            elif not isinstance(raw, bool):
                raise ValueError(f"invalid git.worktrees: {raw!r}")
        err = validate_value(path, value)
        if err:
            raise ValueError(err)
        set_path(out, path, value)

    if isinstance(out.get("git"), dict) and "custom_workflow" not in out["git"]:
        out["git"]["custom_workflow"] = None

    return out


def ensure_prefs_defaults(data: dict[str, Any]) -> dict[str, Any]:
    """Fill missing git/agent shells without inventing a preset the user did not choose."""
    out = deepcopy(data)
    if not isinstance(out.get("git"), dict):
        out["git"] = {}
    if not isinstance(out.get("agent"), dict):
        out["agent"] = {}
    return out


def stamp_setup(data: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(data)
    set_path(out, "setup.version", SETUP_SCHEMA_VERSION)
    set_path(out, "setup.updated", date.today().isoformat())
    return out


def questions_with_state(data: dict[str, Any], *, missing_only: bool) -> list[dict[str, Any]]:
    missing = set(missing_paths(data))
    rows: list[dict[str, Any]] = []
    for q in QUESTIONS:
        path = q["path"]
        current = get_path(data, path)
        is_missing = path in missing
        if missing_only and not is_missing:
            continue
        default = get_path(DEFAULTS, path)
        rows.append(
            {
                **q,
                "current": current,
                "default": current if not is_missing else default,
                "missing": is_missing,
            }
        )
    return rows
