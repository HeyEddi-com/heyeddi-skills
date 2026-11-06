#!/usr/bin/env python3
"""Build the full list of PR review items that require a fix/decline and reply.

Postable replies are unresolved pull-request review threads only (root
review-comment id, no quote). Issue comments are listed and skipped:
tests-hold notes, conversation summaries, and comments written by the
responding account are not threads.

Review submission bodies are parsed for path:line bullets and linked to
inline comments. Orphans are summary-only.

Stdout JSON only. Never writes under ``.heyeddi/docs/``.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from _comment_resolve import awaiting_root_ids, comment_plain_body, is_tests_hold
from _skill_cli import emit, resolve_project_root, run_command
from _temp_store import comments_cache_path, inventory_cache_path

PATH_LINE_RE = re.compile(r"`([^`]+):(\d+)`")
HEYEDDI_MARKER = "<!-- heyeddi-ci-review"
DEBATE_MARKER = "<!-- heyeddi-ci-debate:"
BOT_HINTS = ("heyeddi-ci", "heyeddi[bot]", "heyeddi-ci[bot]")


def _login(item: dict[str, Any]) -> str:
    user = item.get("user") or item.get("author") or {}
    if isinstance(user, dict):
        return str(user.get("login") or "")
    return str(user or "")


def _body(item: dict[str, Any]) -> str:
    return comment_plain_body(item)


def _gh_login(root: Path) -> str | None:
    if not shutil.which("gh"):
        return None
    out = run_command(["gh", "api", "user", "-q", ".login"], root)
    if out.startswith("[exit") or out.startswith("[error]"):
        return None
    login = out.strip()
    return login or None


def _loc_key(path: str | None, line: int | str | None) -> str | None:
    if not path or line is None:
        return None
    return f"{path}:{line}"


def _parse_path_lines(text: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for match in PATH_LINE_RE.finditer(text):
        key = f"{match.group(1)}:{match.group(2)}"
        if key in seen:
            continue
        seen.add(key)
        out.append({"path": match.group(1), "line": int(match.group(2)), "loc": key})
    return out


def _is_actionable_review(review: dict[str, Any]) -> bool:
    state = str(review.get("state") or "").upper()
    body = _body(review).strip()
    if not body:
        return False
    if state == "APPROVED" and not PATH_LINE_RE.search(body):
        return False
    return True


def build_inventory(
    data: dict[str, Any],
    *,
    responder_login: str | None = None,
) -> dict[str, Any]:
    inline_raw = [c for c in (data.get("inline") or []) if isinstance(c, dict)]
    reviews = [c for c in (data.get("reviews") or []) if isinstance(c, dict)]
    discussion = data.get("discussion") or {}
    disc_comments = (
        [c for c in (discussion.get("comments") or []) if isinstance(c, dict)]
        if isinstance(discussion, dict)
        else []
    )

    login = (responder_login or "").strip() or None
    if login is None and isinstance(data.get("responder_login"), str):
        login = data["responder_login"].strip() or None

    inline_by_loc: dict[str, dict[str, Any]] = {}
    items: list[dict[str, Any]] = []
    expected_reply_ids: list[str] = []
    awaiting = set(awaiting_root_ids(inline_raw, login))

    for comment in inline_raw:
        if comment.get("in_reply_to_id") is not None:
            continue
        cid = str(comment.get("id"))
        path = comment.get("path")
        line = comment.get("line") or comment.get("original_line")
        loc = _loc_key(str(path) if path else None, line)
        if loc:
            inline_by_loc[loc] = comment
        summary = _body(comment).strip().splitlines()[0][:160] if _body(comment).strip() else ""
        author = _login(comment)
        if cid not in awaiting:
            items.append(
                {
                    "id": cid,
                    "type": "inline",
                    "reply_target_id": cid,
                    "reply_kind": "answered",
                    "path": path,
                    "line": line,
                    "author": author,
                    "summary": summary,
                    "source": "inline",
                    "note": (
                        "Review thread is not awaiting a reply "
                        "(tests-hold, or the responding account already spoke last)."
                    ),
                }
            )
            continue
        items.append(
            {
                "id": cid,
                "type": "inline",
                "reply_target_id": cid,
                "reply_kind": "inline",
                "path": path,
                "line": line,
                "author": author,
                "summary": summary,
                "source": "inline",
                "listed_in_review": [],
            }
        )
        expected_reply_ids.append(cid)

    for comment in disc_comments:
        cid = str(comment.get("id"))
        body = _body(comment)
        summary = body.strip().splitlines()[0][:160] if body.strip() else ""
        author = _login(comment)
        reasons: list[str] = []
        if is_tests_hold(body):
            reasons.append("tests-hold note")
        if login and author.lower() == login.lower():
            reasons.append("written by the responding account")
        note = "Issue comments are not review threads. Do not quote-reply."
        if reasons:
            note = f"{note} {'; '.join(reasons)}."
        items.append(
            {
                "id": cid,
                "type": "discussion",
                "reply_target_id": None,
                "reply_kind": "issue-comment",
                "path": None,
                "line": None,
                "author": author,
                "summary": summary,
                "source": "discussion",
                "note": note,
            }
        )

    orphan_findings: list[dict[str, Any]] = []
    review_summaries: list[dict[str, Any]] = []

    for review in reviews:
        if not _is_actionable_review(review):
            continue
        rid = str(review.get("id"))
        body = _body(review)
        bullets = _parse_path_lines(body)
        review_summaries.append(
            {
                "review_id": rid,
                "author": _login(review),
                "state": review.get("state"),
                "bullet_count": len(bullets),
                "is_heyeddi": HEYEDDI_MARKER in body or any(h in _login(review).lower() for h in BOT_HINTS),
            }
        )
        matched: set[str] = set()
        for bullet in bullets:
            loc = bullet["loc"]
            inline = inline_by_loc.get(loc)
            if inline:
                iid = str(inline.get("id"))
                matched.add(iid)
                for item in items:
                    if item.get("id") == iid:
                        refs = item.setdefault("listed_in_review", [])
                        if rid not in refs:
                            refs.append(rid)
                        break
            else:
                orphan_id = f"orphan-{rid}-{loc.replace('/', '-')}"
                orphan_findings.append(
                    {
                        "id": orphan_id,
                        "type": "review-finding",
                        "reply_target_id": orphan_id,
                        "reply_kind": "orphan-finding",
                        "path": bullet["path"],
                        "line": bullet["line"],
                        "author": _login(review),
                        "summary": f"Review {rid} lists {loc} with no matching inline comment",
                        "source": "review-body",
                        "review_id": rid,
                    }
                )
                items.append(orphan_findings[-1])

        if not bullets and body.strip():
            items.append(
                {
                    "id": rid,
                    "type": "review",
                    "reply_target_id": rid,
                    "reply_kind": "review",
                    "author": _login(review),
                    "summary": body.strip().splitlines()[0][:160],
                    "source": "review-body",
                    "note": (
                        "No path:line bullets parsed. Address via inline replies if any exist; "
                        "otherwise cover in ## Summary (review bodies are not postable threads)."
                    ),
                }
            )

    # De-dupe expected ids preserving order
    seen_ids: set[str] = set()
    deduped_expected: list[str] = []
    for cid in expected_reply_ids:
        if cid not in seen_ids:
            seen_ids.add(cid)
            deduped_expected.append(cid)

    postable = [i for i in items if i.get("reply_kind") == "inline"]
    summary_only = [
        i
        for i in items
        if i.get("reply_kind") in {"review", "orphan-finding", "issue-comment", "answered"}
    ]

    return {
        "pr": data.get("pr"),
        "repo": data.get("repo"),
        "item_count": len(items),
        "postable_count": len(postable),
        "expected_reply_ids": deduped_expected,
        "postable_reply_ids": [i["reply_target_id"] for i in postable],
        "items": items,
        "review_summaries": review_summaries,
        "orphan_findings": orphan_findings,
        "summary_only_items": summary_only,
        "responder_login": login,
        "rules": [
            "Reply only on unresolved pull-request review threads, at the root comment id, with no quote.",
            "Do not quote-reply issue comments. Skip tests-hold notes, review summaries, and comments written by the responding account.",
            "Every postable inline ID must get a ## Comment <id> reply draft.",
            "Orphan review findings (no inline) must be fixed/declined in code and covered in ## Summary.",
            "Review submission bodies are not postable threads.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PR comment inventory for respond workflow")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--input", default=None, help="Comments JSON (default temp cache from fetch)")
    parser.add_argument("--write-cache", action="store_true", help="Also write inventory.json to temp dir")
    parser.add_argument(
        "--responder",
        default=None,
        help="Login of the account posting replies (default: gh api user, else cache responder_login)",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 when zero actionable items")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    in_path = Path(args.input) if args.input else comments_cache_path(args.pr)
    if args.input and not in_path.is_absolute():
        in_path = root / in_path
    if not in_path.is_file():
        emit(json.dumps({"error": "comments cache not found", "path": str(in_path)}, indent=2))
        sys.exit(1)

    data = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        emit(json.dumps({"error": "comments payload must be an object"}, indent=2))
        sys.exit(1)

    responder = (args.responder or "").strip() or None
    if responder is None:
        cached = data.get("responder_login")
        if isinstance(cached, str) and cached.strip():
            responder = cached.strip()
    if responder is None:
        responder = _gh_login(root)

    inventory = build_inventory(data, responder_login=responder)
    if args.write_cache:
        out_path = inventory_cache_path(args.pr)
        out_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
        inventory["inventory_path"] = str(out_path)

    inventory["ephemeral"] = True
    inventory["comments_path"] = str(in_path)
    emit(json.dumps(inventory, indent=2))

    postable = inventory.get("postable_count") or 0
    if args.check and postable == 0 and not inventory.get("summary_only_items"):
        sys.exit(1)


if __name__ == "__main__":
    main()
