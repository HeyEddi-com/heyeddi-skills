"""Session markers: owner, contributors, and what each may do in a worktree."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "heyeddi" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session_worktree as sw  # noqa: E402


def _isolated_env() -> dict[str, str]:
    # Fixture repos must never inherit GIT_DIR from a hook running this suite:
    # that once wrote a fake identity into a real repository's config.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "fixture"
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "fixture@example.invalid"
    return env


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=_isolated_env()
    ).stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    for key in list(os.environ):
        if key.startswith("GIT_") or key in sw.SESSION_ENV_VARS:
            monkeypatch.delenv(key, raising=False)
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    (main / "a.txt").write_text("a\n", encoding="utf-8")
    _git(main, "add", "a.txt")
    _git(main, "commit", "-qm", "base")
    wt = tmp_path / "wt-feature"
    _git(main, "worktree", "add", "-q", "-b", "feature", str(wt))
    return main, wt


def test_marker_lives_in_git_dir_and_is_never_tracked(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    out = sw.claim(wt, "s-owner", task="fix login", pr=None)
    marker = Path(out["marker"])
    assert marker.is_file()
    assert wt not in marker.parents
    assert _git(wt, "status", "--porcelain") == ""


def test_claim_on_another_sessions_worktree_is_refused(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    sw.claim(wt, "s-owner", task="fix login", pr=None)
    out = sw.claim(wt, "s-stranger", task="me too", pr=None)
    assert out["ok"] is False
    assert [s["id"] for s in sw.load_marker(wt)["sessions"]] == ["s-owner"]
    assert sw.check(wt, "s-stranger", "commit")[0] == 1
    assert sw.main(["claim", "--path", str(wt), "--session", "s-stranger"]) == 1


def test_first_claim_owns_later_claims_contribute(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    assert sw.claim(wt, "s-owner", task="fix login", pr=None)["role"] == "owner"
    assert sw.claim(wt, "s-helper", task="add test", pr=None, user_approved=True)["role"] == "contributor"
    marker = sw.load_marker(wt)
    assert marker["owner"] == "s-owner"
    assert marker["task"] == "fix login"
    assert [s["id"] for s in marker["sessions"]] == ["s-owner", "s-helper"]
    assert marker["branch"] == "feature"


@pytest.mark.parametrize(
    ("session", "action", "code"),
    [
        ("s-owner", "merge", 0),
        ("s-owner", "delete", 0),
        ("s-helper", "commit", 0),
        ("s-helper", "push", 0),
        ("s-helper", "merge", 1),
        ("s-helper", "force-push", 1),
        ("s-stranger", "commit", 1),
        ("s-stranger", "delete", 1),
    ],
)
def test_check_gates_by_role(repo: tuple[Path, Path], session: str, action: str, code: int) -> None:
    _, wt = repo
    sw.claim(wt, "s-owner", task="t", pr=None)
    sw.claim(wt, "s-helper", task=None, pr=None, user_approved=True)
    assert sw.check(wt, session, action)[0] == code


def test_check_without_marker_is_read_only(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    code, result = sw.check(wt, "s-any", "commit")
    assert code == 2
    assert "read-only" in result["reason"]


def test_handoff_needs_owner_or_user(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    sw.claim(wt, "s-owner", task="t", pr=None)
    sw.claim(wt, "s-helper", task=None, pr=None, user_approved=True)
    assert sw.handoff(wt, "s-helper", "s-helper", user_approved=False)[0] == 1
    assert sw.handoff(wt, "s-helper", "s-helper", user_approved=True)[0] == 0
    marker = sw.load_marker(wt)
    assert marker["owner"] == "s-helper"
    assert marker["history"][-1]["user_approved"] is True
    assert sw.check(wt, "s-owner", "merge")[0] == 1


def test_list_marks_mine(repo: tuple[Path, Path]) -> None:
    main, wt = repo
    sw.claim(wt, "s-owner", task="fix login", pr="https://example.invalid/pull/1")
    rows = {Path(r["path"]).name: r for r in sw.list_worktrees(main, "s-owner")}
    assert rows["wt-feature"]["mine"] == "owner"
    assert rows["wt-feature"]["pr"] == "https://example.invalid/pull/1"
    assert rows["main"]["owner"] == ""
    assert rows["main"]["mine"] == "none"


def test_cli_uses_session_env(repo: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    _, wt = repo
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s-env")
    assert sw.main(["claim", "--path", str(wt), "--task", "env"]) == 0
    assert sw.load_marker(wt)["owner"] == "s-env"
    assert sw.main(["check", "--path", str(wt), "--action", "merge"]) == 0


def test_concurrent_claims_keep_every_session(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    script = SCRIPTS / "session_worktree.py"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    procs = [
        subprocess.Popen(
            [sys.executable, str(script), "claim", "--path", str(wt), "--session", f"s-{i}", "--user-approved"],
            stdout=subprocess.DEVNULL,
            env=env,
        )
        for i in range(12)
    ]
    assert all(p.wait() == 0 for p in procs)
    marker = sw.load_marker(wt)
    assert sorted(s["id"] for s in marker["sessions"]) == sorted(f"s-{i}" for i in range(12))
    assert [s["role"] for s in marker["sessions"]].count("owner") == 1


def test_cli_without_session_fails(repo: tuple[Path, Path]) -> None:
    _, wt = repo
    with pytest.raises(SystemExit):
        sw.main(["claim", "--path", str(wt)])
