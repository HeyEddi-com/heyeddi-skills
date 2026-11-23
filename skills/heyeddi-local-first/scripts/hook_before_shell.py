#!/usr/bin/env python3
"""Cursor beforeShellExecution hook. Applies the agent permission policy (allow / ask / deny)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_permission import check  # noqa: E402
from classify_command import ACTION_PLAN, classify  # noqa: E402
from permission_policy import ASK, DENY  # noqa: E402


def _command(payload: dict) -> str:
    for key in ("command", "cmd", "shell_command"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _cwd(payload: dict) -> Path | None:
    for key in ("cwd", "working_directory", "workingDirectory"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value)
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    command = _command(payload)
    cwd = _cwd(payload)
    verdict = check(command, cwd=cwd)
    if verdict.decision == DENY:
        message = (
            f"Blocked: {verdict.reason}. "
            "Live prod changes run in the deploy pipeline or in a terminal you run yourself. "
            "terraform plan is allowed."
        )
        out = {
            "permission": "deny",
            "user_message": message,
            "agent_message": message
            + " Do not retry through bash -c, a script, or an API write. Keep working on the rest of the task.",
        }
    elif verdict.decision == ASK:
        out = {
            "permission": "ask",
            "user_message": f"Agent wants to run: {verdict.reason}. Allow?",
            "agent_message": f"{verdict.reason} needs one yes from the user (agent.permissions in .heyeddi/stack.json).",
        }
    elif classify(command, cwd=cwd).action == ACTION_PLAN:
        out = {
            "permission": "allow",
            "user_message": "Plan only. This does not change live infrastructure.",
            "agent_message": "When the output returns, warn the user what would be created, changed, or destroyed. Do not apply.",
        }
    else:
        out = {"permission": "allow"}
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
