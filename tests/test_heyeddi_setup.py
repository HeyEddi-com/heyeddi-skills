"""Tests for heyeddi-setup prefs schema and scripts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "heyeddi-setup" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _stack_schema import (  # noqa: E402
    apply_answers,
    missing_paths,
    stamp_setup,
    validate_value,
)


def _run(script: str, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--project-root", str(cwd), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_missing_paths_on_empty() -> None:
    missing = missing_paths({})
    assert "git.preset" in missing
    assert "git.environments.production" in missing
    assert "agent.commit" in missing
    assert "frontend" not in missing


def test_apply_preset_main_staging_dev() -> None:
    data = apply_answers(
        {},
        {
            "git.preset": "main_staging_dev",
            "git.custom_workflow": None,
            "git.worktrees": False,
            "agent.commit": "ask",
            "agent.push": "ask",
        },
    )
    data = stamp_setup(data)
    assert missing_paths(data) == []
    assert data["git"]["environments"]["production"] == "main"
    assert data["git"]["environments"]["staging"] == "staging"
    assert data["git"]["environments"]["dev"] == "dev"
    assert data["git"]["pr_base"] == "dev"


def test_apply_preset_main_dev() -> None:
    data = apply_answers(
        {},
        {
            "git.preset": "main_dev",
            "git.custom_workflow": None,
            "git.worktrees": True,
            "agent.commit": "auto",
            "agent.push": "ask",
        },
    )
    data = stamp_setup(data)
    assert missing_paths(data) == []
    assert data["git"]["environments"] == {"production": "main", "staging": "dev"}
    assert "dev" not in data["git"]["environments"] or data["git"]["environments"]["staging"] == "dev"


def test_custom_workflow_escape_hatch() -> None:
    data = apply_answers(
        {},
        {
            "git.preset": "main_staging_dev",
            "git.custom_workflow": "gitflow: feature → develop → main",
            "git.worktrees": False,
            "agent.commit": "ask",
            "agent.push": "ask",
        },
    )
    data = stamp_setup(data)
    assert data["git"]["preset"] == "custom"
    assert "gitflow" in data["git"]["custom_workflow"]
    assert missing_paths(data) == []


def test_write_and_verify_scripts(tmp_path: Path) -> None:
    answers = {
        "git.preset": "main_dev",
        "git.custom_workflow": None,
        "git.worktrees": True,
        "agent.commit": "auto",
        "agent.push": "ask",
    }
    wrote = _run("write_setup.py", "--json", json.dumps(answers), cwd=tmp_path)
    assert wrote.returncode == 0, wrote.stderr
    payload = json.loads(wrote.stdout)
    assert payload["complete"] is True

    stack = json.loads((tmp_path / ".heyeddi" / "stack.json").read_text(encoding="utf-8"))
    assert stack["git"]["preset"] == "main_dev"
    assert stack["git"]["environments"]["staging"] == "dev"
    assert stack["git"]["worktrees"] is True

    check = _run("verify_setup.py", "--check", cwd=tmp_path)
    assert check.returncode == 0, check.stderr


def test_setup_version_rejects_bool() -> None:
    assert validate_value("setup.version", True) is not None
    assert validate_value("setup.version", False) is not None
    assert validate_value("setup.version", 1) is None


def test_frontmatter_accepts_crlf(tmp_path: Path) -> None:
    from _auto_sync import _parse_frontmatter  # noqa: PLC0415

    skill = tmp_path / "SKILL.md"
    skill.write_bytes(
        b"---\r\nname: demo\r\nversion: 1.0.0\r\n---\r\n\r\n# Demo\r\n"
    )
    meta = _parse_frontmatter(skill)
    assert meta.get("name") == "demo"
    assert meta.get("version") == "1.0.0"


def test_verify_fails_when_incomplete(tmp_path: Path) -> None:
    heyeddi = tmp_path / ".heyeddi"
    heyeddi.mkdir()
    (heyeddi / "stack.json").write_text(
        json.dumps({"frontend": "vue", "backends": []}) + "\n",
        encoding="utf-8",
    )
    check = _run("verify_setup.py", "--check", cwd=tmp_path)
    assert check.returncode != 0
