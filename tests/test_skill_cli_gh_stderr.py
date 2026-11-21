"""gh 2.105+ prints an "event listen" hint on stderr after `gh pr ...` commands.

Scripts parse `run_command` output as JSON or a SHA, so a successful gh call must
return stdout only. A failing gh call keeps stderr so the error stays visible.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from _skill_loader import load_skill_script

GH_SKILLS = ["heyeddi-pr-review", "heyeddi-pr-respond", "heyeddi-ci-fails", "pre-merge-gate"]

HINT = (
    "hint: if you need to wait for this pull request to be reviewed, merged, or closed "
    "before continuing, use this instead of polling:\n"
    "    gh event listen --resource https://github.com/o/r/pull/1 --event x\n"
)


@pytest.fixture
def fake_gh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'if [ "$1" = fail ]; then echo "GraphQL: Could not resolve" >&2; exit 1; fi\n'
        "echo '{\"number\":1}'\n"
        f"printf '%s' {json.dumps(HINT)} >&2\n"
    )
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return gh


@pytest.mark.parametrize("skill", GH_SKILLS)
def test_gh_success_returns_stdout_only(skill: str, fake_gh: Path, tmp_path: Path) -> None:
    cli = load_skill_script(skill, "_skill_cli")
    out = cli.run_command(["gh", "pr", "view", "1", "--json", "number"], tmp_path)
    assert json.loads(out) == {"number": 1}


@pytest.mark.parametrize("skill", GH_SKILLS)
def test_gh_failure_keeps_stderr(skill: str, fake_gh: Path, tmp_path: Path) -> None:
    cli = load_skill_script(skill, "_skill_cli")
    out = cli.run_command(["gh", "fail"], tmp_path)
    assert out.startswith("[exit 1]")
    assert "Could not resolve" in out


def test_pre_merge_gate_runner_drops_gh_hint(fake_gh: Path, tmp_path: Path) -> None:
    gate = load_skill_script("pre-merge-gate", "pre_merge_gate")
    out = gate.run_command(["gh", "pr", "view", "--json", "number"], tmp_path)
    assert json.loads(out) == {"number": 1}
