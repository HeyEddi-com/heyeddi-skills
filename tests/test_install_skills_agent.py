"""install-skills.sh passes --agent through to the skills CLI (default: cursor)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install-skills.sh"


def _run(tmp_path: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / "npx.log"
    fake = bin_dir / "npx"
    fake.write_text(f'#!/usr/bin/env bash\necho "$@" >> "{log}"\n', encoding="utf-8")
    fake.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    proc = subprocess.run(
        [str(SCRIPT), "heyeddi", "--project", str(tmp_path), *args],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    return proc, log.read_text(encoding="utf-8") if log.exists() else ""


def test_default_agent_is_cursor(tmp_path: Path) -> None:
    proc, calls = _run(tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "-a cursor" in calls


def test_agent_flag_targets_claude_code_globally(tmp_path: Path) -> None:
    proc, calls = _run(tmp_path, "--agent", "claude-code", "--global")
    assert proc.returncode == 0, proc.stderr
    assert "-a claude-code" in calls
    assert " -g" in calls
    assert "cursor" not in calls


def test_agent_flag_rejects_bad_name(tmp_path: Path) -> None:
    proc, calls = _run(tmp_path, "--agent", "Claude Code")
    assert proc.returncode != 0
    assert "agent must be lowercase" in proc.stderr
    assert calls == ""
