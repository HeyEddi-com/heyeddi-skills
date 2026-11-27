"""Leftovers the audit reports named."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "heyeddi-local-first" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "heyeddi" / "scripts"))

from check_permission import check  # noqa: E402
import worktree_guard  # noqa: E402

STACK = {"git": {"environments": {"production": "main"}, "default_branch": "main"}}


@pytest.mark.parametrize(
    "command",
    ["git push --all origin", "git --git-dir=/x/.git push origin main", "git --work-tree /x push origin main"],
)
def test_pushes_that_can_reach_production_ask(command: str) -> None:
    assert check(command, cwd=None, stack=STACK).decision == "ask"


@pytest.mark.parametrize("command", ["rg --pre ./run.sh x", "git grep -Ovim x", "git grep --open-files-in-pager=sh x"])
def test_guard_does_not_call_program_runners_read_only(command: str) -> None:
    assert not worktree_guard._read_only(command, ROOT, "s")


@pytest.mark.parametrize(
    ("script", "package"),
    [("run_tests.py", {"scripts": {"test": "exit 1"}}), ("ensure_npm.py", {"dependencies": {"x": "file:./missing.tgz"}})],
)
def test_failed_npm_steps_exit_nonzero(tmp_path: Path, script: str, package: dict) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"name": "t", "version": "1.0.0", **package}), encoding="utf-8")
    path = ROOT / "skills" / "project-engineering" / "scripts" / script
    proc = subprocess.run([sys.executable, str(path), "--project-root", str(tmp_path)], capture_output=True, text=True)
    assert proc.returncode == 1, proc.stdout


def test_generator_cannot_undo_audit_fixes() -> None:
    text = (ROOT / "scripts" / "bootstrap-all-skills.py").read_text(encoding="utf-8")
    assert "npm run build 2>&1 || true" not in text
    for name in ("define_pre_merge_gate", "define_pr_review_responder"):
        body = text.split(f"def {name}", 1)[1].split("\ndef ", 1)[0]
        assert "disable=True" not in body, name
    assert not (ROOT / "scripts" / "apply-next-skill-section.py").exists()


def test_generated_reports_are_ignored_by_scaffolded_projects() -> None:
    snippet = (ROOT / "skills/project-engineering/scaffold/gitignore-heyeddi-pr-scratch.snippet").read_text(encoding="utf-8")
    for line in (".heyeddi/docs/engineering-audit-*.md", ".heyeddi/docs/cost-estimate-*.md", ".heyeddi/audits/visual/*-contrast-*"):
        assert line in snippet


def test_prose_check_allows_the_rule_that_lists_the_banned_words() -> None:
    sys.path.insert(0, str(ROOT / "skills" / "heyeddi-design" / "scripts"))
    from verify_prose import scan_text

    rule = '- NEVER ship AI prose slop (em/en dashes, delve/leverage/tapestry, "Certainly!"); follow `context/PROSE_ANTI_SLOP.md`'
    assert scan_text(rule, "a.md") == []
    assert scan_text("We delve into the tapestry.", "a.md")
