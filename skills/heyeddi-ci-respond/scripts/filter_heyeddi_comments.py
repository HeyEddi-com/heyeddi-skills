#!/usr/bin/env python3
"""Filter PR comment cache to HeyEddi CI findings only.

Keep comments that match:
- body contains ``<!-- heyeddi-ci-review``
- body contains debate marker ``<!-- heyeddi-ci-debate:``
- author login looks like heyeddi-ci / heyeddi[bot]
- parent (via in_reply_to) looks like HeyEddi when parent is in the same payload
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root

REVIEW_MARKER = "<!-- heyeddi-ci-review"
DEBATE_MARKER = "<!-- heyeddi-ci-debate:"
BOT_LOGIN_HINTS = ("heyeddi-ci", "heyeddi[bot]", "heyeddi-ci[bot]")


def _login(item: dict[str, Any]) -> str:
    user = item.get("user") or item.get("author") or {}
    if isinstance(user, dict):
        return str(user.get("login") or "").lower()
    return str(user or "").lower()


def _body(item: dict[str, Any]) -> str:
    return str(item.get("body") or "")


def _is_bot_login(login: str) -> bool:
    return any(hint in login for hint in BOT_LOGIN_HINTS)


def looks_like_heyeddi(item: dict[str, Any] | None) -> bool:
    if not item:
        return False
    body = _body(item)
    if REVIEW_MARKER in body or DEBATE_MARKER in body:
        return True
    return _is_bot_login(_login(item))


def _index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("id") is not None:
            out[str(item["id"])] = item
    return out


def _keep_item(
    item: dict[str, Any],
    *,
    by_id: dict[str, dict[str, Any]],
) -> bool:
    if looks_like_heyeddi(item):
        return True
    parent_id = item.get("in_reply_to_id")
    if parent_id is None:
        parent_id = item.get("in_reply_to")
    if parent_id is None:
        return False
    return looks_like_heyeddi(by_id.get(str(parent_id)))


def filter_payload(data: dict[str, Any]) -> dict[str, Any]:
    inline = [c for c in (data.get("inline") or []) if isinstance(c, dict)]
    reviews = [c for c in (data.get("reviews") or []) if isinstance(c, dict)]
    discussion = data.get("discussion") or {}
    if isinstance(discussion, dict):
        disc_comments = [c for c in (discussion.get("comments") or []) if isinstance(c, dict)]
    else:
        disc_comments = []

    by_id = _index_by_id(inline + reviews + disc_comments)

    filtered_inline = [c for c in inline if _keep_item(c, by_id=by_id)]
    filtered_reviews = [c for c in reviews if _keep_item(c, by_id=by_id)]
    filtered_disc = [c for c in disc_comments if _keep_item(c, by_id=by_id)]

    out = dict(data)
    out["inline"] = filtered_inline
    out["reviews"] = filtered_reviews
    if isinstance(discussion, dict):
        out["discussion"] = {**discussion, "comments": filtered_disc}
    out["heyeddi_filter"] = {
        "review_marker": REVIEW_MARKER,
        "debate_marker": DEBATE_MARKER,
        "bot_login_hints": list(BOT_LOGIN_HINTS),
        "kept": {
            "inline": len(filtered_inline),
            "reviews": len(filtered_reviews),
            "discussion": len(filtered_disc),
        },
        "dropped": {
            "inline": len(inline) - len(filtered_inline),
            "reviews": len(reviews) - len(filtered_reviews),
            "discussion": len(disc_comments) - len(filtered_disc),
        },
    }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter PR comments to HeyEddi CI findings")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--input",
        default=None,
        help="Input comments JSON (default .heyeddi/docs/pr-<N>-ci-comments.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default overwrites input / ci-comments cache)",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 when zero HeyEddi comments kept")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    docs = root / ".heyeddi" / "docs"
    default_cache = docs / f"pr-{args.pr}-ci-comments.json"
    in_path = Path(args.input) if args.input else default_cache
    if not in_path.is_absolute():
        in_path = root / in_path
    if not in_path.is_file():
        emit(json.dumps({"error": "comments cache not found", "path": str(in_path)}, indent=2))
        sys.exit(1)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        emit(json.dumps({"error": "comments payload must be an object"}, indent=2))
        sys.exit(1)
    filtered = filter_payload(data)
    out_path = Path(args.output) if args.output else default_cache
    if not out_path.is_absolute():
        out_path = root / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(filtered, indent=2) + "\n", encoding="utf-8")
    kept = filtered["heyeddi_filter"]["kept"]
    total = kept["inline"] + kept["reviews"] + kept["discussion"]
    result = {
        "pr": args.pr,
        "path": str(out_path.relative_to(root)),
        "kept": kept,
        "dropped": filtered["heyeddi_filter"]["dropped"],
        "total_kept": total,
    }
    emit(json.dumps(result, indent=2))
    if args.check and total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
