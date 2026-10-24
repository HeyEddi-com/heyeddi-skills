#!/usr/bin/env python3
"""Cursor beforeMCPExecution hook. Deny infra deploys and commands hidden in tool args."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classify_command import ACTION_DENY, classify  # noqa: E402

_FIREBASE_WRITE = re.compile(
    r"firebase_(deploy|create_project|create_app|create_android_sha|update_environment|init)\b",
    re.IGNORECASE,
)


def _strings(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_strings(item))
    return found


def _tool_name(payload: dict) -> str:
    for key in ("tool_name", "toolName", "name", "tool"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    name = _tool_name(payload)
    if _FIREBASE_WRITE.search(name):
        message = (
            f"Blocked live change: MCP tool {name} writes Firebase or Google Cloud. "
            "Edit the config locally and deploy through the reviewed pipeline."
        )
        json.dump(
            {
                "permission": "deny",
                "user_message": message,
                "agent_message": message,
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 0
    for text in _strings(payload):
        if len(text) > 4000:
            continue
        decision = classify(text)
        if decision.action == ACTION_DENY:
            message = (
                f"Blocked live change inside MCP arguments: {decision.reason}. "
                "Edit the config locally."
            )
            json.dump(
                {
                    "permission": "deny",
                    "user_message": message,
                    "agent_message": message + " Do not retry through another tool.",
                },
                sys.stdout,
            )
            sys.stdout.write("\n")
            return 0
    json.dump({"permission": "allow"}, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
