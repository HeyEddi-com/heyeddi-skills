#!/usr/bin/env python3
"""Verify PR review response workflow: every comment drafted and posted."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from _replies_parse import parse_reply_sections, parse_tracking_rows, summary_is_last
from _skill_cli import emit, resolve_project_root, run_command

TRACKING_NAME = "pr-{pr}-ci-tracking.md"
REPLIES_NAME = "pr-{pr}-ci-replies.md"
POSTED_NAME = "pr-{pr}-ci-posted.json"
COMMENTS_CACHE = "pr-{pr}-ci-comments.json"
REQUIRED_TRACKING_COLS = ("Comment ID", "Action", "Status")
RESPONDED_MARKERS = ("RESPONDED", "responded", "replied", "POSTED", "posted")


def docs_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs"


def _expected_from_fixture(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    ids: list[str] = []
    for item in data.get("inline") or []:
        if isinstance(item, dict) and item.get("id") is not None:
            ids.append(str(item["id"]))
    discussion = data.get("discussion") or {}
    for item in discussion.get("comments") or []:
        if isinstance(item, dict) and item.get("id") is not None:
            ids.append(str(item["id"]))
    for item in data.get("reviews") or []:
        if not isinstance(item, dict):
            continue
        body = item.get("body") or ""
        if isinstance(body, str) and body.strip() and item.get("id") is not None:
            ids.append(str(item["id"]))
    return ids


def _expected_from_cache(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        return _expected_from_fixture(path)
    except (json.JSONDecodeError, OSError):
        return []


def _live_replied_inline_ids(root: Path, pr: int, repo: str | None) -> tuple[set[str], str | None]:
    """Return set of parent inline comment IDs that already have a reply on GitHub."""
    if not shutil.which("gh"):
        return set(), "gh CLI not found"
    if not repo:
        repo_out = run_command(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            root,
        )
        if repo_out.startswith("[exit") or repo_out.startswith("[error]"):
            return set(), f"could not resolve repo: {repo_out}"
        repo = repo_out.strip()
    raw = run_command(["gh", "api", f"repos/{repo}/pulls/{pr}/comments", "--paginate"], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return set(), f"gh api failed: {raw[:200]}"
    try:
        comments = json.loads(raw)
    except json.JSONDecodeError:
        return set(), "gh api returned non-JSON"
    if not isinstance(comments, list):
        return set(), "gh api comments payload is not a list"
    replied: set[str] = set()
    for item in comments:
        if not isinstance(item, dict):
            continue
        parent = item.get("in_reply_to_id")
        if parent is not None:
            replied.add(str(parent))
    return replied, None


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify PR review response completeness")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--fixture", default=None, help="Fixture comments JSON to count expected replies")
    parser.add_argument("--require-gate", action="store_true", help="Fail if pre-merge gate report shows BLOCKED")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Require GitHub evidence that each inline comment has a threaded reply",
    )
    parser.add_argument(
        "--allow-draft-only",
        action="store_true",
        help="Eval/offline: skip posted.json requirement (still requires per-ID reply drafts)",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 when incomplete")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    missing: list[str] = []
    tracking_path = docs_dir(root) / TRACKING_NAME.format(pr=args.pr)
    replies_path = docs_dir(root) / REPLIES_NAME.format(pr=args.pr)
    posted_path = docs_dir(root) / POSTED_NAME.format(pr=args.pr)
    cache_path = docs_dir(root) / COMMENTS_CACHE.format(pr=args.pr)

    tracking_rows = []
    if not tracking_path.is_file():
        missing.append(f"missing tracking: {tracking_path.relative_to(root)}")
    else:
        tracking_text = tracking_path.read_text(encoding="utf-8")
        for col in REQUIRED_TRACKING_COLS:
            if col not in tracking_text:
                missing.append(f"tracking missing column: {col}")
        tracking_rows = parse_tracking_rows(tracking_text)
        if not tracking_rows:
            missing.append("tracking table has no comment rows")
        for row in tracking_rows:
            status = row.status or ""
            if not any(marker in status for marker in RESPONDED_MARKERS):
                missing.append(f"unresponded row: {row.raw[:80]}")

    reply_sections: list = []
    if not replies_path.is_file():
        missing.append(f"missing replies draft: {replies_path.relative_to(root)}")
    else:
        replies_text = replies_path.read_text(encoding="utf-8")
        reply_sections, summary_body = parse_reply_sections(replies_text)
        if not reply_sections:
            missing.append("replies file has no ## Comment <id> sections")
        if summary_body is None or not summary_body.strip():
            missing.append("replies file missing ## Summary section with body")
        elif not summary_is_last(replies_text):
            missing.append("## Summary must be the last section (after all individual replies)")
        empty = [s.comment_id for s in reply_sections if not s.body.strip()]
        if empty:
            missing.append(f"empty reply bodies for: {', '.join(empty)}")

    tracked_ids = [r.comment_id for r in tracking_rows]
    draft_ids = {s.comment_id for s in reply_sections}
    for comment_id in tracked_ids:
        if comment_id not in draft_ids:
            missing.append(f"no ## Comment {comment_id} reply draft")

    expected_ids: list[str] = []
    if args.fixture:
        fixture_path = Path(args.fixture)
        if not fixture_path.is_absolute():
            fixture_path = root / fixture_path
        if fixture_path.is_file():
            expected_ids = _expected_from_fixture(fixture_path)
        else:
            missing.append(f"fixture not found: {fixture_path}")
    else:
        expected_ids = _expected_from_cache(cache_path)

    if expected_ids:
        for comment_id in expected_ids:
            if comment_id not in tracked_ids:
                missing.append(f"tracking missing expected comment ID: {comment_id}")
            if comment_id not in draft_ids:
                missing.append(f"replies missing expected comment ID: {comment_id}")

    posted_ids: set[str] = set()
    if args.allow_draft_only or args.fixture:
        # Offline/eval path: drafts + tracking markers are enough.
        pass
    else:
        if not posted_path.is_file():
            missing.append(
                f"missing posted log: {posted_path.relative_to(root)} "
                "(run post_thread_replies.py after drafting replies)"
            )
        else:
            try:
                posted_data = json.loads(posted_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                missing.append("posted log is not valid JSON")
                posted_data = {}
            for item in posted_data.get("posted") or []:
                if not isinstance(item, dict):
                    continue
                cid = item.get("comment_id")
                status = (item.get("status") or "").lower()
                if cid is not None and status in {
                    "posted",
                    "dry-run",
                    "already-replied",
                    "skipped_review_body",
                }:
                    posted_ids.add(str(cid))
            for comment_id in tracked_ids:
                if comment_id not in posted_ids:
                    missing.append(f"not posted to GitHub thread: {comment_id}")

    live_checked = False
    live_replied: set[str] = set()
    if args.live:
        live_checked = True
        repo = None
        if cache_path.is_file():
            try:
                repo = json.loads(cache_path.read_text(encoding="utf-8")).get("repo")
            except (json.JSONDecodeError, OSError):
                repo = None
        live_replied, live_err = _live_replied_inline_ids(root, args.pr, repo)
        if live_err:
            missing.append(f"live reply check failed: {live_err}")
        else:
            inline_ids = [
                r.comment_id
                for r in tracking_rows
                if (r.kind or "").lower() == "inline" or re.fullmatch(r"\d+", r.comment_id or "")
            ]
            # Prefer explicit type=inline; fall back to numeric IDs that appear in drafts as inline.
            for section in reply_sections:
                if (section.kind or "").lower() == "inline":
                    if section.comment_id not in inline_ids:
                        inline_ids.append(section.comment_id)
            for comment_id in inline_ids:
                # Skip review-typed numeric IDs.
                row = next((r for r in tracking_rows if r.comment_id == comment_id), None)
                if row and (row.kind or "").lower() in {"review", "reviews"}:
                    continue
                if comment_id not in live_replied:
                    missing.append(f"live GitHub missing threaded reply for inline {comment_id}")

    if args.require_gate:
        gate_candidates = list(docs_dir(root).glob("ship-report.md")) + list(docs_dir(root).glob("*gate*"))
        gate_text = ""
        for path in gate_candidates:
            if path.is_file():
                gate_text += path.read_text(encoding="utf-8", errors="replace")
        if "BLOCKED" in gate_text:
            missing.append("pre-merge gate reports BLOCKED")

    status = "ok" if not missing else "fail"
    payload = {
        "pr": args.pr,
        "status": status,
        "tracking": str(tracking_path.relative_to(root)) if tracking_path.is_file() else None,
        "replies": str(replies_path.relative_to(root)) if replies_path.is_file() else None,
        "posted": str(posted_path.relative_to(root)) if posted_path.is_file() else None,
        "tracked_count": len(tracked_ids),
        "draft_count": len(reply_sections),
        "posted_count": len(posted_ids),
        "live_checked": live_checked,
        "live_replied_inline_count": len(live_replied) if live_checked else None,
        "missing": missing,
    }
    emit(json.dumps(payload, indent=2))
    if args.check and missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
