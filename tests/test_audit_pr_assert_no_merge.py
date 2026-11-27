"""assert_no_merge: production merges stay blocked; ordinary branch updates do not."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "heyeddi-pr-respond" / "scripts" / "assert_no_merge.py"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
        cwd=root, env=ENV, check=True, capture_output=True,
    )


def _repo(path: Path, branch: str, stack: dict | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "main")
    _git(path, "commit", "-q", "--allow-empty", "-m", "init")
    if stack is not None:
        (path / ".heyeddi").mkdir()
        (path / ".heyeddi" / "stack.json").write_text(json.dumps(stack), encoding="utf-8")
    if branch != "main":
        _git(path, "checkout", "-q", "-b", branch)
    return path


def _check(root: Path, command: str, *extra: str) -> int:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root), "--planned-command", command, "--check", *extra],
        env=ENV, capture_output=True, text=True, check=False,
    ).returncode


@pytest.mark.parametrize(
    "command",
    [
        "git merge origin/main",
        "git merge --abort",
        "git merge --continue",
        "git merge-base HEAD origin/main",
        "git fetch origin && git merge --no-edit origin/main",
    ],
)
def test_feature_branch_updates_are_allowed(tmp_path: Path, command: str) -> None:
    assert _check(_repo(tmp_path / "r", "feat/x"), command) == 0


@pytest.mark.parametrize(
    "command",
    [
        "git merge feat/x",
        "git merge --no-ff feat/x",
        "git -c core.editor=true merge feat/x",
        "git merge --continue",
    ],
)
def test_git_merge_on_production_is_blocked(tmp_path: Path, command: str) -> None:
    repo = _repo(tmp_path / "r", "main")
    assert _check(repo, command) == 1
    assert _check(repo, command, "--base", "staging") == 1
    assert _check(repo, command, "--user-text", "authorize merge") == 0


@pytest.mark.parametrize(
    "command",
    [
        "git checkout main && git merge feat/x",
        "git switch main; git merge feat/x",
        "cd ../other && git merge feat/x",
        "git -C ../other merge feat/x",
        "git checkout - && git merge feat/x",
        "bash -c 'git merge feat/x'",
        "git status\ngit checkout main\ngit merge feat/x",
        "gh api -X PUT repos/o/r/pulls/3/merge",
    ],
)
def test_hidden_or_switched_targets_are_blocked(tmp_path: Path, command: str) -> None:
    assert _check(_repo(tmp_path / "r", "feat/x"), command) == 1


def test_no_repository_means_unknown_target(tmp_path: Path) -> None:
    assert _check(tmp_path, "git merge feat/x") == 1


def test_abort_on_production_is_not_a_merge(tmp_path: Path) -> None:
    assert _check(_repo(tmp_path / "r", "main"), "git merge --abort") == 0


def test_gh_pr_merge_still_needs_base_and_blocks_production(tmp_path: Path) -> None:
    repo = _repo(tmp_path / "r", "feat/x")
    assert _check(repo, "gh pr merge 3 --squash") == 1
    assert _check(repo, "gh pr merge 3 --squash", "--base", "main") == 1
    assert _check(repo, "gh pr merge 3 --squash", "--base", "staging") == 0
    assert _check(repo, "gh pr merge 3 --admin", "--base", "staging") == 1
    assert _check(repo, "git merge origin/main && gh pr merge 3", "--base", "main") == 1


def test_deny_policy_blocks_merge_into_environment_branch(tmp_path: Path) -> None:
    stack = {"git": {"environments": {"staging": "staging"}}, "agent": {"permissions": {"merge": "deny"}}}
    repo = _repo(tmp_path / "r", "staging", stack)
    assert _check(repo, "git merge feat/x", "--user-text", "authorize merge") == 1


def test_linked_worktree_reads_the_main_checkout_stack(tmp_path: Path) -> None:
    main = _repo(tmp_path / "main", "main", {"git": {"environments": {"production": "release"}}})
    tree = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", "-b", "feat/x", str(tree))
    assert not (tree / ".heyeddi").exists()
    assert _check(tree, "gh pr merge 3", "--base", "release") == 1
    assert _check(tree, "git checkout release && git merge feat/x") == 1


@pytest.mark.parametrize("skill", ["heyeddi-pr-respond", "heyeddi-ci-fails"])
def test_manifest_exposes_the_flags(skill: str) -> None:
    manifest = json.loads((ROOT / "skills" / skill / "manifest.json").read_text(encoding="utf-8"))
    tool = next(t for t in manifest["tools"] if t["name"] == "assert_no_merge")
    props = tool["parameters"]["properties"]
    assert {"base", "planned_command", "user_text", "check", "project_root", "check_yaml"} <= set(props)
    assert "production" in tool["description"].lower()


def test_documented_callers_pass_base_and_command() -> None:
    for rel in (
        "heyeddi-pr-respond/SKILL.md",
        "heyeddi-ci-fails/SKILL.md",
        "heyeddi-ci-fails/context/EXAMPLES.md",
    ):
        text = (ROOT / "skills" / rel).read_text(encoding="utf-8")
        calls = [line for line in text.splitlines() if "assert_no_merge --check" in line]
        assert calls, rel
        assert all("--base" in line and "--planned-command" in line for line in calls), rel
