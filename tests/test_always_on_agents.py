"""Thin always-on AGENTS.md + Cursor alwaysApply rule install."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "heyeddi" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _always_on_agents import END, START, ensure_always_on_agents  # noqa: E402
from _auto_sync import ensure_heyeddi  # noqa: E402


def test_ensure_writes_agents_and_rule(tmp_path: Path) -> None:
    out = ensure_always_on_agents(tmp_path)
    assert out["ok"] is True
    assert "AGENTS.md" in out["written"]
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert START in agents and END in agents
    assert "@pre-merge-gate --signoff" in agents
    assert "Tests (this project)" in agents
    assert "would have failed" in agents
    assert "Playwright" in agents
    assert "legacy-scan" in agents
    assert "browser-platform.md" in agents
    assert "local" in agents
    assert "production" in agents
    assert "No destructive action" in agents
    rule = (tmp_path / ".cursor" / "rules" / "heyeddi-always-on.mdc").read_text(encoding="utf-8")
    assert "alwaysApply: true" in rule
    assert "HeyEddi always-on" in rule
    assert "Tests (this project)" in rule


def test_ensure_preserves_user_agents_content(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Mine\n\nDo not delete.\n", encoding="utf-8")
    ensure_always_on_agents(tmp_path)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert text.startswith("# Mine")
    assert "Do not delete." in text
    assert START in text


def test_ensure_updates_managed_block_only(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        f"# Mine\n\n{START}\nSTALE_MARKER_BODY\n{END}\n\n# After\n",
        encoding="utf-8",
    )
    ensure_always_on_agents(tmp_path)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "# Mine" in text
    assert "# After" in text
    assert "STALE_MARKER_BODY" not in text
    assert "@heyeddi-setup" in text


def test_auto_sync_installs_always_on(tmp_path: Path) -> None:
    result = ensure_heyeddi(tmp_path, once_per_process=False)
    assert result is not None
    assert result.get("always_on_agents", {}).get("ok") is True
    assert (tmp_path / "AGENTS.md").is_file()


def test_ensure_cli_check(tmp_path: Path) -> None:
    script = SCRIPTS / "ensure_always_on_agents.py"
    missing = subprocess.run(
        [sys.executable, str(script), "--project-root", str(tmp_path), "--check"],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert missing.returncode != 0
    ensure_always_on_agents(tmp_path)
    ok = subprocess.run(
        [sys.executable, str(script), "--project-root", str(tmp_path), "--check"],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert ok.returncode == 0
    payload = json.loads(ok.stdout)
    assert payload["ok"] is True
