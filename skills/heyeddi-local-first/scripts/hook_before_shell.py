#!/usr/bin/env python3
"""Cursor beforeShellExecution hook. Deny live mutations. Allow terraform plan."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classify_command import ACTION_DENY, ACTION_PLAN, classify  # noqa: E402


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
    decision = classify(command, cwd=_cwd(payload))
    if decision.action == ACTION_DENY:
        message = (
            f"Blocked live change: {decision.reason}. "
            "Edit the config locally. terraform plan is allowed. "
            "Apply runs in Cloud Build after review, or in a terminal you run yourself."
        )
        out = {
            "permission": "deny",
            "user_message": message,
            "agent_message": message + " Do not retry through bash -c, a script, or an API write.",
        }
    elif decision.action == ACTION_PLAN:
        message = (
            f"{decision.reason}. "
            "When the output returns, warn the user what would be created, changed, or destroyed. "
            "Do not apply."
        )
        out = {
            "permission": "allow",
            "user_message": "Plan only. This does not change live infrastructure.",
            "agent_message": message,
        }
    else:
        out = {"permission": "allow"}
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
