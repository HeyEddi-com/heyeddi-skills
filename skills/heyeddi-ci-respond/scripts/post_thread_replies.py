#!/usr/bin/env python3
"""Post every drafted PR reply **in the same thread** as the reviewer comment.

Never use `gh pr comment` for individual replies (that creates top-level spam).
Inline / review-thread comments → REST `/pulls/{pr}/comments/{id}/replies`.
Review *submission* bodies (type=review) → do not post a separate PR comment.
Discussion issue comments → GraphQL reply when possible; never "ack review" spam.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from _replies_parse import (
    infer_reply_kind,
    parse_reply_sections,
    parse_tracking_rows,
    summary_is_last,
)
from _skill_cli import emit, resolve_project_root, run_command

TRACKING_NAME = "pr-{pr}-ci-tracking.md"
REPLIES_NAME = "pr-{pr}-ci-replies.md"
POSTED_NAME = "pr-{pr}-ci-posted.json"
COMMENTS_CACHE = "pr-{pr}-ci-comments.json"

# Status values that satisfy verify_response posted.json checks
OK_STATUSES = frozenset({"posted", "dry-run", "skipped_review_body", "already-replied"})

BANNED_BODY = re.compile(
    r"acknowledged review attachment|inline threads carry the detailed",
    re.IGNORECASE,
)


def docs_dir(root: Path) -> Path:
    return root / ".heyeddi" / "docs"


def _resolve_repo(root: Path, cache_path: Path) -> str | None:
    if cache_path.is_file():
        try:
            repo = json.loads(cache_path.read_text(encoding="utf-8")).get("repo")
            if isinstance(repo, str) and repo.strip():
                return repo.strip()
        except (json.JSONDecodeError, OSError):
            pass
    if not shutil.which("gh"):
        return None
    out = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        root,
    )
    if out.startswith("[exit") or out.startswith("[error]"):
        return None
    return out.strip() or None


def _mark_tracking_responded(tracking_path: Path, comment_ids: set[str]) -> None:
    if not tracking_path.is_file() or not comment_ids:
        return
    lines = tracking_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        updated = line
        for comment_id in comment_ids:
            if f"| {comment_id} |" in line or f"|{comment_id}|" in line.replace(" ", ""):
                updated = re.sub(
                    r"(\|\s*)PENDING(\s*\|?\s*)$",
                    r"\1RESPONDED\2",
                    updated,
                    flags=re.IGNORECASE,
                )
                if "PENDING" in updated.upper() and "RESPONDED" not in updated.upper():
                    updated = re.sub(
                        r"PENDING",
                        "RESPONDED",
                        updated,
                        count=1,
                        flags=re.IGNORECASE,
                    )
        out.append(updated)
    tracking_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _post_review_comment_reply(
    root: Path, repo: str, pr: int, comment_id: str, body: str
) -> tuple[str, str | None]:
    """Reply in the same review-comment thread (Files changed / inline)."""
    raw = run_command(
        [
            "gh",
            "api",
            f"repos/{repo}/pulls/{pr}/comments/{comment_id}/replies",
            "-X",
            "POST",
            "-f",
            f"body={body}",
        ],
        root,
    )
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    try:
        payload = json.loads(raw)
        reply_id = str(payload.get("id")) if isinstance(payload, dict) and payload.get("id") else None
    except json.JSONDecodeError:
        reply_id = None
    return "posted", reply_id


def _resolve_database_id(root: Path, node_id: str) -> tuple[str | None, str | None]:
    """Map GraphQL node id → databaseId + typename."""
    query = (
        "query($id:ID!){ node(id:$id){ __typename "
        "... on PullRequestReviewComment { databaseId } "
        "... on IssueComment { databaseId } } }"
    )
    raw = run_command(
        ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"id={node_id}"],
        root,
    )
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return None, raw[:200]
    try:
        data = json.loads(raw)
        node = (data.get("data") or {}).get("node") or {}
        db = node.get("databaseId")
        typename = node.get("__typename")
        if db is None:
            return None, f"no databaseId for {typename or node_id}"
        return f"{typename}:{db}", None
    except json.JSONDecodeError:
        return None, "graphql non-JSON"


def _post_issue_comment_reply_resolved(
    root: Path, repo: str, comment_id: str, body: str
) -> tuple[str, str | None]:
    raw = run_command(
        [
            "gh",
            "api",
            f"repos/{repo}/issues/comments/{comment_id}/replies",
            "-X",
            "POST",
            "-f",
            f"body={body}",
        ],
        root,
    )
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    try:
        payload = json.loads(raw)
        return "posted", str(payload.get("id") or payload.get("node_id") or "")
    except json.JSONDecodeError:
        return "posted", raw.strip()[:120] or None


def _post_one(
    *,
    root: Path,
    repo: str,
    pr: int,
    comment_id: str,
    kind: str,
    body: str,
) -> tuple[str, str | None]:
    if BANNED_BODY.search(body):
        return (
            "error",
            "banned body: do not post 'Acknowledged review attachment' top-level spam",
        )

    # Review *submission* bodies are not threads. Never gh pr comment these.
    if kind == "review":
        return (
            "skipped_review_body",
            "Review submission bodies are not reply threads. Reply on each inline "
            "comment via /replies; at most one Summary at the end.",
        )

    # Numeric IDs → always in-thread review-comment reply.
    if comment_id.isdigit():
        return _post_review_comment_reply(root, repo, pr, comment_id, body)

    # GraphQL / opaque ids: resolve then reply in the correct thread type.
    resolved, err = _resolve_database_id(root, comment_id)
    if err or not resolved:
        # Fixture-style DC_* ids or unresolved: refuse top-level spam.
        return (
            "error",
            err
            or (
                f"Cannot resolve {comment_id} to a threadable comment id. "
                "Use the numeric review-comment id and POST .../comments/ID/replies."
            ),
        )
    typename, db_id = resolved.split(":", 1)
    if typename == "PullRequestReviewComment":
        return _post_review_comment_reply(root, repo, pr, db_id, body)
    if typename == "IssueComment":
        return _post_issue_comment_reply_resolved(root, repo, db_id, body)
    return "error", f"unsupported comment type {typename}"


def _post_summary_once(root: Path, pr: int, body: str) -> tuple[str, str | None]:
    """Only allowed use of top-level PR comment: a single final summary."""
    if BANNED_BODY.search(body):
        return "error", "banned summary body"
    raw = run_command(["gh", "pr", "comment", str(pr), "--body", body], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    url = raw.strip().splitlines()[-1] if raw.strip() else None
    return "posted", url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post drafted replies in-thread (never top-level per-comment spam)"
    )
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write posted.json without calling gh (evals / offline)",
    )
    parser.add_argument(
        "--post-summary",
        action="store_true",
        help="Post ## Summary once via gh pr comment AFTER all threads succeed (optional)",
    )
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    docs = docs_dir(root)
    docs.mkdir(parents=True, exist_ok=True)
    tracking_path = docs / TRACKING_NAME.format(pr=args.pr)
    replies_path = docs / REPLIES_NAME.format(pr=args.pr)
    posted_path = docs / POSTED_NAME.format(pr=args.pr)
    cache_path = docs / COMMENTS_CACHE.format(pr=args.pr)

    if not replies_path.is_file():
        emit(json.dumps({"error": "missing replies draft", "path": str(replies_path)}, indent=2))
        sys.exit(1)

    replies_text = replies_path.read_text(encoding="utf-8")
    sections, summary_body = parse_reply_sections(replies_text)
    if not sections:
        emit(json.dumps({"error": "no ## Comment <id> sections in replies draft"}, indent=2))
        sys.exit(1)
    if summary_body is None or not summary_body.strip():
        emit(json.dumps({"error": "replies draft missing ## Summary body"}, indent=2))
        sys.exit(1)
    if not summary_is_last(replies_text):
        emit(json.dumps({"error": "## Summary must be last (after all individual replies)"}, indent=2))
        sys.exit(1)

    tracking_rows = (
        parse_tracking_rows(tracking_path.read_text(encoding="utf-8")) if tracking_path.is_file() else []
    )
    kind_by_id = {r.comment_id: r.kind for r in tracking_rows}

    dry_run = args.dry_run or not shutil.which("gh")
    repo = None if dry_run else _resolve_repo(root, cache_path)
    if not dry_run and not repo:
        emit(json.dumps({"error": "could not resolve repo for gh posts"}, indent=2))
        sys.exit(1)

    posted: list[dict] = []
    errors: list[str] = []
    succeeded_ids: set[str] = set()

    for section in sections:
        if not section.body.strip():
            errors.append(f"empty body for {section.comment_id}")
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": infer_reply_kind(
                        section.comment_id, kind_by_id.get(section.comment_id), section.kind
                    ),
                    "status": "error",
                    "detail": "empty body",
                }
            )
            continue

        if BANNED_BODY.search(section.body):
            errors.append(f"{section.comment_id}: banned acknowledgement spam body")
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": infer_reply_kind(
                        section.comment_id, kind_by_id.get(section.comment_id), section.kind
                    ),
                    "status": "error",
                    "detail": "banned acknowledgement body",
                }
            )
            continue

        kind = infer_reply_kind(section.comment_id, kind_by_id.get(section.comment_id), section.kind)

        if dry_run:
            status = "skipped_review_body" if kind == "review" else "dry-run"
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": kind,
                    "status": status,
                    "reply_ref": None,
                    "note": (
                        "Review bodies are not posted as top-level comments"
                        if kind == "review"
                        else "Would POST .../comments/ID/replies in-thread"
                    ),
                }
            )
            succeeded_ids.add(section.comment_id)
            continue

        assert repo is not None
        status, ref = _post_one(
            root=root,
            repo=repo,
            pr=args.pr,
            comment_id=section.comment_id,
            kind=kind,
            body=section.body,
        )

        entry: dict = {
            "comment_id": section.comment_id,
            "type": kind,
            "status": status,
            "reply_ref": ref if status == "posted" else None,
        }
        if status in OK_STATUSES:
            succeeded_ids.add(section.comment_id)
            if status == "skipped_review_body":
                entry["detail"] = ref
        else:
            entry["detail"] = ref
            errors.append(f"{section.comment_id}: {ref}")
        posted.append(entry)

    summary_status = None
    if args.post_summary and not errors:
        if dry_run:
            summary_status = {"status": "dry-run", "reply_ref": None}
        else:
            status, ref = _post_summary_once(root, args.pr, summary_body)
            summary_status = {
                "status": status,
                "reply_ref": ref if status == "posted" else None,
            }
            if status != "posted":
                errors.append(f"summary: {ref}")

    payload = {
        "pr": args.pr,
        "dry_run": dry_run,
        "posted": posted,
        "posted_count": sum(1 for p in posted if p["status"] in OK_STATUSES),
        "error_count": len(errors),
        "errors": errors,
        "summary": summary_status,
        "rule": "Individual replies MUST use in-thread /replies. Never gh pr comment per comment.",
        "hint": "Run verify_response.py --pr <N> --check before considering the workflow done.",
    }
    posted_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    payload["posted_log"] = str(posted_path.relative_to(root))

    if succeeded_ids:
        _mark_tracking_responded(tracking_path, succeeded_ids)

    emit(json.dumps(payload, indent=2))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
