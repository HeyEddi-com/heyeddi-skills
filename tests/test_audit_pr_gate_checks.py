"""Pre-merge gate: approved cost, generated files, project runner, visual and CI checks."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from _skill_loader import load_skill_script

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _gate():
    return load_skill_script("pre-merge-gate", "pre_merge_gate")


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
        cwd=root, env=ENV, check=True, capture_output=True,
    )


def _write(root: Path, rel: str, text: str = "x\n") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _clean_status(root: Path) -> tuple[str, str]:
    rows: list = []
    _gate().run_git_clean_checks(root, rows)
    return {name: (st, note) for name, st, note in rows}["git-clean"]


BLOCK = "<!-- heyeddi-always-on:start -->\n{}\n<!-- heyeddi-always-on:end -->\n"


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _write(tmp_path, "AGENTS.md", "# Agent instructions\n\nMine.\n\n" + BLOCK.format("old"))
    _write(tmp_path, "src/app.py")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def test_generated_files_do_not_dirty_the_tree(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    for rel in (
        ".heyeddi/docs/engineering-audit-2026-01-01.md",
        ".heyeddi/docs/cost-estimate-2026-01-01.md",
        ".heyeddi/audits/visual/home-contrast-2026-01-01.json",
        ".heyeddi/skills-index.json",
        ".heyeddi/skills-index.md",
        ".cursor/rules/heyeddi-always-on.mdc",
    ):
        _write(root, rel)
    _write(root, "AGENTS.md", "# Agent instructions\n\nMine.\n\n" + BLOCK.format("new"))
    assert _clean_status(root)[0] == "PASS"


@pytest.mark.parametrize(
    ("rel", "text"),
    [
        ("src/app.py", "changed\n"),
        ("new.py", "x\n"),
        (".heyeddi/audits/visual/home-review.md", "x\n"),
        (".heyeddi/docs/engineering/decisions.md", "x\n"),
        ("AGENTS.md", "# Agent instructions\n\nEdited by hand.\n\n" + BLOCK.format("old")),
    ],
)
def test_real_changes_still_fail(tmp_path: Path, rel: str, text: str) -> None:
    root = _repo(tmp_path)
    _write(root, rel, text)
    status, note = _clean_status(root)
    assert status == "FAIL" and rel in note


def _run_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *args: str) -> list[list[str]]:
    gate = _gate()
    calls: list[list[str]] = []

    def fake(root, skill, script, extra):
        calls.append([script, *extra])
        if "estimate_change_cost" in script and "--approved" in extra:
            path = root / ".heyeddi" / "docs" / "engineering" / "decisions.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nApproved by the user: ok to spend\n", encoding="utf-8")
        return '{"ok": true}'

    monkeypatch.setattr(gate, "run_skill_script", fake)
    monkeypatch.setattr(sys, "argv", ["gate", "--project-root", str(tmp_path), "--skip-visual-audit", *args])
    gate.main()
    return [c for c in calls if "estimate_change_cost" in c[0]]


def test_cost_approval_is_passed_through_and_recorded_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    decisions = _write(tmp_path, ".heyeddi/docs/engineering/decisions.md", "# Decisions\n")
    calls = _run_gate(tmp_path, monkeypatch, "--cost-approved", "ok to spend")
    assert calls == [["scripts/estimate_change_cost.py", "--check", "--approved", "ok to spend"]]
    first = decisions.read_text(encoding="utf-8")
    assert "ok to spend" in first
    _run_gate(tmp_path, monkeypatch, "--cost-approved", "ok to spend")
    assert decisions.read_text(encoding="utf-8") == first


def test_cost_is_not_approved_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run_gate(tmp_path, monkeypatch) == [["scripts/estimate_change_cost.py", "--check"]]


@pytest.mark.parametrize(
    ("files", "prefix"),
    [
        ({"backend/uv.lock": ""}, ["uv", "run"]),
        ({"uv.lock": ""}, ["uv", "run"]),
        ({"backend/poetry.lock": ""}, ["poetry", "run"]),
        ({"backend/pyproject.toml": "[tool.poetry]\nname='a'\n"}, ["poetry", "run"]),
    ],
)
def test_backend_checks_use_the_declared_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, files: dict, prefix: list
) -> None:
    gate = _gate()
    (tmp_path / "backend" / "app").mkdir(parents=True)
    for rel, text in files.items():
        _write(tmp_path, rel, text)
    calls: list[list[str]] = []
    monkeypatch.setattr(gate, "run_command", lambda cmd, cwd, timeout=600: calls.append(cmd) or "ok")
    rows: list = []
    gate.run_backend_checks(tmp_path, rows)
    assert calls[0] == [*prefix, "pytest", "-q", "tests"]
    assert calls[1][:4] == [*prefix, "ruff", "check"]
    assert [st for _, st, _ in rows] == ["PASS", "PASS"]


def test_missing_declared_runner_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    gate = _gate()
    _write(tmp_path, "backend/uv.lock", "")
    monkeypatch.setattr(gate, "run_command", lambda cmd, cwd, timeout=600: "[error] command not found: uv")
    rows: list = []
    gate.run_backend_checks(tmp_path, rows)
    assert [st for _, st, _ in rows] == ["FAIL", "FAIL"]


def _visual(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, output: str = '{"status": "ok"}') -> tuple[list, list]:
    gate = _gate()
    seen: list = []

    def fake(root, skill, script, extra):
        seen.append((extra[1], os.environ.get("DEV_SERVER_URL")))
        return output

    monkeypatch.setattr(gate, "run_skill_script", fake)
    rows: list = []
    gate.run_visual_checks(tmp_path, rows, require=True)
    return rows, seen


def test_visual_skips_without_a_frontend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, ".heyeddi/product.md", "`/api/users`\n")
    rows, seen = _visual(tmp_path, monkeypatch)
    assert seen == [] and rows[0][1] == "SKIP" and "frontend" in rows[0][2]


def test_visual_skips_without_routes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, ".heyeddi/product.md", "No routes yet.\n")
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"vue": "3"}}))
    rows, seen = _visual(tmp_path, monkeypatch)
    assert seen == [] and rows[0][1] == "SKIP" and "routes" in rows[0][2]


def test_visual_starts_and_stops_its_own_dev_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEV_SERVER_URL", raising=False)
    monkeypatch.delenv("FLUTTER_WEB_URL", raising=False)
    _write(tmp_path, ".heyeddi/product.md", "`/settings`\n")
    server = _write(
        tmp_path,
        "server.py",
        "import http.server, sys\n"
        "port = int(sys.argv[sys.argv.index('--port') + 1])\n"
        "open('port.txt', 'w').write(str(port))\n"
        "http.server.HTTPServer(('127.0.0.1', port), http.server.SimpleHTTPRequestHandler).serve_forever()\n",
    )
    _write(
        tmp_path,
        "package.json",
        json.dumps({"scripts": {"dev": f"{sys.executable} {server.name}"}, "dependencies": {"vue": "3"}}),
    )
    rows, seen = _visual(tmp_path, monkeypatch)
    assert [st for _, st, _ in rows] == ["PASS"]
    port = (tmp_path / "port.txt").read_text()
    assert seen == [("/settings", f"http://127.0.0.1:{port}")]
    assert "DEV_SERVER_URL" not in os.environ
    import socket

    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", int(port))) != 0


def test_visual_without_a_way_to_serve_fails_sign_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEV_SERVER_URL", raising=False)
    monkeypatch.delenv("FLUTTER_WEB_URL", raising=False)
    _write(tmp_path, ".heyeddi/product.md", "`/settings`\n")
    _write(tmp_path, "pubspec.yaml", "name: a\n")
    rows, seen = _visual(tmp_path, monkeypatch)
    assert seen == [] and rows[0][1] == "FAIL" and "DEV_SERVER_URL" in rows[0][2]


def test_visual_missing_playwright_fails_sign_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEV_SERVER_URL", "http://127.0.0.1:1")
    _write(tmp_path, ".heyeddi/product.md", "`/settings`\n")
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"vue": "3"}}))
    rows, _ = _visual(tmp_path, monkeypatch, "[skip] Playwright not installed.")
    assert any(st == "FAIL" for _, st, _ in rows)


def _checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, output: str) -> tuple[str, str]:
    gate = _gate()

    def fake(cmd, cwd, timeout=600):
        if cmd[:3] == ["gh", "pr", "checks"]:
            return output
        return "[exit 1] stop here"

    monkeypatch.setattr(gate, "gh_status", lambda root: {"ok": True})
    monkeypatch.setattr(gate, "run_command", fake)
    rows: list = []
    gate.run_pr_checks(tmp_path, 7, rows)
    return {name: (st, note) for name, st, note in rows}["pr-checks"]


NO_CHECKS = "[exit 1]\nno checks reported on the 'feat/x' branch"


def test_no_checks_passes_only_without_ci(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert _checks(tmp_path, monkeypatch, NO_CHECKS)[0] == "PASS"
    _write(tmp_path, ".github/workflows/ci.yml", "on: pull_request\n")
    status, note = _checks(tmp_path, monkeypatch, NO_CHECKS)
    assert status == "FAIL" and "gh pr checks 7 --watch" in note[:120]


@pytest.mark.parametrize(
    "rel_text",
    [(".gitlab-ci.yml", "x"), (".circleci/config.yml", "x"), ("eddi-ci.yaml", "pipeline:\n  t:\n    run: pytest\n")],
)
def test_other_ci_config_keeps_no_checks_failing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, rel_text: tuple) -> None:
    _write(tmp_path, *rel_text)
    assert _checks(tmp_path, monkeypatch, NO_CHECKS)[0] == "FAIL"


def test_pending_checks_say_to_watch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    status, note = _checks(tmp_path, monkeypatch, "[exit 8]\nunit\tpending\t0\turl")
    assert status == "FAIL" and "gh pr checks 7 --watch" in note[:120]


def _pr_check_row(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, output: str) -> tuple[str, str]:
    gate = _gate()
    monkeypatch.setattr(gate, "add_unverified_pr_rows", lambda *_: False)
    monkeypatch.setattr(gate, "run_command", lambda cmd, *a, **k: output if cmd[1:3] == ["pr", "checks"] else "[error] stop")
    rows: list = []
    gate.run_pr_checks(tmp_path, 1, rows)
    return next((st, note) for name, st, note in rows if name == "pr-checks")


def test_a_skipped_review_of_the_latest_commit_is_not_a_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    st, note = _pr_check_row(monkeypatch, tmp_path, "HeyEddi Reviewer\tskipping\t1m\turl\ntests\tpass\t1m\turl\n")
    assert st == "FAIL" and "/heyeddi review" in note


def test_other_skipped_jobs_still_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out = "HeyEddi Reviewer\tpass\t1m\turl\ndeploy\tskipping\t0\turl\n"
    assert _pr_check_row(monkeypatch, tmp_path, out)[0] == "PASS"
