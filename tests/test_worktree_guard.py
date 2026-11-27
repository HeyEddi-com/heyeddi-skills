"""The hook that stops a session from writing in a worktree another session owns."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "heyeddi" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session_worktree as sw  # noqa: E402
import worktree_guard as guard  # noqa: E402

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=cwd, check=True, capture_output=True, env=ENV,
    )


@pytest.fixture()
def trees(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)
    main, owned = tmp_path / "main", tmp_path / "owned"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    _git(main, "commit", "-qm", "base", "--allow-empty")
    _git(main, "worktree", "add", "-q", "-b", "feature", str(owned))
    sw.claim(owned, "s-owner", task="t", pr=None)
    return main, owned


def _decide(session: str, cwd: Path, tool: str, **tool_input: str) -> str:
    return guard.decide({"session_id": session, "cwd": str(cwd), "tool_name": tool, "tool_input": tool_input})[0]


@pytest.mark.parametrize("tool", ["Edit", "Write", "NotebookEdit"])
def test_only_the_owner_edits_files(trees: tuple[Path, Path], tool: str) -> None:
    main, owned = trees
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    target = {key: str(owned / "src" / "new.py")}
    assert _decide("s-other", main, tool, **target) == "deny"
    assert _decide("s-owner", main, tool, **target) == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m x",
        "rm -rf src",
        "echo hi > notes.md",
        "git status && git reset --hard",
        "python3 build.py",
        "sed -i s/a/b/ a.py",
    ],
)
def test_shell_writes_inside_a_foreign_worktree_are_denied(trees: tuple[Path, Path], command: str) -> None:
    _, owned = trees
    assert _decide("s-other", owned, "Bash", command=command) == "deny"
    assert _decide("s-owner", owned, "Bash", command=command) == "allow"


@pytest.mark.parametrize("template", ["cd {wt} && git push", "git -C {wt} checkout main", "rm {wt}/a.py", "git worktree remove {wt}"])
def test_reaching_in_from_outside_is_denied(trees: tuple[Path, Path], template: str) -> None:
    main, owned = trees
    assert _decide("s-other", main, "Bash", command=template.format(wt=owned)) == "deny"


def test_looking_stays_allowed(trees: tuple[Path, Path]) -> None:
    _, owned = trees
    assert _decide("s-other", owned, "Bash", command="git status && git log --oneline | head -3") == "allow"
    assert _decide("s-other", owned, "Read", file_path=str(owned / "a.py")) == "allow"


def test_unclaimed_checkout_is_not_blocked(trees: tuple[Path, Path]) -> None:
    main, _ = trees
    assert _decide("s-other", main, "Bash", command="git commit -m x") == "allow"


def test_taking_ownership_needs_the_users_click(trees: tuple[Path, Path]) -> None:
    main, owned = trees
    cmd = f"python3 session_worktree.py handoff --path {owned} --to s-other --user-approved"
    assert _decide("s-other", main, "Bash", command=cmd) == "ask"


def test_nobody_edits_the_marker(trees: tuple[Path, Path]) -> None:
    main, owned = trees
    marker = str(sw.marker_path(owned))
    assert _decide("s-other", main, "Write", file_path=marker) == "deny"
    assert _decide("s-other", main, "Bash", command=f"rm {marker}") == "deny"


def test_hook_speaks_the_claude_code_protocol(trees: tuple[Path, Path]) -> None:
    _, owned = trees
    event = {"session_id": "s-other", "cwd": str(owned), "tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "worktree_guard.py")], input=json.dumps(event),
        capture_output=True, text=True, env=ENV, check=True,
    )
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny" and "s-owner" in out["permissionDecisionReason"]


def test_install_adds_the_hook_once_and_keeps_other_settings(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"model": "x", "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": []}]}}))
    for _ in range(2):
        guard.install(tmp_path)
    data = json.loads(settings.read_text())
    assert data["model"] == "x"
    assert len(data["hooks"]["PreToolUse"]) == 2
    assert (tmp_path / "hooks" / "worktree_guard.py").is_file()
    assert (tmp_path / "hooks" / "session_worktree.py").is_file()
