"""The smoke test runs tools against a temp copy of fixtures/, never the tracked tree.

Before: every run of scripts/test-skills.py left dated reports and rewritten
workflow files under fixtures/, which then failed assert_fixes_pushed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _fixture_state() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", "fixtures"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_smoke_run_leaves_fixtures_untouched() -> None:
    before = _fixture_state()
    for skill in ("engineering-excellence", "heyeddi"):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "test-skills.py"), skill],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        assert "Fixture missing" not in proc.stderr, proc.stderr
    assert _fixture_state() == before
