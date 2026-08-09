#!/usr/bin/env python3
"""Fetch failing GitHub Checks / Actions evidence for a PR head (read-only)."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root, run_command


def _docs_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs"


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
    docs = _docs_dir(root)
    docs.mkdir(parents=True, exist_ok=True)
    out_path = docs / f"pr-{args.pr}-ci-fails-raw.json"

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
                    "path": str(out_path.relative_to(root)),
                    "source": "fixture",
                    "failing_count": len(data.get("failing") or []),
                },
                indent=2,
            )
        )
        return

    if not shutil.which("gh"):
        emit(json.dumps({"error": "gh CLI not found", "pr": args.pr}, indent=2))
        raise SystemExit(1)

    pr = _gh_json(root, ["pr", "view", str(args.pr), "--json", "number,url,headRefOid,headRefName,statusCheckRollup"])
    if isinstance(pr, dict) and pr.get("_error"):
        emit(json.dumps({"error": "gh pr view failed", "detail": pr}, indent=2))
        raise SystemExit(1)

    rollup = pr.get("statusCheckRollup") or []
    failing: list[dict[str, Any]] = []
    for item in rollup:
        if not isinstance(item, dict):
            continue
        state = str(item.get("state") or item.get("conclusion") or "").upper()
        if state in {"FAILURE", "FAILED", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            failing.append(
                {
                    "name": item.get("name") or item.get("context"),
                    "state": state,
                    "detailsUrl": item.get("detailsUrl") or item.get("targetUrl"),
                    "description": item.get("description") or item.get("title"),
                    "workflowName": item.get("workflowName"),
                }
            )

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
                "path": str(out_path.relative_to(root)),
                "failing_count": len(failing),
                "head_sha": head,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
