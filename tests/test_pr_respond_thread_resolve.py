"""Thread resolution replies only on unresolved review threads, at the root id."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "heyeddi-pr-respond" / "scripts"


def _import_resolve():
    for name in ("_comment_resolve", "_skill_cli", "_untrusted_doc", "_temp_store"):
        sys.modules.pop(name, None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    from _comment_resolve import (  # noqa: E402
        build_comment_index,
        resolve_reply_target,
        walk_to_root,
    )

    return build_comment_index, resolve_reply_target, walk_to_root


def test_walk_to_root_follows_chain() -> None:
    build_index, _, walk = _import_resolve()
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
    build_index, resolve, _ = _import_resolve()
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
    assert target.post_method == "skip_issue_comment"
    assert target.reply_to_id is None
    assert target.mcp_tool is None
    assert "Do not quote-reply" in (target.detail or "")


def test_child_inline_resolves_to_root_for_mcp() -> None:
    build_index, resolve, _ = _import_resolve()
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


def test_self_review_roots_postable_answered_still_skipped() -> None:
    build_index, resolve, _ = _import_resolve()
    index = build_index(
        {
            "inline": [
                {
                    "id": 300,
                    "body": "I left this note",
                    "user": {"login": "author"},
                    "created_at": "2026-11-06T00:00:00Z",
                },
                {
                    "id": 400,
                    "body": "please fix",
                    "user": {"login": "reviewer"},
                    "created_at": "2026-11-06T00:00:00Z",
                },
                {
                    "id": 401,
                    "body": "Fixed.",
                    "in_reply_to_id": 400,
                    "user": {"login": "author"},
                    "created_at": "2026-11-06T01:00:00Z",
                },
            ],
            "discussion": {
                "comments": [
                    {
                        "id": 500,
                        "body": "<!-- heyeddi:tests-hold:abc -->\nHeyEddi did not review this commit.",
                        "user": {"login": "heyeddi-ci[bot]"},
                    }
                ]
            },
        }
    )
    own = resolve(
        root=None,
        repo=None,
        pr=1,
        comment_id="300",
        kind_hint="inline",
        index=index,
        live=False,
        responder_login="author",
    )
    # Self-review findings stay postable (same login left the root finding).
    assert own.post_method == "review_reply"
    assert own.reply_to_id == "300"
    answered = resolve(
        root=None,
        repo=None,
        pr=1,
        comment_id="400",
        kind_hint="inline",
        index=index,
        live=False,
        responder_login="author",
    )
    assert answered.post_method == "skip_answered"
    assert answered.reply_to_id == "400"
    hold = resolve(
        root=None,
        repo=None,
        pr=1,
        comment_id="500",
        kind_hint=None,
        index=index,
        live=False,
        responder_login="author",
    )
    assert hold.post_method == "skip_issue_comment"
    assert "Tests-hold" in (hold.detail or "")


def test_index_uses_raw_body_not_untrusted_banner() -> None:
    build_index, _, _ = _import_resolve()
    sys.modules.pop("_untrusted_doc", None)
    from _untrusted_doc import wrap_untrusted_doc  # noqa: E402

    plain = "Can we add a loading state?"
    wrapped = wrap_untrusted_doc("pr-comment-body", plain)
    assert wrapped is not None
    index = build_index(
        {
            "inline": [
                {
                    "id": 1,
                    "body": wrapped,
                    "body_raw": plain,
                    "user": {"login": "qa-reviewer"},
                }
            ]
        }
    )
    assert index["1"].body == plain
    assert "<<<UNTRUSTED_" not in index["1"].body

    banner_only = build_index({"inline": [{"id": 2, "body": wrapped}]})
    assert banner_only["2"].body == plain
    assert "<<<UNTRUSTED_" not in banner_only["2"].body


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
    assert by_id["77"]["post_method"] == "skip_issue_comment"
    assert by_id["77"]["reply_to_id"] is None


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
    assert by_id["9001001"]["post_method"] == "review_reply"
    assert by_id["555001"]["post_method"] == "skip_issue_comment"
    assert by_id["555001"]["status"] == "skipped_issue_comment"
    assert by_id["8001"]["status"] == "skipped_review_body"
    assert "add_issue_comment" not in json.dumps(by_id["555001"])
