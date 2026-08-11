#!/usr/bin/env python3
"""Verify PR review response workflow without writing project scratch files.

Pass reply drafts via --replies-text or --replies-file. Use --live to confirm
GitHub threaded replies. Never requires ``.heyeddi/docs/pr-*-ci-*`` on disk.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from _replies_parse import parse_reply_sections, summary_is_last
from _skill_cli import emit, resolve_project_root, run_command
from _temp_store import comments_cache_path, inventory_cache_path


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


def _load_replies_text(args: argparse.Namespace, root: Path) -> str | None:
    if args.replies_text:
        return args.replies_text
    if args.replies_file:
        path = Path(args.replies_file)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    return None


def _parse_comment_ids(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


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
    parser.add_argument(
        "--replies-text",
        default=None,
        help="Draft replies markdown (## Comment <id> + ## Summary last)",
    )
    parser.add_argument(
        "--replies-file",
        default=None,
        help="Path to replies markdown (never .heyeddi/docs/pr-*-ci-replies.md)",
    )
    parser.add_argument(
        "--comment-ids",
        default=None,
        help="Comma-separated expected comment IDs (default: from temp comments cache or fixture)",
    )
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
        help="Eval/offline: verify reply draft shape only (no GitHub live check)",
    )
    parser.add_argument(
        "--use-inventory",
        action="store_true",
        help="Require reply drafts for every postable ID from build_comment_inventory",
    )
    parser.add_argument(
        "--inventory",
        default=None,
        help="Inventory JSON path (default temp inventory.json when --use-inventory)",
    )
    parser.add_argument("--check", action="store_true", help="Exit 1 when incomplete")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)

    missing: list[str] = []
    replies_text = _load_replies_text(args, root)
    if not replies_text:
        missing.append(
            "missing replies draft (--replies-text or --replies-file). "
            "Do not write pr-*-replies.md under .heyeddi/docs/."
        )
        reply_sections = []
        summary_body = None
    else:
        reply_sections, summary_body = parse_reply_sections(replies_text)
        if not reply_sections:
            missing.append("replies draft has no ## Comment <id> sections")
        if summary_body is None or not summary_body.strip():
            missing.append("replies draft missing ## Summary section with body")
        elif not summary_is_last(replies_text):
            missing.append("## Summary must be the last section (after all individual replies)")
        empty = [s.comment_id for s in reply_sections if not s.body.strip()]
        if empty:
            missing.append(f"empty reply bodies for: {', '.join(empty)}")

    draft_ids = {s.comment_id for s in reply_sections}

    payload_note: str | None = None
    expected_ids = _parse_comment_ids(args.comment_ids)
    if args.use_inventory or args.inventory:
        inv_path = Path(args.inventory) if args.inventory else inventory_cache_path(args.pr)
        if not inv_path.is_file() and args.use_inventory:
            missing.append(
                f"missing inventory: {inv_path} (run build_comment_inventory --write-cache first)"
            )
        elif inv_path.is_file():
            try:
                inv = json.loads(inv_path.read_text(encoding="utf-8"))
                inv_ids = inv.get("postable_reply_ids") or inv.get("expected_reply_ids") or []
                for cid in inv_ids:
                    scid = str(cid)
                    if scid not in expected_ids:
                        expected_ids.append(scid)
                orphans = inv.get("orphan_findings") or []
                if orphans:
                    payload_note = (
                        f"{len(orphans)} review-body finding(s) lack inline threads — "
                        "fix/decline in code and cover in ## Summary"
                    )
            except json.JSONDecodeError:
                missing.append("inventory file is not valid JSON")

    if not expected_ids and args.fixture:
        fixture_path = Path(args.fixture)
        if not fixture_path.is_absolute():
            fixture_path = root / fixture_path
        if fixture_path.is_file():
            expected_ids = _expected_from_fixture(fixture_path)
        else:
            missing.append(f"fixture not found: {fixture_path}")
    elif not expected_ids:
        expected_ids = _expected_from_cache(comments_cache_path(args.pr))

    for comment_id in expected_ids:
        if comment_id not in draft_ids:
            missing.append(f"replies missing expected comment ID: {comment_id}")

    live_checked = False
    live_replied: set[str] = set()
    if args.live and not args.allow_draft_only:
        live_checked = True
        repo = None
        cache_path = comments_cache_path(args.pr)
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
                cid
                for cid in expected_ids
                if re.fullmatch(r"\d+", cid or "")
            ]
            for section in reply_sections:
                if (section.kind or "").lower() == "inline" and section.comment_id not in inline_ids:
                    inline_ids.append(section.comment_id)
            for comment_id in inline_ids:
                row_kind = next(
                    (s.kind for s in reply_sections if s.comment_id == comment_id),
                    None,
                )
                if (row_kind or "").lower() in {"review", "reviews"}:
                    continue
                if comment_id not in live_replied:
                    missing.append(f"live GitHub missing threaded reply for inline {comment_id}")

    if args.require_gate:
        docs = root / ".heyeddi" / "docs"
        gate_candidates = list(docs.glob("ship-report.md")) + list(docs.glob("*gate*"))
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
        "draft_count": len(reply_sections),
        "expected_count": len(expected_ids),
        "live_checked": live_checked,
        "live_replied_inline_count": len(live_replied) if live_checked else None,
        "missing": missing,
        "inventory_note": payload_note,
        "rule": "Never write .heyeddi/docs/pr-* scratch files; use --replies-text and --live.",
    }
    emit(json.dumps(payload, indent=2))
    if args.check and missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
