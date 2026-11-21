"""The gh CLI is optional: a missing or logged-out gh degrades, it never crashes or passes.

Contract for every script that talks to GitHub when gh cannot be used:
- exit code 3 (not 0, not a traceback, not the exit 1 that means a real failure)
- stdout is JSON with status "degraded", the reason, and what to do by hand
- nothing is reported as posted, verified or merge-ready
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from _skill_loader import REPO, load_skill_script

SKILLS = REPO / "skills"
PR = 987654


def _sandbox(tmp_path: Path, gh_script: str | None) -> dict[str, str]:
    """Env whose PATH has python and git but only the gh we hand it."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("git", "bash", "sh", "env"):
        found = shutil.which(tool)
        if found:
            (bin_dir / tool).symlink_to(found)
    if gh_script is not None:
        gh = bin_dir / "gh"
        gh.write_text("#!/usr/bin/env bash\n" + gh_script)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    return {"PATH": str(bin_dir), "TMPDIR": str(tmp), "HOME": str(tmp_path), "PYTHONDONTWRITEBYTECODE": "1"}


def _run(env: dict[str, str], skill: str, script: str, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SKILLS / skill / "scripts" / script), "--project-root", str(cwd), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=60,
    )


def _git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    return repo


REPLIES = "## Comment 1\nFixed.\n\n## Summary\nDone.\n"
FINDING = json.dumps([{"path": "a.py", "line": 3, "body": "bug"}])

CASES = [
    ("heyeddi-pr-review", "fetch_pr_context.py", ["--pr", str(PR)]),
    ("heyeddi-pr-respond", "fetch_pr_comments.py", ["--pr", str(PR)]),
    ("heyeddi-ci-fails", "fetch_failing_checks.py", ["--pr", str(PR)]),
    ("heyeddi-pr-review", "verify_inline_review.py", ["--pr", str(PR), "--check"]),
    ("heyeddi-pr-review", "post_inline_review.py", ["--pr", str(PR), "--findings-json", FINDING]),
    ("heyeddi-pr-respond", "verify_response.py", ["--pr", str(PR), "--replies-text", REPLIES, "--live", "--check"]),
    ("heyeddi-pr-respond", "post_thread_replies.py", ["--pr", str(PR), "--replies-text", REPLIES, "--allow-unpushed"]),
]


@pytest.mark.parametrize(("skill", "script", "args"), CASES, ids=[c[1] for c in CASES])
def test_missing_gh_degrades(skill: str, script: str, args: list[str], tmp_path: Path) -> None:
    env = _sandbox(tmp_path, gh_script=None)
    assert shutil.which("gh", path=env["PATH"]) is None
    result = _run(env, skill, script, *args, cwd=_git_repo(tmp_path))
    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == 3, (result.returncode, result.stdout, result.stderr)
    out = json.loads(result.stdout)
    assert out["status"] == "degraded"
    assert out["gh"]["state"] == "missing"
    assert out["manual"], "must say what to do without gh"


def test_logged_out_gh_degrades(tmp_path: Path) -> None:
    env = _sandbox(tmp_path, gh_script='if [ "$1 $2" = "auth token" ]; then exit 1; fi\necho should-not-run >&2\nexit 9\n')
    result = _run(env, "heyeddi-pr-respond", "fetch_pr_comments.py", "--pr", str(PR), cwd=_git_repo(tmp_path))
    assert result.returncode == 3, (result.stdout, result.stderr)
    out = json.loads(result.stdout)
    assert out["gh"]["state"] == "unauthenticated"
    assert "gh auth login" in out["gh"]["hint"]


def test_logged_in_gh_is_ok_and_token_is_not_leaked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env = _sandbox(tmp_path, gh_script='if [ "$1 $2" = "auth token" ]; then echo ghp_secret123; exit 0; fi\nexit 9\n')
    monkeypatch.setenv("PATH", env["PATH"])
    cli = load_skill_script("heyeddi-pr-respond", "_skill_cli")
    status = cli.gh_status(tmp_path)
    assert status["ok"] is True
    assert status["state"] == "ok"
    assert "ghp_secret123" not in json.dumps(status)


def test_degraded_fetch_removes_stale_cache(tmp_path: Path) -> None:
    """A cache from an earlier run must not pass for fresh data once gh is gone."""
    env = _sandbox(tmp_path, gh_script=None)
    cache = Path(env["TMPDIR"]) / "heyeddi" / f"pr-{PR}" / "respond" / "comments.json"
    cache.parent.mkdir(parents=True)
    cache.write_text('{"inline": [{"id": 1}]}')
    result = _run(env, "heyeddi-pr-respond", "fetch_pr_comments.py", "--pr", str(PR), cwd=_git_repo(tmp_path))
    assert result.returncode == 3
    assert not cache.exists()


def test_degraded_post_names_what_was_not_posted(tmp_path: Path) -> None:
    env = _sandbox(tmp_path, gh_script=None)
    result = _run(env, "heyeddi-pr-review", "post_inline_review.py", "--pr", str(PR), "--findings-json", FINDING, cwd=_git_repo(tmp_path))
    out = json.loads(result.stdout)
    assert out["payload"]["comments"][0]["path"] == "a.py"
    assert out["posted"] is False


def test_explicit_dry_run_still_works_without_gh(tmp_path: Path) -> None:
    env = _sandbox(tmp_path, gh_script=None)
    result = _run(env, "heyeddi-pr-review", "post_inline_review.py", "--pr", str(PR), "--findings-json", FINDING, "--dry-run", cwd=_git_repo(tmp_path))
    assert result.returncode == 0
    assert json.loads(result.stdout)["dry_run"] is True


# --- pre-merge gate: "could not check" is neither PASS nor FAIL -------------------------


def test_gate_unverified_is_not_ok_and_exits_3() -> None:
    gate = load_skill_script("pre-merge-gate", "pre_merge_gate")
    rows = [("setup-audit", "PASS", ""), ("pr-checks", "UNVERIFIED", "gh CLI not found")]
    _text, payload, code = gate.build_report(rows, pr=None, signoff=True, emergency_used=[])
    assert code == 3
    assert payload["ok"] is False
    assert payload["overall"] == "UNVERIFIED"
    assert payload["unverified_count"] == 1


def test_gate_fail_outranks_unverified() -> None:
    gate = load_skill_script("pre-merge-gate", "pre_merge_gate")
    rows = [("test", "FAIL", "red"), ("pr-checks", "UNVERIFIED", "gh CLI not found")]
    _text, payload, code = gate.build_report(rows, pr=7, signoff=True, emergency_used=[])
    assert code == 1
    assert payload["overall"] == "BLOCKED"


def test_gate_signoff_without_gh_cannot_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """--signoff used to skip PR checks silently when gh could not find the PR."""
    gate = load_skill_script("pre-merge-gate", "pre_merge_gate")
    monkeypatch.setattr(gate, "gh_status", lambda cwd=None: {"ok": False, "state": "missing", "reason": "gh CLI not found on PATH", "hint": ""})
    rows: list[tuple[str, str, str]] = []
    gate.add_unverified_pr_rows(tmp_path, rows)
    assert {name for name, _st, _ in rows} == {"pr-checks", "pr-review-threads"}
    assert all(st == "UNVERIFIED" for _n, st, _ in rows)
    _t, _p, code = gate.build_report(rows, pr=None, signoff=True, emergency_used=[])
    assert code == 3


def test_gate_run_pr_checks_without_gh_is_unverified_not_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    gate = load_skill_script("pre-merge-gate", "pre_merge_gate")
    monkeypatch.setattr(gate, "gh_status", lambda cwd=None: {"ok": False, "state": "unauthenticated", "reason": "gh is installed but not logged in", "hint": ""})
    rows: list[tuple[str, str, str]] = []
    gate.run_pr_checks(tmp_path, 5, rows)
    assert [st for _n, st, _ in rows] == ["UNVERIFIED", "UNVERIFIED"]


def test_verify_inline_review_with_nothing_to_check_fails(tmp_path: Path) -> None:
    """0 expected, 0 posted and no APPROVE used to report ok, so --check passed on nothing."""
    posted = tmp_path / "posted.json"
    posted.write_text(json.dumps({"event": "COMMENT", "comments": []}))
    env = _sandbox(tmp_path, gh_script=None)
    result = _run(env, "heyeddi-pr-review", "verify_inline_review.py", "--pr", str(PR), "--posted-file", str(posted), "--check", cwd=_git_repo(tmp_path))
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert "nothing verified" in result.stdout


def test_verify_inline_review_clean_approve_passes(tmp_path: Path) -> None:
    posted = tmp_path / "posted.json"
    posted.write_text(json.dumps({"event": "APPROVE", "comments": []}))
    env = _sandbox(tmp_path, gh_script=None)
    result = _run(env, "heyeddi-pr-review", "verify_inline_review.py", "--pr", str(PR), "--posted-file", str(posted), "--check", cwd=_git_repo(tmp_path))
    assert result.returncode == 0, (result.stdout, result.stderr)
