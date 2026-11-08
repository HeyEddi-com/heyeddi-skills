#!/usr/bin/env python3
"""Post a GitHub PR review with inline comments on exact lines.

Findings JSON (list or {\"findings\": [...]}):
  path, line (int), body (str), optional side (RIGHT|LEFT), severity

0 findings → APPROVE with LGTM.
≥1 finding → REQUEST_CHANGES (or COMMENT if --event COMMENT).

Each comment body should include <!-- heyeddi-pr-review --> (added if missing).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from _skill_cli import emit, fail, resolve_project_root, run_command

MARKER = "<!-- heyeddi-pr-review -->"
DEFAULT_APPROVE = (
    f"{MARKER}\n"
    "LGTM. No in-scope line findings (security, logic, correctness). "
    "Lint/style and merge gates are left to pre-commit / `@pre-merge-gate`."
)


def _load_findings(path: Path | None, raw: str | None) -> list[dict[str, Any]]:
    if path:
        data = json.loads(path.read_text(encoding="utf-8"))
    elif raw:
        data = json.loads(raw)
    else:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        findings = data.get("findings")
        if isinstance(findings, list):
            return [item for item in findings if isinstance(item, dict)]
    fail("findings must be a JSON list or an object with a findings list")


def _ensure_marker(body: str) -> str:
    text = (body or "").strip()
    if MARKER in text:
        return text
    return f"{MARKER}\n{text}" if text else MARKER


def _normalize_comments(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    for item in findings:
        path = str(item.get("path") or "").strip()
        line = item.get("line")
        body = str(item.get("body") or "").strip()
        if not path or line is None or not body:
            fail(f"each finding needs path, line, body; got {item!r}")
        try:
            line_n = int(line)
        except (TypeError, ValueError) as exc:
            fail(f"invalid line {line!r}: {exc}")
        side = str(item.get("side") or "RIGHT").upper()
        if side not in {"RIGHT", "LEFT"}:
            fail(f"side must be RIGHT or LEFT, got {side}")
        comments.append(
            {
                "path": path,
                "line": line_n,
                "side": side,
                "body": _ensure_marker(body),
            }
        )
    return comments


def _repo(root: Path) -> str:
    out = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        root,
    )
    if out.startswith("[exit") or out.startswith("[error]"):
        fail(f"could not resolve repo: {out}")
    return out.strip()


def _head_sha(root: Path, pr: int) -> str:
    out = run_command(
        ["gh", "pr", "view", str(pr), "--json", "headRefOid", "-q", ".headRefOid"],
        root,
    )
    if out.startswith("[exit") or out.startswith("[error]"):
        fail(f"could not resolve PR head SHA: {out}")
    sha = out.strip()
    if not sha:
        fail("empty headRefOid")
    return sha


def main() -> None:
    parser = argparse.ArgumentParser(description="Post GitHub PR review with inline line comments")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--findings-file", default=None, help="JSON file of findings")
    parser.add_argument("--findings-json", default=None, help="Inline JSON findings")
    parser.add_argument(
        "--event",
        default=None,
        choices=["APPROVE", "REQUEST_CHANGES", "COMMENT"],
        help="Override event (default: APPROVE if empty, else REQUEST_CHANGES)",
    )
    parser.add_argument("--body", default=None, help="Review summary body")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--fixture-out",
        default=None,
        help="Write the review payload JSON here instead of calling gh (evals)",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    findings = _load_findings(
        Path(args.findings_file) if args.findings_file else None,
        args.findings_json,
    )
    comments = _normalize_comments(findings)

    if args.event:
        event = args.event
    elif comments:
        event = "REQUEST_CHANGES"
    else:
        event = "APPROVE"

    if event == "APPROVE" and comments:
        fail("APPROVE cannot include inline comments; drop findings or use REQUEST_CHANGES/COMMENT")

    summary = args.body
    if not summary:
        if event == "APPROVE":
            summary = DEFAULT_APPROVE
        else:
            summary = (
                f"{MARKER}\n"
                f"**Commented on the diff** ({len(comments)} finding(s)). "
                "Each issue is on the exact line. Lint/style left to pre-commit; "
                "merge gates → `@pre-merge-gate` after `@heyeddi-pr-respond`."
            )
    else:
        summary = _ensure_marker(summary)

    payload: dict[str, Any] = {
        "body": summary,
        "event": event,
        "comments": comments,
    }

    if args.fixture_out:
        out_path = Path(args.fixture_out)
        if not out_path.is_absolute():
            out_path = root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        emit(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "pr": args.pr,
                    "event": event,
                    "comment_count": len(comments),
                    "fixture_out": str(out_path),
                },
                indent=2,
            )
        )
        return

    if args.dry_run:
        emit(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "pr": args.pr,
                    "event": event,
                    "comment_count": len(comments),
                    "payload": payload,
                },
                indent=2,
            )
        )
        return

    if not shutil.which("gh"):
        fail("gh CLI not found")

    repo = _repo(root)
    sha = _head_sha(root, pr=args.pr)
    api_body = {
        "commit_id": sha,
        "body": summary,
        "event": event,
        "comments": comments,
    }

    # APPROVE with empty comments array is fine; omit comments key if empty for cleanliness
    if not comments:
        api_body.pop("comments", None)

    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(api_body, handle)
        handle.write("\n")
        payload_path = handle.name

    out = run_command(
        [
            "gh",
            "api",
            f"repos/{repo}/pulls/{args.pr}/reviews",
            "-X",
            "POST",
            "--input",
            payload_path,
        ],
        root,
    )
    Path(payload_path).unlink(missing_ok=True)

    if out.startswith("[exit") or out.startswith("[error]"):
        fail(f"failed to post review: {out}")

    try:
        review = json.loads(out)
    except json.JSONDecodeError:
        review = {"raw": out}

    emit(
        json.dumps(
            {
                "ok": True,
                "pr": args.pr,
                "repo": repo,
                "event": event,
                "comment_count": len(comments),
                "review_id": review.get("id"),
                "html_url": review.get("html_url"),
                "commit_id": sha,
                "findings": [
                    {"path": c["path"], "line": c["line"], "side": c["side"]} for c in comments
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — skill CLI boundary
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
