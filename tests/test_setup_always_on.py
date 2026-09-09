"""Always-on heyeddi-setup prefs hard gate: verify_setup + pre-merge wiring."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP_SCRIPTS = ROOT / "skills" / "heyeddi-setup" / "scripts"
PRE_MERGE = ROOT / "skills" / "pre-merge-gate" / "scripts" / "pre_merge_gate.py"


def _write_complete_setup(project: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(SETUP_SCRIPTS / "write_setup.py"),
            "--project-root",
            str(project),
            "--json",
            json.dumps(
                {
                    "git.preset": "main_staging_dev",
                    "git.custom_workflow": None,
                    "git.worktrees": False,
                    "agent.commit": "ask",
                    "agent.push": "ask",
                }
            ),
        ],
        cwd=str(SETUP_SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_setup_skill_declares_always_on() -> None:
    body = (ROOT / "skills" / "heyeddi-setup" / "SKILL.md").read_text(encoding="utf-8")
    assert "ALWAYS-ON" in body or "Always on" in body
    assert "verify_setup" in body
    assert "Hard gate" in body or "hard gate" in body
    assert (ROOT / "skills" / "heyeddi-setup" / "reference" / "setup-always-on.md").is_file()


def test_always_on_docs_mention_setup_hard() -> None:
    hub = (ROOT / "docs" / "always-on-skills.md").read_text(encoding="utf-8")
    assert "@heyeddi-setup" in hub
    assert "verify_setup" in hub
    assert "fail" in hub.lower()
    orch = (
        ROOT / "skills" / "heyeddi-orchestrator" / "reference" / "always-on.md"
    ).read_text(encoding="utf-8")
    assert "verify_setup" in orch
    assert "hard" in orch.lower()


def test_pre_merge_includes_setup_audit(tmp_path: Path) -> None:
    _write_complete_setup(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            str(PRE_MERGE),
            "--project-root",
            str(tmp_path),
            "--skip-backend",
            "--skip-duplicate-ui",
            "--skip-prose-audit",
            "--skip-visual-audit",
            "--skip-engineering-audit",
        ],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "setup-audit" in out
    assert "| setup-audit | PASS |" in out or "| setup-audit | SKIP |" in out
    if "| setup-audit | PASS |" in out:
        assert proc.returncode == 0


def test_pre_merge_setup_fails_when_incomplete(tmp_path: Path) -> None:
    heyeddi = tmp_path / ".heyeddi"
    heyeddi.mkdir()
    (heyeddi / "stack.json").write_text(
        json.dumps({"frontend": "vue"}) + "\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(PRE_MERGE),
            "--project-root",
            str(tmp_path),
            "--skip-backend",
            "--skip-duplicate-ui",
            "--skip-prose-audit",
            "--skip-visual-audit",
            "--skip-engineering-audit",
        ],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| setup-audit | FAIL |" in out
    assert proc.returncode != 0


def test_pre_merge_skip_setup_flag(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(PRE_MERGE),
            "--project-root",
            str(tmp_path),
            "--skip-backend",
            "--skip-duplicate-ui",
            "--skip-prose-audit",
            "--skip-visual-audit",
            "--skip-engineering-audit",
            "--skip-setup-audit",
        ],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| setup-audit | SKIP |" in out
    assert proc.returncode == 0


def test_bookends_mention_setup_gate() -> None:
    for skill_name in (
        "heyeddi-orchestrator",
        "project-engineering",
        "flutter-engineering",
        "heyeddi-pr-respond",
        "pre-merge-gate",
    ):
        body = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert "verify_setup" in body or "heyeddi-setup" in body or "setup-audit" in body, skill_name
