"""Thread resolution must never guess — classify, walk to root, quote discussion."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "heyeddi-pr-respond" / "scripts"


def _import_resolve():
    sys.modules.pop("_comment_resolve", None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    from _comment_resolve import (  # noqa: E402
        build_comment_index,
        ensure_quote_reply,
        resolve_reply_target,
        walk_to_root,
    )

    return build_comment_index, ensure_quote_reply, resolve_reply_target, walk_to_root


def test_walk_to_root_follows_chain() -> None:
    build_index, _, _, walk = _import_resolve()
    index = build_index(
        {
            "inline": [
                {"id": 10, "body": "root", "in_reply_to_id": None},
                {"id": 11, "body": "child", "in_reply_to_id": 10},
                {"id": 12, "body": "grandchild", "in_reply_to_id": 11},
            ]
        }
    )
    assert walk("12", index) == "10"
    assert walk("11", index) == "10"
    assert walk("10", index) == "10"


def test_numeric_discussion_not_treated_as_inline() -> None:
    build_index, _, resolve, _ = _import_resolve()
    index = build_index(
        {
            "inline": [{"id": 100, "body": "inline finding"}],
            "discussion": {"comments": [{"id": 555001, "body": "Please add loading UI"}]},
        }
    )
    target = resolve(
        root=None,
        repo=None,
        pr=42,
        comment_id="555001",
        kind_hint=None,
        index=index,
        live=False,
    )
    assert target.kind == "discussion"
    assert target.post_method == "discussion_quote"
    assert target.mcp_tool == "add_issue_comment"


def test_child_inline_resolves_to_root_for_mcp() -> None:
    build_index, _, resolve, _ = _import_resolve()
    index = build_index(
        {
            "inline": [
                {"id": 200, "body": "root bug"},
                {"id": 201, "body": "nit", "in_reply_to_id": 200},
            ]
        }
    )
    target = resolve(
        root=None,
        repo=None,
        pr=7,
        comment_id="201",
        kind_hint="inline",
        index=index,
        live=False,
    )
    assert target.post_method == "review_reply"
    assert target.reply_to_id == "200"
    assert target.mcp_tool == "add_reply_to_pull_request_comment"
    assert "200" in (target.mcp_hint or "")


def test_ensure_quote_reply_prefixes_parent() -> None:
    _, ensure_quote, _, _ = _import_resolve()
    out = ensure_quote("Fixed in latest push.", "Can we add a loading state?")
    assert out.startswith(">")
    assert "Fixed in latest push." in out
    already = ensure_quote("> quoted\n\nDone.", "ignored")
    assert already.startswith(">")


def test_resolve_cli_offline(tmp_path: Path) -> None:
    cache_dir = Path("/tmp") / "heyeddi" / "pr-4242" / "respond"
    # Use the real temp path helper by writing via script import
    sys.modules.pop("_temp_store", None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    from _temp_store import comments_cache_path  # noqa: E402

    path = comments_cache_path(4242)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "pr": 4242,
                "repo": "acme/app",
                "inline": [
                    {"id": 9, "body": "root"},
                    {"id": 10, "body": "child", "in_reply_to_id": 9},
                ],
                "discussion": {"comments": [{"id": 77, "body": "ship it?"}]},
                "reviews": [],
            }
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "resolve_reply_targets.py"),
            "--pr",
            "4242",
            "--project-root",
            str(tmp_path),
            "--offline",
            "--comment-ids",
            "10,77:discussion",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    by_id = {t["input_id"]: t for t in data["targets"]}
    assert by_id["10"]["reply_to_id"] == "9"
    assert by_id["77"]["post_method"] == "discussion_quote"


def test_post_dry_run_includes_mcp_fallback(tmp_path: Path) -> None:
    replies = """## Comment 9001001 (inline)
Fixed.

## Comment 555001 (discussion)
Agreed — added skeleton.

## Comment 8001 (review)
Covered inline.

## Summary
Responded to 3/3.
"""
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "post_thread_replies.py"),
            "--pr",
            "42",
            "--project-root",
            str(tmp_path),
            "--dry-run",
            "--replies-text",
            replies,
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    by_id = {p["comment_id"]: p for p in data["posted"]}
    assert by_id["9001001"]["status"] == "dry-run"
    assert by_id["555001"]["post_method"] == "discussion_quote"
    assert by_id["8001"]["status"] == "skipped_review_body"
    assert "add_issue_comment" in (by_id["555001"].get("mcp_fallback") or "")
