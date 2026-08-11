"""Hard gate: every PR comment must have a reply draft (--replies-text) and verify passes."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "heyeddi-pr-respond" / "scripts"
FIXTURE = REPO / "skills" / "heyeddi-pr-respond" / "fixtures" / "sample-pr-comments.json"

REPLIES_COMPLETE = """# PR #42 replies

## Comment 9001001 (inline)
Fixed - Pagination is 1-based.

## Comment 9001002 (inline)
Fixed - Removed redundant Depends.

## Comment DC_10001 (discussion)
@product-owner Added loading skeleton.

## Comment 8001 (review)
@backend-lead Addressed inline notes.

## Comment 8002 (review)
@qa-reviewer Thanks, CI is green after fixes.

## Summary
Responded to 5/5 comments. Ready for re-review.
"""


def _run(script: str, tmp: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *extra, "--project-root", str(tmp)],
        capture_output=True,
        text=True,
    )


def test_verify_fails_without_per_id_sections(tmp_path: Path) -> None:
    proc = _run(
        "verify_response.py",
        tmp_path,
        "--pr",
        "42",
        "--check",
        "--fixture",
        str(FIXTURE),
        "--replies-text",
        "# PR #42 replies\n\n## Summary\nResponded to 5/5.\n",
        "--allow-draft-only",
    )
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["status"] == "fail"
    assert any("no ## Comment" in m or "missing expected" in m for m in data["missing"])


def test_verify_fails_when_summary_not_last(tmp_path: Path) -> None:
    bad = REPLIES_COMPLETE.replace(
        "## Summary\nResponded to 5/5 comments. Ready for re-review.\n",
        "## Summary\nToo early.\n\n## Comment 9999 (inline)\nLate reply.\n",
    )
    proc = _run(
        "verify_response.py",
        tmp_path,
        "--pr",
        "42",
        "--check",
        "--fixture",
        str(FIXTURE),
        "--replies-text",
        bad,
        "--allow-draft-only",
    )
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert any("Summary must be the last" in m for m in data["missing"])


def test_verify_passes_with_fixture_drafts(tmp_path: Path) -> None:
    proc = _run(
        "verify_response.py",
        tmp_path,
        "--pr",
        "42",
        "--check",
        "--fixture",
        str(FIXTURE),
        "--replies-text",
        REPLIES_COMPLETE,
        "--allow-draft-only",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    assert data["status"] == "ok"
    assert data["draft_count"] == 5


def test_verify_requires_replies_text(tmp_path: Path) -> None:
    proc = _run("verify_response.py", tmp_path, "--pr", "42", "--check", "--allow-draft-only")
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert any("missing replies draft" in m for m in data["missing"])


def test_post_dry_run_skips_review_bodies_no_top_level(tmp_path: Path) -> None:
    post = _run(
        "post_thread_replies.py",
        tmp_path,
        "--pr",
        "42",
        "--dry-run",
        "--replies-text",
        REPLIES_COMPLETE,
    )
    assert post.returncode == 0, post.stdout + post.stderr
    post_data = json.loads(post.stdout)
    by_id = {p["comment_id"]: p for p in post_data["posted"]}
    assert by_id["9001001"]["status"] == "dry-run"
    assert by_id["8001"]["status"] == "skipped_review_body"
    assert by_id["8002"]["status"] == "skipped_review_body"
    assert post_data["posted_count"] == 5


def test_banned_acknowledgement_body(tmp_path: Path) -> None:
    bad = REPLIES_COMPLETE.replace(
        "Fixed - Pagination is 1-based.",
        "Acknowledged review attachment PRR_kWD0Tefbwc8AAAABI1ELng — inline threads carry the detailed responses.",
    )
    post = _run(
        "post_thread_replies.py",
        tmp_path,
        "--pr",
        "42",
        "--dry-run",
        "--replies-text",
        bad,
    )
    assert post.returncode == 1
    data = json.loads(post.stdout)
    assert data["error_count"] >= 1
    assert any("banned" in e.lower() for e in data["errors"])


def test_parse_helpers_unit() -> None:
    sys.modules.pop("_replies_parse", None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    from _replies_parse import (  # noqa: E402
        infer_reply_kind,
        parse_reply_sections,
        parse_tracking_rows,
        summary_is_last,
    )

    tracking = """| Comment ID | Type | Author | Summary | Action | Status |
| 9001001 | inline | qa | x | fix | PENDING |"""
    rows = parse_tracking_rows(tracking)
    assert rows[0].comment_id == "9001001"
    sections, summary = parse_reply_sections(REPLIES_COMPLETE)
    assert len(sections) == 5
    assert summary and "5/5" in summary
    assert summary_is_last(REPLIES_COMPLETE)
    assert infer_reply_kind("9001001", "inline", None) == "inline"
    assert infer_reply_kind("DC_10001", None, None) == "discussion"
    assert infer_reply_kind("8001", "review", None) == "review"
