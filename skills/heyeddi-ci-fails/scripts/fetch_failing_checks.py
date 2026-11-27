#!/usr/bin/env python3
"""Fetch failing GitHub Checks / Actions evidence for a PR head (read-only)."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from _skill_cli import degraded, emit, gh_status, resolve_project_root, run_command
from _ci_temp import ci_temp_dir

FAILED_STATES = {"FAILURE", "FAILED", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}


def classify_rollup(rollup: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """(failing checks, names of checks still running). Pending is not green."""
    failing: list[dict[str, Any]] = []
    pending: list[str] = []
    for item in rollup:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("context")
        state = str(item.get("state") or item.get("conclusion") or "").upper()
        status = str(item.get("status") or "").upper()
        if state in FAILED_STATES:
            failing.append(
                {
                    "name": name,
                    "state": state,
                    "detailsUrl": item.get("detailsUrl") or item.get("targetUrl"),
                    "description": item.get("description") or item.get("title"),
                    "workflowName": item.get("workflowName"),
                }
            )
        elif state in {"PENDING", "EXPECTED"} or (status and status != "COMPLETED"):
            pending.append(str(name))
    return failing, pending


def _gh_json(root: Path, args: list[str]) -> Any:
    raw = run_command(["gh", *args], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return {"_error": raw}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_error": "non-JSON", "_raw": raw[:2000]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch failing PR checks")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--fixture",
        default=None,
        help="Fixture JSON path (evals without gh)",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    out_path = ci_temp_dir(root, args.pr) / f"pr-{args.pr}-ci-fails-raw.json"

    if args.fixture:
        fixture = Path(args.fixture)
        if not fixture.is_absolute():
            fixture = root / fixture
        data = json.loads(fixture.read_text(encoding="utf-8"))
        out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        emit(
            json.dumps(
                {
                    "pr": args.pr,
                    "path": str(out_path),
                    "source": "fixture",
                    "failing_count": len(data.get("failing") or []),
                },
                indent=2,
            )
        )
        return

    status = gh_status(root)
    if not status["ok"]:
        degraded(
            "fetch_failing_checks",
            status,
            pr=args.pr,
            manual=[
                "Read check status with the GitHub MCP tool pull_request_read (get_status).",
                "Or open the PR's Checks tab and paste the failing job log into the chat.",
            ],
        )

    pr = _gh_json(root, ["pr", "view", str(args.pr), "--json", "number,url,headRefOid,headRefName,statusCheckRollup"])
    if isinstance(pr, dict) and pr.get("_error"):
        emit(json.dumps({"error": "gh pr view failed", "detail": pr}, indent=2))
        raise SystemExit(1)

    failing, pending = classify_rollup(pr.get("statusCheckRollup") or [])

    # Best-effort: failed check runs on head SHA
    head = str(pr.get("headRefOid") or "")
    check_runs: Any = None
    if head:
        repo = run_command(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            root,
        ).strip()
        if not repo.startswith("["):
            check_runs = _gh_json(
                root,
                [
                    "api",
                    f"repos/{repo}/commits/{head}/check-runs",
                    "--jq",
                    "{total: .total_count, runs: [.check_runs[] | select(.conclusion==\"failure\" or .conclusion==\"timed_out\" or .conclusion==\"cancelled\") | {id, name, conclusion, html_url, output: {title: .output.title, summary: .output.summary}}]}",
                ],
            )

    payload = {
        "pr": args.pr,
        "head_sha": head,
        "head_ref": pr.get("headRefName"),
        "url": pr.get("url"),
        "failing": failing,
        "pending": pending,
        "check_runs": check_runs,
        "note": (
            "Read-only evidence. For hosted App analysis the user can comment "
            "`/heyeddi fails` on the PR (may be billable)."
        ),
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    emit(
        json.dumps(
            {
                "pr": args.pr,
                "path": str(out_path),
                "failing_count": len(failing),
                "pending_count": len(pending),
                "pending": pending,
                "green": not failing and not pending,
                "next": f"gh pr checks {args.pr} --watch" if pending else None,
                "head_sha": head,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
