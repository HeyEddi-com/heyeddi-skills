"""Inline PR review posting helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "heyeddi-pr-review" / "scripts"


def _load_mods():
    for name in ("post_inline_review", "verify_inline_review", "_skill_cli", "_auto_sync"):
        sys.modules.pop(name, None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    import post_inline_review as post  # noqa: E402
    import verify_inline_review as ver  # noqa: E402

    return post, ver


def test_post_inline_review_fixture_approve(tmp_path) -> None:
    post, _ = _load_mods()
    out = tmp_path / "posted.json"
    old = sys.argv
    sys.argv = [
        "post_inline_review.py",
        "--pr",
        "1",
        "--project-root",
        str(tmp_path),
        "--findings-json",
        "[]",
        "--fixture-out",
        str(out),
    ]
    try:
        post.main()
    finally:
        sys.argv = old
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["event"] == "APPROVE"
    assert data["comments"] == []
    assert "heyeddi-pr-review" in data["body"]


def test_post_inline_review_fixture_request_changes(tmp_path) -> None:
    post, ver = _load_mods()
    findings = tmp_path / "findings.json"
    findings.write_text(
        json.dumps(
            [
                {
                    "path": "src/a.py",
                    "line": 10,
                    "body": "**Severity:** high\n**Issue:** bug",
                }
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "posted.json"
    old = sys.argv
    sys.argv = [
        "post_inline_review.py",
        "--pr",
        "2",
        "--project-root",
        str(tmp_path),
        "--findings-file",
        str(findings),
        "--fixture-out",
        str(out),
    ]
    try:
        post.main()
    finally:
        sys.argv = old
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["event"] == "REQUEST_CHANGES"
    assert len(data["comments"]) == 1
    assert data["comments"][0]["path"] == "src/a.py"
    assert data["comments"][0]["line"] == 10
    assert "<!-- heyeddi-pr-review -->" in data["comments"][0]["body"]

    old = sys.argv
    sys.argv = [
        "verify_inline_review.py",
        "--pr",
        "2",
        "--project-root",
        str(tmp_path),
        "--findings-file",
        str(findings),
        "--posted-file",
        str(out),
        "--check",
    ]
    try:
        ver.main()
    finally:
        sys.argv = old
