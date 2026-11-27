"""Pre-merge gate: only a PR author's marked decline with a reason may leave a thread open."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from _skill_loader import load_skill_script


def _gate():
    return load_skill_script("pre-merge-gate", "pre_merge_gate")


def _thread(body: str, *, author: str = "dev", total: int = 2, resolved: bool = False) -> dict:
    return {
        "isResolved": resolved,
        "path": "src/app.py",
        "line": 12,
        "comments": {
            "totalCount": total,
            "nodes": [{"body": body, "url": "https://github.com/o/r/pull/7#discussion_r1", "author": {"login": author}}],
        },
    }


def test_author_decline_with_reason_passes_and_is_listed() -> None:
    blocking, declined = _gate().triage_threads(
        [_thread("**Declined:** the caller already validates this value.")], "dev"
    )
    assert blocking == []
    assert declined == [
        {
            "path": "src/app.py",
            "line": 12,
            "url": "https://github.com/o/r/pull/7#discussion_r1",
            "reason": "the caller already validates this value.",
        }
    ]


@pytest.mark.parametrize(
    "thread",
    [
        _thread("Fixed in abc123."),
        _thread("I will look at this later."),
        _thread("Partially fixed: the rest is fine as it is."),
        _thread("**Declined:**"),
        _thread("Declined: no."),
        _thread("We have not declined: this is still open to discuss."),
        _thread("**Declined:** the caller already validates this value.", author="reviewer"),
        _thread("**Declined:** the caller already validates this value.", total=1),
    ],
)
def test_every_other_open_thread_blocks(thread: dict) -> None:
    blocking, declined = _gate().triage_threads([thread], "dev")
    assert len(blocking) == 1
    assert declined == []


def test_unknown_pr_author_blocks() -> None:
    blocking, _ = _gate().triage_threads([_thread("Declined: the caller already validates it.")], "")
    assert len(blocking) == 1


def test_resolved_threads_are_ignored() -> None:
    assert _gate().triage_threads([_thread("anything", resolved=True)], "dev") == ([], [])


def test_run_pr_checks_pages_threads_and_reports_declines(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    gate = _gate()
    pages = [
        ([_thread("**Declined:** the caller already validates this value.")], True),
        ([_thread("Please change this.", author="reviewer", total=1)], False),
    ]

    def fake(cmd, cwd, timeout=600):
        if cmd[:3] == ["gh", "pr", "checks"]:
            return "all pass"
        if cmd[:3] == ["gh", "repo", "view"]:
            return "o/r"
        nodes, more = pages.pop(0)
        return json.dumps(
            {
                "data": {
                    "repository": {
                        "pullRequest": {
                            "author": {"login": "dev"},
                            "reviewThreads": {"pageInfo": {"hasNextPage": more, "endCursor": "c1"}, "nodes": nodes},
                        }
                    }
                }
            }
        )

    monkeypatch.setattr(gate, "gh_status", lambda root: {"ok": True})
    monkeypatch.setattr(gate, "run_command", fake)
    rows: list = []
    declined: list = []
    gate.run_pr_checks(tmp_path, 7, rows, declined)
    row = {name: (st, note) for name, st, note in rows}["pr-review-threads"]
    assert row[0] == "FAIL" and row[1].startswith("1 unresolved")
    assert len(declined) == 1

    md, payload, _ = gate.build_report(rows, pr=7, signoff=True, emergency_used=[], declined=declined)
    assert "Declined threads" in md and "discussion_r1" in md and "already validates" in md
    assert payload["declined_threads"] == declined
