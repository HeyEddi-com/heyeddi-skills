"""Tests for unified heyeddi-pr-respond (merged with ci-respond)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESPOND = ROOT / "skills" / "heyeddi-pr-respond" / "scripts"
FIXTURE = ROOT / "skills" / "heyeddi-pr-respond" / "fixtures" / "sample-pr-comments.json"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_build_comment_inventory_links_review_bullets(tmp_path: Path) -> None:
    comments = {
        "pr": 71,
        "repo": "org/repo",
        "inline": [
            {
                "id": 101,
                "path": "backend/app/review_subagents.py",
                "line": 185,
                "body": "<!-- heyeddi-ci-review --> focus path bug",
                "user": {"login": "heyeddi-ci[bot]"},
            },
            {
                "id": 102,
                "path": "backend/app/usage_analytics.py",
                "line": 56,
                "body": "<!-- heyeddi-ci-review --> token double count",
                "user": {"login": "heyeddi-ci[bot]"},
            },
        ],
        "discussion": {"comments": []},
        "reviews": [
            {
                "id": 9001,
                "body": (
                    "**Commented on the diff**\n"
                    "1. focus path — `backend/app/review_subagents.py:185`\n"
                    "2. token usage — `backend/app/usage_analytics.py:56`\n"
                ),
                "author": {"login": "heyeddi-ci[bot]"},
                "state": "CHANGES_REQUESTED",
            }
        ],
    }
    cache = tmp_path / "comments.json"
    cache.write_text(json.dumps(comments), encoding="utf-8")
    proc = _run(
        RESPOND / "build_comment_inventory.py",
        "--pr",
        "71",
        "--project-root",
        str(tmp_path),
        "--input",
        str(cache),
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    inv = json.loads(proc.stdout)
    assert inv["postable_count"] == 2
    assert set(inv["postable_reply_ids"]) == {"101", "102"}
    assert inv["items"][0]["listed_in_review"] == ["9001"] or any(
        i.get("listed_in_review") == ["9001"] for i in inv["items"]
    )


def test_fetch_pr_comments_fixture_uses_temp_not_docs(tmp_path: Path) -> None:
    proc = _run(
        RESPOND / "fetch_pr_comments.py",
        "--pr",
        "42",
        "--project-root",
        str(tmp_path),
        "--fixture",
        str(FIXTURE),
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(proc.stdout)
    assert data.get("ephemeral") is True
    assert not (tmp_path / ".heyeddi" / "docs" / "pr-42-comments.json").exists()


def test_filter_comments_scope_all(tmp_path: Path) -> None:
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps(
            {
                "pr": 9,
                "inline": [
                    {"id": 1, "body": "<!-- heyeddi-ci-review --> x", "user": {"login": "heyeddi-ci[bot]"}},
                    {"id": 2, "body": "human", "user": {"login": "human"}},
                ],
                "discussion": {"comments": []},
                "reviews": [],
            }
        ),
        encoding="utf-8",
    )
    out = Path(tempfile.gettempdir()) / "heyeddi-test-pr-9-all.json"
    proc = _run(
        RESPOND / "filter_comments.py",
        "--pr",
        "9",
        "--project-root",
        str(tmp_path),
        "--input",
        str(src),
        "--output",
        str(out),
        "--scope",
        "all",
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["inline"]) == 2
