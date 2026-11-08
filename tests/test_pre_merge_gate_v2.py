"""pre-merge-gate v2: sign-off, emergency skips, Flutter, JSON."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE_MERGE = ROOT / "skills" / "pre-merge-gate" / "scripts" / "pre_merge_gate.py"
ENG_SCRIPTS = ROOT / "skills" / "engineering-excellence" / "scripts"


def _run(project: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PRE_MERGE), "--project-root", str(project), *extra],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )


def _local_skips() -> list[str]:
    return [
        "--skip-backend",
        "--skip-duplicate-ui",
        "--skip-prose-audit",
        "--skip-visual-audit",
        "--skip-engineering-audit",
        "--skip-setup-audit",
    ]


def test_local_emergency_skips_are_skip_not_fail(tmp_path: Path) -> None:
    proc = _run(tmp_path, *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| setup-audit | SKIP |" in out
    assert "| engineering-audit | SKIP |" in out
    assert "signoff-emergency-skips" not in out
    assert proc.returncode == 0


def test_signoff_emergency_skips_fail(tmp_path: Path) -> None:
    proc = _run(tmp_path, "--signoff", "--no-pr", "--skip-git-clean", *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| setup-audit | FAIL |" in out
    assert "| engineering-audit | FAIL |" in out
    assert "| signoff-emergency-skips | FAIL |" in out
    assert "**Sign-off mode:** yes" in out
    assert proc.returncode != 0


def test_pr_flag_implies_signoff_emergency_fail(tmp_path: Path) -> None:
    # --pr enables sign-off even if gh is unavailable for checks
    proc = _run(
        tmp_path,
        "--pr",
        "999999",
        "--skip-git-clean",
        *_local_skips(),
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| signoff-emergency-skips | FAIL |" in out
    assert proc.returncode != 0


def test_flutter_absent_is_skip(tmp_path: Path) -> None:
    proc = _run(tmp_path, *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| dart-analyze | SKIP |" in out
    assert "| flutter-test | SKIP |" in out


def test_flutter_present_without_tooling_fails(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text("name: demo\n", encoding="utf-8")
    proc = _run(tmp_path, *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    # If dart/flutter exist on the machine, analyze may run; otherwise FAIL.
    assert "dart-analyze" in out
    assert "flutter-test" in out
    if "dart/flutter not found" in out:
        assert proc.returncode != 0
        assert "| dart-analyze | FAIL |" in out


def test_json_payload_emitted(tmp_path: Path) -> None:
    proc = _run(tmp_path, "--json", *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "```json" in out
    match = re.search(r"```json\n(\{.*?\})\n```", out, re.DOTALL)
    assert match, out[:500]
    payload = json.loads(match.group(1))
    assert payload["signoff"] is False
    assert payload["pr"] is None
    assert payload["ok"] is True
    assert isinstance(payload["checks"], list)


def test_signoff_report_marks_mode(tmp_path: Path) -> None:
    proc = _run(tmp_path, "--signoff", "--no-pr", "--skip-git-clean", *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "**Sign-off mode:** yes" in out
    assert "**PR:** none (local)" in out


def test_git_clean_treats_empty_status_sentinel_as_pass(tmp_path: Path) -> None:
    """run_command returns '(success, no output)' for empty porcelain — must be clean."""
    sys.path.insert(0, str(PRE_MERGE.parent))
    from pre_merge_gate import run_git_clean_checks  # noqa: PLC0415

    rows: list[tuple[str, str, str]] = []
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "README").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "README"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    run_git_clean_checks(tmp_path, rows)
    clean = [r for r in rows if r[0] == "git-clean"]
    assert clean and clean[0][1] == "PASS", rows


def test_tooling_package_json_skips_test_build(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "hub", "scripts": {"skill-security": "echo ok"}}),
        encoding="utf-8",
    )
    proc = _run(tmp_path, *_local_skips())
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| test | SKIP |" in out
    assert "| build | SKIP |" in out
    assert proc.returncode == 0
