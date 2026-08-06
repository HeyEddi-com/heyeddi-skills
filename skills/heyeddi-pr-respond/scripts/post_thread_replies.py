#!/usr/bin/env python3
"""Post every drafted PR reply to its GitHub thread.

Reads `.heyeddi/docs/pr-<N>-replies.md` (## Comment <id> sections) and posts
each reply before any summary comment. Writes `pr-<N>-posted.json` so
`verify_response --check` can hard-fail when individual threads were skipped.
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

TRACKING_NAME = "pr-{pr}-tracking.md"
REPLIES_NAME = "pr-{pr}-replies.md"
POSTED_NAME = "pr-{pr}-posted.json"
COMMENTS_CACHE = "pr-{pr}-comments.json"


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
                # Replace PENDING (any case) in Status cell with RESPONDED.
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


def _post_inline(
    root: Path, repo: str, pr: int, comment_id: str, body: str
) -> tuple[str, str | None]:
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


def _post_pr_comment(root: Path, pr: int, body: str) -> tuple[str, str | None]:
    raw = run_command(["gh", "pr", "comment", str(pr), "--body", body], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return "error", raw[:400]
    # gh prints the comment URL on success.
    url = raw.strip().splitlines()[-1] if raw.strip() else None
    return "posted", url


def main() -> None:
    parser = argparse.ArgumentParser(description="Post drafted PR replies to every comment thread")
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
        help="Also post the ## Summary section via gh pr comment (only after all threads succeed)",
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

    tracking_rows = parse_tracking_rows(tracking_path.read_text(encoding="utf-8")) if tracking_path.is_file() else []
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
                    "type": infer_reply_kind(section.comment_id, kind_by_id.get(section.comment_id), section.kind),
                    "status": "error",
                    "detail": "empty body",
                }
            )
            continue

        kind = infer_reply_kind(section.comment_id, kind_by_id.get(section.comment_id), section.kind)
        if dry_run:
            posted.append(
                {
                    "comment_id": section.comment_id,
                    "type": kind,
                    "status": "dry-run",
                    "reply_ref": None,
                }
            )
            succeeded_ids.add(section.comment_id)
            continue

        assert repo is not None
        if kind == "inline":
            status, ref = _post_inline(root, repo, args.pr, section.comment_id, section.body)
        else:
            status, ref = _post_pr_comment(root, args.pr, section.body)

        entry = {
            "comment_id": section.comment_id,
            "type": kind,
            "status": status,
            "reply_ref": ref if status == "posted" else None,
        }
        if status != "posted":
            entry["detail"] = ref
            errors.append(f"{section.comment_id}: {ref}")
        else:
            succeeded_ids.add(section.comment_id)
        posted.append(entry)

    summary_status = None
    if args.post_summary and not dry_run and not errors:
        status, ref = _post_pr_comment(root, args.pr, summary_body)
        summary_status = {"status": status, "reply_ref": ref if status == "posted" else None}
        if status != "posted":
            errors.append(f"summary: {ref}")
    elif args.post_summary and dry_run and not errors:
        summary_status = {"status": "dry-run", "reply_ref": None}

    payload = {
        "pr": args.pr,
        "dry_run": dry_run,
        "posted": posted,
        "posted_count": sum(1 for p in posted if p["status"] in {"posted", "dry-run"}),
        "error_count": len(errors),
        "errors": errors,
        "summary": summary_status,
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
