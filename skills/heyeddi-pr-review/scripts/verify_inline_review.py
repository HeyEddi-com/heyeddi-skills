#!/usr/bin/env python3
"""Verify a posted (or fixture) inline review matches drafted findings."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root, run_command

MARKER = "<!-- heyeddi-pr-review -->"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _findings_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("findings"), list):
        return [x for x in data["findings"] if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("comments"), list):
        return [x for x in data["comments"] if isinstance(x, dict)]
    return []


def _key(path: str, line: Any) -> str:
    return f"{path}:{line}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify inline PR review findings were posted")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--findings-file", default=None, help="Draft findings JSON to match")
    parser.add_argument(
        "--posted-file",
        default=None,
        help="Posted payload / fixture JSON (skip live gh when set)",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    expected: list[dict[str, Any]] = []
    if args.findings_file:
        expected = _findings_list(_load_json(Path(args.findings_file)))

    missing: list[str] = []
    posted_comments: list[dict[str, Any]] = []
    event = None

    if args.posted_file:
        posted = _load_json(Path(args.posted_file))
        event = posted.get("event") if isinstance(posted, dict) else None
        posted_comments = _findings_list(posted)
    else:
        if not shutil.which("gh"):
            missing.append("gh CLI not found and no --posted-file")
        else:
            repo_out = run_command(
                ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                root,
            )
            if repo_out.startswith("[exit") or repo_out.startswith("[error]"):
                missing.append(f"repo resolve failed: {repo_out}")
            else:
                repo = repo_out.strip()
                out = run_command(
                    ["gh", "api", f"repos/{repo}/pulls/{args.pr}/comments", "--paginate"],
                    root,
                )
                if out.startswith("[exit") or out.startswith("[error]"):
                    missing.append(f"list comments failed: {out}")
                else:
                    try:
                        comments = json.loads(out)
                    except json.JSONDecodeError:
                        comments = []
                    for item in comments if isinstance(comments, list) else []:
                        if not isinstance(item, dict):
                            continue
                        body = str(item.get("body") or "")
                        if MARKER not in body and "heyeddi-pr-review" not in body.lower():
                            continue
                        posted_comments.append(
                            {
                                "path": item.get("path"),
                                "line": item.get("line") or item.get("original_line"),
                                "body": body,
                            }
                        )

    if expected:
        posted_keys = {
            _key(str(c.get("path")), c.get("line"))
            for c in posted_comments
            if c.get("path") is not None and c.get("line") is not None
        }
        for item in expected:
            key = _key(str(item.get("path")), item.get("line"))
            if key not in posted_keys:
                missing.append(f"missing inline comment for {key}")
    elif not posted_comments and event not in {"APPROVE", "APPROVED"}:
        # Clean approve may have zero comments; require either APPROVE event in fixture
        # or at least one heyeddi-pr-review activity when findings were expected empty.
        if args.posted_file and event == "APPROVE":
            pass
        elif args.findings_file is not None and not expected:
            if args.posted_file and event != "APPROVE":
                missing.append("zero findings require APPROVE event")
        # live mode with zero expected: do not fail solely on empty comments

    status = "ok" if not missing else "fail"
    payload = {
        "pr": args.pr,
        "status": status,
        "expected_count": len(expected),
        "posted_count": len(posted_comments),
        "event": event,
        "missing": missing,
    }
    emit(json.dumps(payload, indent=2))
    if args.check and missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
