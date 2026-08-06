"""Skills hub update check: detect and ask, never auto-install."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "heyeddi-orchestrator" / "scripts"


def _run(*extra: str, project: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_skills_update.py"), *extra, "--project-root", str(project)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def test_update_available_asks_user(tmp_path: Path) -> None:
    data = _run("--latest", "99.0.0", "--force", project=tmp_path)
    assert data["update_available"] is True
    assert data["ask_user"] is True
    assert data["never_auto_update"] is True
    assert "user_block" in data
    assert "npx skills add" in data["user_block"]
    assert "Approve update" in data["user_block"]


def test_up_to_date(tmp_path: Path) -> None:
    data = _run("--latest", "0.0.1", "--force", project=tmp_path)
    assert data["update_available"] is False
    assert data["ask_user"] is False
    assert data["status"] == "up_to_date"


def test_kill_switch_disable(tmp_path: Path) -> None:
    disabled = _run("--disable", project=tmp_path)
    assert disabled["status"] == "disabled"
    state = json.loads((tmp_path / ".heyeddi" / "sync-state.json").read_text(encoding="utf-8"))
    assert state["skills_update_check"] is False

    skipped = _run("--latest", "99.0.0", "--force", project=tmp_path)
    assert skipped["status"] == "skipped"
    assert skipped["ask_user"] is False


def test_dismiss_stops_nag(tmp_path: Path) -> None:
    first = _run("--latest", "99.0.0", "--force", project=tmp_path)
    assert first["ask_user"] is True
    dismissed = _run("--dismiss", "--latest", "99.0.0", project=tmp_path)
    assert dismissed["status"] == "dismissed"
    again = _run("--latest", "99.0.0", "--force", project=tmp_path)
    assert again["ask_user"] is False
    assert again["status"] == "dismissed"


def test_throttle(tmp_path: Path) -> None:
    _run("--latest", "99.0.0", "--force", project=tmp_path)
    throttled = _run("--latest", "99.0.0", project=tmp_path)
    assert throttled["status"] == "throttled"
    assert throttled["ask_user"] is False


def test_semver_helpers() -> None:
    sys.modules.pop("_skills_update", None)
    if str(SCRIPTS) in sys.path:
        sys.path.remove(str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS))
    from _skills_update import parse_semver, version_lt  # noqa: E402

    assert parse_semver("v3.0.6") == (3, 0, 6)
    assert version_lt("3.0.5", "3.0.6")
    assert not version_lt("3.0.6", "3.0.6")
