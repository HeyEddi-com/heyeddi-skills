#!/usr/bin/env python3
"""Claude Code Stop hook: a turn may not end waiting for a "go".

It blocks once and sends the agent back to work. If the agent stops again
(`stop_hook_active`), the stop goes through, so a real question still reaches
the user. Installed by `worktree_guard.py --install`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# A "go" the agent waits for, not the Go language: quoted, "go-ahead", or lowercase `go`
# followed by what ends a request ("your go.", "on your go", "your go before ...").
_GO_NEXT = r"(?=\s*(?:$|[,!?;:)]|\.(?!\w))|\s+(?:on|before|to|and|first)\b)"
WAITING = re.compile(
    r"waiting (for|on) (your|you)\b|if you say\b"
    r"|\b(your|the) (?:[\"'\u2018\u201c]go[\"'\u2019\u201d]|go[- ]ahead\b)"
    rf"|\byour (?-i:go){_GO_NEXT}"
    rf"|\b(?:wait\w*|await\w*|need\w*)\b[^.\n]{{0,30}}\bthe (?-i:go){_GO_NEXT}"
    rf"|\bsay [\"']?(?-i:go)\b[\"']?{_GO_NEXT}"
    r"|\b(should|shall|can|may) i\b[^.\n]*\?|\b(want|would you like) me to\b|let me know (if|when|whether)",
    re.IGNORECASE,
)
# The one wait that is correct.
ALLOWED = re.compile(r"authorize merge", re.IGNORECASE)

REASON = (
    "Do not stop to wait for a go. A request or an approved plan covers every step in it: "
    "do the next step now. Ask only what check_permission marks ask or deny, or a login you do not have."
)


def _last_text(event: dict) -> str:
    if event.get("last_assistant_message"):
        return str(event["last_assistant_message"])
    path = Path(str(event.get("transcript_path") or ""))
    if not path.is_file():
        return ""
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("type") != "assistant":
            continue
        parts = (row.get("message") or {}).get("content") or []
        text = "\n".join(p.get("text", "") for p in parts if isinstance(p, dict))
        if text.strip():
            return text
    return ""


def decide(event: dict) -> str:
    """The reason to keep working, or "" to let the turn end."""
    if event.get("stop_hook_active"):
        return ""
    ending = _last_text(event)[-600:]
    return REASON if WAITING.search(ending) and not ALLOWED.search(ending) else ""


if __name__ == "__main__":
    reason = decide(json.load(sys.stdin))
    if reason:
        json.dump({"decision": "block", "reason": reason}, sys.stdout)
