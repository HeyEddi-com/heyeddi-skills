#!/usr/bin/env python3
"""Resolve every drafted comment id to a postable GitHub target + MCP fallback.

Use before or after ``post_thread_replies`` when an agent claims a thread was
"not found". Prints JSON with root ids and exact MCP tool hints — never guess.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _comment_resolve import build_comment_index, resolve_reply_target
from _replies_parse import infer_reply_kind, parse_reply_sections
from _skill_cli import emit, resolve_project_root
from _temp_store import comments_cache_path


def _load_replies(args: argparse.Namespace) -> str:
    if args.replies_text:
        return args.replies_text
    if args.replies_file:
        path = Path(args.replies_file)
        if not path.is_file():
            emit(json.dumps({"error": "replies file not found", "path": str(path)}, indent=2))
            sys.exit(1)
        return path.read_text(encoding="utf-8")
    emit(json.dumps({"error": "pass --replies-text, --replies-file, or --comment-ids"}, indent=2))
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve PR reply targets (gh + MCP hints)")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--replies-text", default=None)
    parser.add_argument("--replies-file", default=None)
    parser.add_argument(
        "--comment-ids",
        default=None,
        help="Comma-separated ids with optional kind: 123,456:discussion,789:inline",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not call gh live lookups (cache + hints only)",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    cache_path = comments_cache_path(args.pr)
    cache: dict[str, Any] = {}
    if cache_path.is_file():
        try:
            loaded = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                cache = loaded
        except (json.JSONDecodeError, OSError):
            cache = {}
    index = build_comment_index(cache)
    repo = cache.get("repo") if isinstance(cache.get("repo"), str) else None

    pairs: list[tuple[str, str | None]] = []
    if args.comment_ids:
        for part in args.comment_ids.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                cid, kind = part.split(":", 1)
                pairs.append((cid.strip(), kind.strip() or None))
            else:
                pairs.append((part, None))
    else:
        text = _load_replies(args)
        sections, _ = parse_reply_sections(text)
        for section in sections:
            pairs.append(
                (
                    section.comment_id,
                    infer_reply_kind(section.comment_id, None, section.kind),
                )
            )

    cached_login = cache.get("responder_login")
    responder_login = (
        cached_login.strip() if isinstance(cached_login, str) and cached_login.strip() else None
    )
    targets = []
    unresolved = 0
    for cid, hint in pairs:
        target = resolve_reply_target(
            root=root,
            repo=repo,
            pr=args.pr,
            comment_id=cid,
            kind_hint=hint,
            index=index,
            live=not args.offline and bool(repo),
            responder_login=responder_login,
        )
        if target.post_method == "unresolved":
            unresolved += 1
        targets.append(
            {
                "input_id": target.input_id,
                "kind": target.kind,
                "post_method": target.post_method,
                "reply_to_id": target.reply_to_id,
                "detail": target.detail,
                "mcp_tool": target.mcp_tool,
                "mcp_hint": target.mcp_hint,
                "body_snippet": target.body_snippet[:120],
            }
        )

    emit(
        json.dumps(
            {
                "pr": args.pr,
                "repo": repo,
                "target_count": len(targets),
                "unresolved_count": unresolved,
                "targets": targets,
                "rule": (
                    "Reply only on unresolved review threads at the root id, with no quote. "
                    "Issue comments are skipped. On a review-thread failure, use mcp_tool / "
                    "mcp_hint — do not claim thread not found and do not quote-reply."
                ),
            },
            indent=2,
        )
    )
    if unresolved:
        sys.exit(1)


if __name__ == "__main__":
    main()
