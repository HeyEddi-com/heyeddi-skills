"""backlog.py: the agent asks the script for the next item instead of ending the run."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills" / "heyeddi-product" / "scripts" / "backlog.py"

BACKLOG = """# Product backlog

| Priority | Feature / route | User story (summary) | Status | Notes |
|----------|-----------------|----------------------|--------|-------|
| P1 | /settings | Save profile \\| prefs | planned | |
| P0 | /login | Sign in | done | PR 1 |
| P0 | /dashboard | See roster | planned | |
| P0 | /billing | Pay | blocked | needs Stripe key |

## Out of scope (v1)

- SSO
"""


def _seed(root: Path, text: str = BACKLOG) -> Path:
    path = root / ".heyeddi" / "docs" / "product" / "backlog.md"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(root: Path, *args: str) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    return proc.returncode, data, proc.stderr


def test_next_returns_highest_priority_open_item(tmp_path: Path) -> None:
    _seed(tmp_path)
    code, data, _ = _run(tmp_path, "next")
    assert code == 0
    assert data["status"] == "item"
    assert data["item"]["feature"] == "/dashboard"
    assert data["remaining"] == 2
    assert [row["feature"] for row in data["blocked"]] == ["/billing"]


def test_done_marks_one_row_and_next_moves_on(tmp_path: Path) -> None:
    path = _seed(tmp_path)
    code, _, _ = _run(tmp_path, "done", "/dashboard", "--note", "PR 2")
    assert code == 0
    text = path.read_text(encoding="utf-8")
    assert "| P0 | /dashboard | See roster | done | PR 2 |" in text
    assert "Save profile \\| prefs | planned" in text
    assert "- SSO" in text
    _, data, _ = _run(tmp_path, "next")
    assert data["item"]["feature"] == "/settings"
    assert data["item"]["story"] == "Save profile | prefs"


def test_loop_ends_only_when_nothing_doable_is_left(tmp_path: Path) -> None:
    _seed(tmp_path)
    _run(tmp_path, "done", "/dashboard")
    _run(tmp_path, "done", "/settings")
    code, data, _ = _run(tmp_path, "next")
    assert code == 0
    assert data["status"] == "none"
    assert data["item"] is None


def test_block_requires_a_reason(tmp_path: Path) -> None:
    path = _seed(tmp_path)
    code, _, _ = _run(tmp_path, "block", "/dashboard")
    assert code != 0
    code, _, _ = _run(tmp_path, "block", "/dashboard", "--reason", "no API login")
    assert code == 0
    assert "| /dashboard | See roster | blocked | no API login |" in path.read_text(encoding="utf-8")


def test_unknown_item_fails_without_writing(tmp_path: Path) -> None:
    path = _seed(tmp_path)
    code, _, err = _run(tmp_path, "done", "/nope")
    assert code != 0
    assert "/dashboard" in err
    assert path.read_text(encoding="utf-8") == BACKLOG


def test_stub_backlog_is_not_an_empty_backlog(tmp_path: Path) -> None:
    init = SCRIPT.parent / "init_product_docs.py"
    subprocess.run([sys.executable, str(init), "--project-root", str(tmp_path)], check=True, capture_output=True)
    _, data, _ = _run(tmp_path, "next")
    assert data["status"] == "unfilled"


def test_missing_backlog_is_reported(tmp_path: Path) -> None:
    code, data, _ = _run(tmp_path, "next")
    assert code == 0
    assert data["status"] == "no_backlog"


def test_manifest_lists_the_script() -> None:
    manifest = json.loads((SCRIPT.parent.parent / "manifest.json").read_text(encoding="utf-8"))
    assert "scripts/backlog.py" in [tool["script"] for tool in manifest["tools"]]
