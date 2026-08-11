"""Smoke tests for HeyEddi CI skill scripts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESPOND = ROOT / "skills" / "heyeddi-pr-respond" / "scripts"
FAILS = ROOT / "skills" / "heyeddi-ci-fails" / "scripts"
RUNNERS = ROOT / "skills" / "heyeddi-ci-runners" / "scripts"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_filter_heyeddi_comments(tmp_path: Path) -> None:
    import tempfile

    src = tmp_path / "comments-in.json"
    src.write_text(
        json.dumps(
            {
                "pr": 9,
                "inline": [
                    {
                        "id": 1,
                        "body": "<!-- heyeddi-ci-review --> finding about auth",
                        "user": {"login": "heyeddi-ci[bot]"},
                    },
                    {
                        "id": 2,
                        "body": "please fix typo",
                        "user": {"login": "human-reviewer"},
                    },
                ],
                "discussion": [],
                "reviews": [],
            }
        ),
        encoding="utf-8",
    )
    out = Path(tempfile.gettempdir()) / "heyeddi-test-pr-9-filter.json"
    proc = _run(
        RESPOND / "filter_comments.py",
        "--pr",
        "9",
        "--project-root",
        str(tmp_path),
        "--input",
        str(src),
        "--output",
        str(out),
        "--scope",
        "heyeddi",
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["inline"]) == 1
    assert data["inline"][0]["id"] == 1
    assert not (tmp_path / ".heyeddi" / "docs" / "pr-9-ci-comments.json").exists()


def test_assert_no_merge_default() -> None:
    proc = _run(RESPOND / "assert_no_merge.py")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(proc.stdout)
    assert data["authorized"] is False
    assert data["merge_allowed"] is False


def test_assert_no_merge_rejects_auto_merge_yaml(tmp_path: Path) -> None:
    (tmp_path / "eddi-ci.yaml").write_text("version: '1.0'\nauto_merge: true\n", encoding="utf-8")
    proc = _run(
        RESPOND / "assert_no_merge.py",
        "--project-root",
        str(tmp_path),
        "--check-yaml",
    )
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["issues"]


def test_assert_no_merge_blocks_unauthorized_gh_merge() -> None:
    proc = _run(
        RESPOND / "assert_no_merge.py",
        "--planned-command",
        "gh pr merge 12 --squash",
        "--check",
    )
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["allow"] is False


def test_assert_runners_placeholder() -> None:
    proc = _run(RUNNERS / "assert_runners_placeholder.py")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(proc.stdout)
    assert data["execution_available"] is False
    assert data["placeholder"] is True


def test_assert_runners_blocks_false_claim() -> None:
    proc = _run(
        RUNNERS / "assert_runners_placeholder.py",
        "--agent-text",
        "The Spot job succeeded on your PR.",
        "--check",
    )
    assert proc.returncode == 1


def test_discover_and_verify_empty_repo(tmp_path: Path) -> None:
    proc = _run(
        RESPOND / "discover_and_verify.py",
        "--project-root",
        str(tmp_path),
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(proc.stdout)
    assert data.get("commands") == [] or data.get("status") in {"ok", "SKIP", "DRY_RUN"} or "commands" in data


def test_write_ci_fails_report(tmp_path: Path) -> None:
    docs = tmp_path / ".heyeddi" / "docs"
    docs.mkdir(parents=True)
    (docs / "pr-3-ci-fails.json").write_text(
        json.dumps(
            {
                "pr": 3,
                "head_sha": "abc",
                "head_ref": "feat/x",
                "url": "https://example.com/pr/3",
                "failing_checks": [{"name": "test", "conclusion": "FAILURE", "detailsUrl": "u"}],
            }
        ),
        encoding="utf-8",
    )
    proc = _run(
        FAILS / "write_ci_fails_report.py",
        "--pr",
        "3",
        "--project-root",
        str(tmp_path),
        "--force",
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    md = (docs / "pr-3-ci-fails.md").read_text(encoding="utf-8")
    assert "Ephemeral" in md or "ephemeral" in md.lower() or "authorize merge" in md.lower()
