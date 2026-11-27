#!/usr/bin/env python3
"""Plan gate: engineering docs ready + optional plan smell check (always-on)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _heyeddi_paths import engineering_docs_dir
from _skill_cli import emit, fail, resolve_project_root

REQUIRED_DOCS = ("architecture.md", "reuse-catalog.md", "decisions.md")
ABSTRACTION_SMELL = re.compile(
    r"(\w*Factory|\w*Manager|\bOrchestrator\b|\bAbstract[A-Z]\w*|\bBase[A-Z]\w+Service\b)"
)
REUSE_HINT = re.compile(r"\b(reuse|reuse-catalog|existing|second call site|YAGNI|DRY)\b", re.I)
COST_DRIVER = re.compile(
    r"(min[_ -]?instances?|always[- ]on|\bGKE\b|Kubernetes|Cloud NAT|NAT gateway|Cloud SQL|AlloyDB|"
    r"Spanner|Redis|Memorystore|load balancer|Firestore|onSnapshot|listener|realtime|real-time|\bcron\b|polling|setInterval|\bLLM\b|claude-|gpt-|\bGPU\b|"
    r"macos runner|larger runner)",
    re.I,
)
POLL_WORK = re.compile(
    r"(\bcron\b|polling|setInterval|Cloud Scheduler|scheduled job|"
    r"every \d+ ?(?:s|sec|secs|seconds?|min|mins|minutes?)\b|every (?:second|minute))",
    re.I,
)
EVENT_PATH = re.compile(
    r"(Cloud Tasks|Pub/?Sub|Eventarc|webhook|log sink|event[- ]driven|due time|backstop)", re.I
)
COST_HINT = re.compile(r"(\bcost|\bbudget|\$\s?\d|per month|/mo\b|estimate_change_cost)", re.I)


def _docs_status(root: Path) -> list[dict]:
    eng = engineering_docs_dir(root)
    findings: list[dict] = []
    for name in REQUIRED_DOCS:
        path = eng / name
        if not path.is_file():
            findings.append(
                {
                    "principle": "Documentation",
                    "severity": "error",
                    "file": f".heyeddi/docs/engineering/{name}",
                    "message": "Missing: run init_engineering_docs.py before implementing",
                }
            )
        elif path.stat().st_size < 100:
            findings.append(
                {
                    "principle": "Documentation",
                    "severity": "warn",
                    "file": f".heyeddi/docs/engineering/{name}",
                    "message": "Stub doc: expand before large features",
                }
            )
    return findings


def _plan_smells(plan_text: str, plan_label: str) -> list[dict]:
    findings: list[dict] = []
    if not plan_text.strip():
        return findings
    if ABSTRACTION_SMELL.search(plan_text) and not REUSE_HINT.search(plan_text):
        findings.append(
            {
                "principle": "YAGNI",
                "severity": "error",
                "file": plan_label,
                "message": (
                    "Plan names a new abstraction without citing reuse-catalog / "
                    "existing call sites / YAGNI. Rewrite or waive with ADR."
                ),
            }
        )
    if re.search(r"\b(god object|do everything|new framework)\b", plan_text, re.I):
        findings.append(
            {
                "principle": "KISS",
                "severity": "error",
                "file": plan_label,
                "message": "Plan smells over-built: prefer the smallest change that meets AC",
            }
        )
    driver = COST_DRIVER.search(plan_text)
    if driver and not COST_HINT.search(plan_text):
        findings.append(
            {
                "principle": "Budget",
                "severity": "warn",
                "file": plan_label,
                "message": (
                    f"Plan adds a cost driver ({driver.group(0)}) with no cost line. "
                    "Add a monthly estimate and the cheaper option you rejected."
                ),
            }
        )
    poll = POLL_WORK.search(plan_text)
    if poll and not EVENT_PATH.search(plan_text):
        findings.append(
            {
                "principle": "Reliability",
                "severity": "warn",
                "file": plan_label,
                "message": (
                    f"Plan polls for work ({poll.group(0)}) with no event path. Schedule a "
                    "wake-up at each due time, take failures as events, and keep a bounded "
                    "backstop. See reference/event-driven-work.md."
                ),
            }
        )
    return findings


def check_engineering_plan(root: Path, plan_text: str | None, plan_label: str) -> dict:
    findings = _docs_status(root)
    checklist = [
        "Read .heyeddi/docs/engineering/reuse-catalog.md",
        "Prefer extend existing modules over new abstractions",
        "Keep views/routers thin; services/composables hold logic",
        "Cost drivers (infra, LLM calls, schedules, CI, polling): state $/month and the cheaper option",
        "Timed or background work: follow reference/event-driven-work.md (wake-up at due time, "
        "live rows only, bounded backstop)",
        "After edits: audit_engineering.py --check (errors fail; warns advisory)",
        "After edits: estimate_change_cost.py (never stops the work; only pre-merge-gate adds --check)",
    ]
    if plan_text is not None:
        findings.extend(_plan_smells(plan_text, plan_label))
        checklist.insert(0, "Plan reviewed against KISS / YAGNI / DRY / SOLID")

    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]
    return {
        "ok": not errors,
        "finding_count": len(findings),
        "error_count": len(errors),
        "warn_count": len(warns),
        "findings": findings,
        "checklist": checklist,
        "always_on": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineering plan gate (always-on)")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--plan-file", default=None, help="Optional plan markdown to smell-check")
    parser.add_argument("--plan-text", default=None, help="Optional plan text (alt to --plan-file)")
    parser.add_argument("--check", action="store_true", help="Exit 1 on error-severity findings")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    plan_text: str | None = None
    plan_label = "(no plan file)"
    if args.plan_file:
        path = Path(args.plan_file)
        if not path.is_file():
            fail(f"Plan file not found: {args.plan_file}")
        plan_text = path.read_text(encoding="utf-8", errors="replace")
        plan_label = str(path)
    elif args.plan_text is not None:
        plan_text = args.plan_text
        plan_label = "(plan-text)"

    result = check_engineering_plan(root, plan_text, plan_label)
    emit(json.dumps(result, indent=2))
    if args.check and not result.get("ok"):
        fail("Engineering plan gate failed: see findings")


if __name__ == "__main__":
    main()
