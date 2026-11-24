"""Resolve a review thread once its "Fixed" reply is posted.

The HeyEddi Reviewer will not review a new commit while a thread stays open,
so a fixed finding must not leave its thread unresolved. Declines stay open
for the reviewer to accept or push back.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "heyeddi-pr-respond" / "scripts"

REPLIES = """# PR #42 replies

## Comment 9001001 (inline)
Fixed - Pagination is 1-based.

## Comment 9001002 (inline)
Declined: the extra Depends is needed for the auth override.

## Summary
Fixed 1, declined 1.
"""


def _import():
    for name in ("_comment_resolve", "_skill_cli", "_untrusted_doc", "_temp_store"):
        sys.modules.pop(name, None)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import _comment_resolve  # noqa: E402

    return _comment_resolve


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("Fixed - Pagination is 1-based.", True),
        ("**Fixed** in abc123.", True),
        ("fixed: renamed the helper", True),
        ("Done. Moved the check before the write.", True),
        ("Addressed in 4f2e1aa.", True),
        ("Declined: out of scope.", False),
        ("Not fixed yet, see the summary.", False),
        ("Partially fixed: the rest is a follow-up.", False),
        ("Good catch. Fixed in the next commit.", False),
    ],
)
def test_is_fixed_reply(body: str, expected: bool) -> None:
    assert _import().is_fixed_reply(body) is expected


def test_resolve_review_thread_runs_the_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _import()
    calls: list[list[str]] = []
    lookup = {
        "data": {
            "repository": {
                "pullRequest": {
                    "reviewThreads": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [{"id": "PRRT_1", "comments": {"nodes": [{"databaseId": 9001001}]}}],
                    }
                }
            }
        }
    }
    resolved = {"data": {"resolveReviewThread": {"thread": {"id": "PRRT_1", "isResolved": True}}}}

    def fake(cmd: list[str], root: Path, stdin_text: str | None = None) -> str:
        calls.append(cmd)
        query = next(a for a in cmd if a.startswith("query="))
        return json.dumps(resolved if "resolveReviewThread" in query else lookup)

    monkeypatch.setattr(mod, "run_command", fake)
    status, detail = mod.resolve_review_thread(Path("."), "acme/app", 42, "9001001")
    assert status == "resolved", detail
    assert detail == "PRRT_1"
    assert any("threadId=PRRT_1" in a for a in calls[-1])


def test_resolve_review_thread_reports_a_missing_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _import()
    empty = {"data": {"repository": {"pullRequest": {"reviewThreads": {"pageInfo": {}, "nodes": []}}}}}
    monkeypatch.setattr(mod, "run_command", lambda cmd, root, stdin_text=None: json.dumps(empty))
    status, _ = mod.resolve_review_thread(Path("."), "acme/app", 42, "1")
    assert status == "error"


def _post(tmp: Path, *extra: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "post_thread_replies.py"), "--pr", "42", "--dry-run",
         "--replies-text", REPLIES, "--project-root", str(tmp), *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return {p["comment_id"]: p for p in json.loads(proc.stdout)["posted"]}


def test_dry_run_marks_only_fixed_threads_for_resolving(tmp_path: Path) -> None:
    by_id = _post(tmp_path)
    assert by_id["9001001"]["resolve"] == "would-resolve"
    assert by_id["9001002"]["resolve"] == "left-open"


def test_no_resolve_flag_leaves_every_thread_open(tmp_path: Path) -> None:
    by_id = _post(tmp_path, "--no-resolve")
    assert by_id["9001001"]["resolve"] == "left-open"
