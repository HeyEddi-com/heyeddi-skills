"""ci-fails: pending is not green, scratch stays out of the tree, tests use the project runner."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from _skill_loader import load_skill_script

ROOT = Path(__file__).resolve().parents[1]
FAILS = ROOT / "skills" / "heyeddi-ci-fails" / "scripts"


def test_pending_checks_are_reported() -> None:
    mod = load_skill_script("heyeddi-ci-fails", "fetch_failing_checks")
    failing, pending = mod.classify_rollup(
        [
            {"name": "ok", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "bad", "status": "COMPLETED", "conclusion": "FAILURE"},
            {"name": "boot", "status": "COMPLETED", "conclusion": "STARTUP_FAILURE"},
            {"name": "running", "status": "IN_PROGRESS", "conclusion": ""},
            {"name": "queued", "status": "QUEUED"},
            {"context": "legacy", "state": "PENDING"},
            {"context": "legacy-ok", "state": "SUCCESS"},
        ]
    )
    assert [item["name"] for item in failing] == ["bad", "boot"]
    assert pending == ["running", "queued", "legacy"]


def test_scratch_files_stay_outside_the_project(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        json.dumps({"pr": 4, "head_sha": "abc", "failing": [{"name": "unit", "state": "FAILURE"}]}),
        encoding="utf-8",
    )

    def run(script: str, *extra: str) -> dict:
        proc = subprocess.run(
            [sys.executable, str(FAILS / script), "--pr", "4", "--project-root", str(tmp_path), *extra],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
        return json.loads(proc.stdout[proc.stdout.index("{"):])

    raw = Path(run("fetch_failing_checks.py", "--fixture", str(fixture))["path"])
    report = Path(run("write_ci_fails_report.py", "--force")["path"])
    for path in (raw, report):
        assert path.is_absolute() and path.is_file()
        assert tmp_path not in path.parents
    assert "### unit" in report.read_text(encoding="utf-8")
    assert not list((tmp_path / ".heyeddi").rglob("pr-4-*"))


@pytest.mark.parametrize("skill", ["heyeddi-ci-fails", "heyeddi-pr-respond"])
@pytest.mark.parametrize(
    ("lock", "expected"),
    [
        ("uv.lock", [["uv", "run", "pytest"]]),
        ("poetry.lock", [["poetry", "install", "--no-interaction"], ["poetry", "run", "pytest"]]),
    ],
)
def test_pytest_runs_through_the_project_runner(tmp_path: Path, skill: str, lock: str, expected: list) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    (tmp_path / lock).write_text("", encoding="utf-8")
    commands = load_skill_script(skill, "discover_and_verify").discover(tmp_path)
    assert [c["argv"] for c in commands if c["kind"] == "pytest"] == expected
