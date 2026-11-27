"""Self-review: GitHub rejects APPROVE and REQUEST_CHANGES on your own PR."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "heyeddi-pr-review" / "scripts"

FAKE_GH = """#!{python}
import json, os, sys
a = sys.argv[1:]
if a[:2] == ["auth", "token"]:
    print("x")
elif a[:2] == ["repo", "view"]:
    print("o/r")
elif a[:2] == ["pr", "view"]:
    print(os.environ["FAKE_AUTHOR"] if "author" in a else "abc123")
elif a[:2] == ["api", "user"]:
    print("me")
elif a[0] == "api":
    body = open(a[a.index("--input") + 1]).read()
    open(os.environ["FAKE_OUT"], "w").write(body)
    print(json.dumps({{"id": 1, "html_url": "u"}}))
"""

FINDING = json.dumps([{"path": "a.py", "line": 1, "body": "**Issue:** x"}])


def _post(tmp_path: Path, author: str, findings: str) -> tuple[dict, dict]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH.format(python=sys.executable), encoding="utf-8")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    sent = tmp_path / "sent.json"
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
           "FAKE_AUTHOR": author, "FAKE_OUT": str(sent)}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "post_inline_review.py"), "--pr", "5",
         "--project-root", str(tmp_path), "--findings-json", findings],
        env=env, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    return json.loads(sent.read_text(encoding="utf-8")), json.loads(proc.stdout[proc.stdout.index("{"):])


@pytest.mark.parametrize("findings", [FINDING, "[]"])
def test_own_pr_is_posted_as_comment(tmp_path: Path, findings: str) -> None:
    sent, out = _post(tmp_path, "me", findings)
    assert sent["event"] == "COMMENT"
    assert sent["body"].strip()
    assert out["event"] == "COMMENT" and out["self_review"] is True


def test_other_authors_pr_keeps_the_verdict(tmp_path: Path) -> None:
    sent, _ = _post(tmp_path, "someone-else", FINDING)
    assert sent["event"] == "REQUEST_CHANGES"
    sent, _ = _post(tmp_path, "someone-else", "[]")
    assert sent["event"] == "APPROVE"


def _verify(tmp_path: Path, posted: dict) -> int:
    path = tmp_path / "posted.json"
    path.write_text(json.dumps(posted), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "verify_inline_review.py"), "--pr", "5",
         "--project-root", str(tmp_path), "--posted-file", str(path), "--check"],
        capture_output=True, text=True, check=False,
    ).returncode


def test_clean_self_review_verifies(tmp_path: Path) -> None:
    sent, _ = _post(tmp_path, "me", "[]")
    assert _verify(tmp_path, sent) == 0


def test_plain_comment_review_is_not_a_clean_result(tmp_path: Path) -> None:
    assert _verify(tmp_path, {"event": "COMMENT", "body": "<!-- heyeddi-pr-review -->\nhm", "comments": []}) == 1
