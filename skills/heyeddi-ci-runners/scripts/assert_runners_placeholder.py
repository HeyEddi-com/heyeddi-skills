#!/usr/bin/env python3
"""Assert Spot runners remain fail-closed / placeholder — never claim jobs ran."""
from __future__ import annotations

import argparse
import json
import re
import sys

from _skill_cli import emit

CLAIM_RE = re.compile(
    r"\b(job(s)?\s+(ran|succeeded|passed|completed)|runner(s)?\s+(executed|ran)|"
    r"spot\s+(job|run)\s+(succeeded|passed)|pipeline\s+(executed|ran))\b",
    re.I,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed assertion for runners placeholder")
    parser.add_argument(
        "--agent-text",
        default="",
        help="Draft reply or summary to scan for false execution claims",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 on forbidden claims")
    args = parser.parse_args()
    text = args.agent_text or ""
    hit = CLAIM_RE.search(text)
    payload = {
        "placeholder": True,
        "execution_available": False,
        "claim_detected": bool(hit),
        "match": hit.group(0) if hit else None,
        "message": (
            "Spot runners are PLACEHOLDER / fail-closed. Author valid pipeline YAML only. "
            "Never claim jobs ran, succeeded, or were dispatched."
        ),
    }
    emit(json.dumps(payload, indent=2))
    if args.check and hit:
        print("BLOCKED: runners are placeholder — do not claim execution", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
