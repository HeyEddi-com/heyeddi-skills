"""Where the backlog lives, keeping documents current, and per-repo choices."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "heyeddi-product" / "scripts" / "backlog.py"
SETUP = ROOT / "skills" / "heyeddi-setup" / "scripts"

TABLE = """| Priority | Feature / route | User story | Status | Notes |
|---|---|---|---|---|
| P0 | /login | sign in | planned | |
"""


def _project(tmp_path: Path, stack: dict | None = None) -> Path:
    docs = tmp_path / ".heyeddi" / "docs" / "product"
    docs.mkdir(parents=True)
    (docs / "backlog.md").write_text(TABLE, encoding="utf-8")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    if stack is not None:
        (tmp_path / ".heyeddi" / "stack.json").write_text(json.dumps(stack), encoding="utf-8")
    return tmp_path


def _run(root: Path, *args: str, code: int = 0) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root), *args], capture_output=True, text=True
    )
    assert proc.returncode == code, proc.stdout + proc.stderr
    return json.loads(proc.stdout) if proc.returncode == 0 else {"error": proc.stderr + proc.stdout}


def _table(root: Path) -> str:
    return (root / ".heyeddi" / "docs" / "product" / "backlog.md").read_text(encoding="utf-8")


def test_add_puts_a_new_item_in_the_table(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _run(root, "add", "/billing", "--priority", "P1", "--story", "pay | invoice")
    assert "/billing" in _table(root)
    assert _run(root, "next")["remaining"] == 2


def test_done_needs_the_documents_or_a_reason(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _run(root, "done", "/login", code=1)
    _run(root, "done", "/login", "--docs", "missing.md", code=1)
    assert "planned" in _table(root)
    _run(root, "done", "/login", "--note", "PR", "--docs", "README.md")
    assert "docs: README.md" in _table(root)


def test_done_accepts_a_stated_reason_for_no_doc_change(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _run(root, "done", "/login", "--docs-none", "internal refactor")
    assert "internal refactor" in _table(root)


def test_external_provider_hands_the_operation_to_mcp(tmp_path: Path) -> None:
    root = _project(tmp_path, {"backlog": {"provider": "mcp", "mcp": {"server": "tasks", "project": "app"}}})
    for args, operation in (
        (["next"], "next"),
        (["add", "/x"], "add"),
        (["block", "/login", "--reason", "no key"], "block"),
        (["done", "/login", "--docs", "README.md"], "done"),
    ):
        out = _run(root, *args)
        assert (out["status"], out["operation"], out["server"], out["project"]) == ("external", operation, "tasks", "app")
    assert _table(root) == TABLE
    assert _run(root, "--local", "next")["status"] == "item"


def test_worktree_without_a_backlog_uses_the_main_checkouts(tmp_path: Path) -> None:
    main, tree = tmp_path / "main", tmp_path / "wt"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "init", "-q", str(main)], check=True)
    subprocess.run([*git, "-C", str(main), "commit", "-qm", "r", "--allow-empty"], check=True)
    subprocess.run([*git, "-C", str(main), "worktree", "add", "-q", str(tree)], check=True)
    _project(main)
    assert _run(tree, "next")["item"]["feature"] == "/login"


def test_setup_records_the_choices_per_repository(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    proc = subprocess.run(
        [sys.executable, str(SETUP / "write_setup.py"), "--project-root", str(tmp_path), "--defaults"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    stack = json.loads((tmp_path / ".heyeddi" / "stack.json").read_text(encoding="utf-8"))
    assert stack["backlog"] == {"provider": "local"}
    assert "README.md" in stack["docs"]["keep"]
    assert stack["docs"]["provider"] == "repo"


def test_choices_are_validated() -> None:
    sys.path.insert(0, str(SETUP))
    from _stack_schema import validate_value

    assert validate_value("backlog.provider", "mcp") is None
    assert validate_value("backlog.provider", "jira") is not None
    assert validate_value("docs.keep", ["README.md"]) is None
    assert validate_value("docs.keep", "README.md") is not None


def test_documents_can_live_somewhere_else(tmp_path: Path) -> None:
    root = _project(tmp_path, {"docs": {"provider": "mcp", "mcp": {"server": "wiki", "space": "app"}}})
    _run(root, "done", "/login", "--docs", "Login page spec")
    assert "docs: Login page spec" in _table(root)


def test_a_link_counts_as_a_document_in_any_setup(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _run(root, "done", "/login", "--docs", "https://docs.example.com/login")


def test_docs_location_choices_are_validated() -> None:
    sys.path.insert(0, str(SETUP))
    from _stack_schema import validate_value

    for value in ("repo", "mcp", "external"):
        assert validate_value("docs.provider", value) is None
    assert validate_value("docs.provider", "notion") is not None
    assert validate_value("docs.location", "https://example.com/wiki") is None
