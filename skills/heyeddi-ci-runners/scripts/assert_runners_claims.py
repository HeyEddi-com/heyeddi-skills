#!/usr/bin/env python3
"""Block unsubstantiated Spot execution claims — require Check/Spot evidence."""
from __future__ import annotations

import argparse
import json
import re
import sys

from _skill_cli import emit

CLAIM_RE = re.compile(
    r"\b("
    r"job(s)?\s+(ran|succeeded|passed|completed|failed|dispatched)|"
    r"runner(s)?\s+(executed|ran)|"
    r"spot\s+(job|run)\s+(succeeded|passed|failed|ran)|"
    r"pipeline\s+(executed|ran|succeeded|passed)"
    r")\b",
    re.I,
)

EVIDENCE_RE = re.compile(
    r"("
    r"HeyEddi Runner:|"
    r"gh\s+pr\s+checks|"
    r"check(s)?\s+(passed|failed|succeeded|neutral|cancelled)|"
    r"conclusion\s*[:=]|"
    r"detailsUrl|"
    r"spot-jobs/|"
    r"stdout\.log|"
    r"workflow\s+run"
    r")",
    re.I,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail when agent text claims Spot/GHA jobs ran without Check evidence"
    )
    parser.add_argument(
        "--agent-text",
        default="",
        help="Draft reply or summary to scan for unsubstantiated execution claims",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 on forbidden claims")
    args = parser.parse_args()
    text = args.agent_text or ""
    hit = CLAIM_RE.search(text)
    has_evidence = bool(EVIDENCE_RE.search(text))
    blocked = bool(hit) and not has_evidence
    payload = {
        "placeholder": False,
        "execution_available": True,
        "claim_detected": bool(hit),
        "evidence_detected": has_evidence,
        "blocked": blocked,
        "match": hit.group(0) if hit else None,
        "message": (
            "Spot runners are shipped. Jobs can run for entitled workspaces. "
            "Only claim a job ran when Check/Spot evidence is present "
            "(e.g. 'HeyEddi Runner: …', gh pr checks, conclusion). "
            "YAML lint alone is not execution."
        ),
    }
    emit(json.dumps(payload, indent=2))
    if args.check and blocked:
        print(
            "BLOCKED: execution claim without Check/Spot evidence",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
