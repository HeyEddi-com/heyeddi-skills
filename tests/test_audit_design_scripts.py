"""Skill scripts that failed finished work, or passed work they never checked."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from _skill_loader import REPO, load_skill_script

SKILLS = REPO / "skills"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(skill: str, script: str, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SKILLS / skill / "scripts" / f"{script}.py"), *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def _intake_project(root: Path) -> None:
    """A product with a login page and no settings page."""
    intake = root / ".heyeddi" / "docs" / "intake"
    _write(intake / "skill-routing.json", json.dumps({"routes": [{"route": "/login", "skill": "heyeddi-design"}]}))
    _write(intake / "product-translation.json", json.dumps({"pages": [{"route": "/login"}]}))


def test_intake_needs_no_settings_page(tmp_path: Path) -> None:
    _intake_project(tmp_path)
    out = _run("heyeddi-intake", "verify_intake", "--project-root", str(tmp_path)).stdout
    assert "settings" not in out


def test_intake_checks_artifacts_for_handoff_routes(tmp_path: Path) -> None:
    intake = tmp_path / ".heyeddi" / "docs" / "intake"
    _write(
        intake / "skill-routing.json",
        json.dumps({"routes": [{"route": "/login", "skill": "heyeddi-handoff", "feature": "login"}]}),
    )
    data = json.loads(_run("heyeddi-intake", "verify_intake", "--project-root", str(tmp_path)).stdout)
    assert any(issue.startswith("login-handoff-visual") for issue in data["issues"])


def test_intake_allows_views_already_committed(tmp_path: Path) -> None:
    vi = load_skill_script("heyeddi-intake", "verify_intake")
    git = ["git", "-C", str(tmp_path), "-c", "user.email=t@example.com", "-c", "user.name=t"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    _write(tmp_path / "src" / "views" / "Old.vue", "<template/>")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "base", "--no-gpg-sign"], check=True)
    assert vi._disallowed_vue(tmp_path) == []
    _write(tmp_path / "src" / "views" / "New.vue", "<template/>")
    assert vi._disallowed_vue(tmp_path) == ["src/views/New.vue"]


def test_routing_feature_matches_route_slug() -> None:
    br = load_skill_script("heyeddi-intake", "build_routing")
    for route, slug in (("/", "home"), ("/login", "login"), ("/dashboard", "dashboard"), ("/a/settings", "a-settings")):
        assert br.feature_slug(route, "View") == slug


def test_seed_brief_for_dashboard_is_not_a_settings_screen(tmp_path: Path) -> None:
    _write(
        tmp_path / ".heyeddi" / "designs" / "dashboard" / "wireframe.md",
        "# Wireframe\n\n## Regions (required)\n| Region | Desktop | Mobile | Suggested component |\n"
        "|---|---|---|---|\n| Data surface | Roster table | Scroll | DataTable |\n",
    )
    _run("heyeddi-intake", "seed_brief", "--project-root", str(tmp_path), "--feature", "dashboard")
    brief = (tmp_path / ".heyeddi" / "designs" / "dashboard" / "mockup-brief.md").read_text(encoding="utf-8")
    assert "Data surface" in brief and "DataTable" in brief
    assert "## Implementation spec" in brief
    for wrong in ("Profile card", "Notifications", "SettingsView", "AppSidebar"):
        assert wrong not in brief


LOGIN_BRIEF = """# Mockup brief: Login

## Region map
| Region | What the user sees | Build |
|---|---|---|
| Auth card | Email, password, button | Card |

## Implementation spec

| Component / region | Token or CSS rule | File(s) |
|---|---|---|
| Card gap | `gap: var(--size-4)` | `src/views/LoginView.vue` |

Notes: no sidebar. The account settings link is a later route. """ + "Centered card. " * 10


def test_handoff_passes_a_route_without_a_sidebar(tmp_path: Path) -> None:
    _write(tmp_path / ".heyeddi" / "designs" / "login" / "mockup-brief.md", LOGIN_BRIEF.replace("sidebar", "rail"))
    _write(tmp_path / "src" / "views" / "LoginView.vue", "<style>.a{gap: var(--size-4)}</style>")
    proc = _run("heyeddi-handoff", "verify_handoff", "--route", "/login", "--project-root", str(tmp_path), "--check")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_handoff_still_checks_shell_files_the_spec_names(tmp_path: Path) -> None:
    brief = LOGIN_BRIEF + "\n| Sidebar | `margin-top: auto` | `src/components/layout/AppSidebar.vue` |\n"
    _write(tmp_path / ".heyeddi" / "designs" / "login" / "mockup-brief.md", brief)
    proc = _run("heyeddi-handoff", "verify_handoff", "--route", "/login", "--project-root", str(tmp_path))
    assert "Sidebar flex column + user pinned" in json.loads(proc.stdout)["failed"]


def test_handoff_without_a_spec_does_not_pass(tmp_path: Path) -> None:
    proc = _run("heyeddi-handoff", "verify_handoff", "--route", "/login", "--project-root", str(tmp_path))
    assert json.loads(proc.stdout)["ok"] is False


def test_brief_check_does_not_require_the_word_sidebar(tmp_path: Path) -> None:
    _write(tmp_path / ".heyeddi" / "designs" / "login" / "mockup-brief.md", LOGIN_BRIEF.replace("sidebar", "rail"))
    proc = _run("heyeddi-handoff", "describe_handoff", "--route", "/login", "--project-root", str(tmp_path), "--check")
    assert proc.returncode == 0, proc.stderr


def test_placeholder_attribute_is_not_a_placeholder_view(tmp_path: Path) -> None:
    scan = load_skill_script("heyeddi-product", "_product_scan")
    body = "\n".join(f"  <p>Row {i}</p>" for i in range(12))
    real = _write(
        tmp_path / "Login.vue",
        f'<template>\n  <InputText v-if="a > 0" placeholder="Email" :placeholder="hint" />\n{body}\n</template>\n'
        "<style>input::placeholder { color: red }</style>\n",
    )
    assert scan.view_placeholder_flags(real) == []
    stub = _write(tmp_path / "Stub.vue", f"<template>\n  <p>Placeholder page</p>\n{body}\n</template>\n")
    assert scan.view_placeholder_flags(stub) == ["placeholder:placeholder"]
    todo = _write(tmp_path / "Todo.vue", f"<template>\n  <!-- TODO: wire -->\n{body}\n</template>\n")
    assert scan.view_placeholder_flags(todo) == ["placeholder:todo:"]


def test_check_features_states_actions_not_questions() -> None:
    cf = load_skill_script("heyeddi-product", "check_features")
    text = " ".join(
        cf._pm_questions([{"route": "/a", "status": "missing"}, {"route": "/b", "status": "placeholder"}], [])
    )
    assert "Build `/a`" in text and "Finish `/b`" in text
    assert "?" not in text


def _fake_playwright(root: Path, sync_api: str) -> dict:
    _write(root / "fake" / "playwright" / "__init__.py", "")
    _write(root / "fake" / "playwright" / "sync_api.py", sync_api)
    return {"PYTHONPATH": str(root / "fake")}


def test_capture_and_contrast_fail_without_playwright(tmp_path: Path) -> None:
    env = _fake_playwright(tmp_path, "raise ImportError('gone')\n")
    for script in ("audit_ui", "audit_contrast"):
        proc = _run("visual-auditor", script, "--route", "/", "--project-root", str(tmp_path), env=env)
        assert proc.returncode != 0, script
        assert "Playwright" in proc.stderr


def test_capture_fails_when_the_server_is_down(tmp_path: Path) -> None:
    env = _fake_playwright(
        tmp_path,
        "class P:\n"
        "    def __getattr__(self, name):\n"
        "        if name == 'goto':\n"
        "            def boom(*a, **k):\n"
        "                raise RuntimeError('refused')\n"
        "            return boom\n"
        "        return lambda *a, **k: P()\n"
        "    @property\n"
        "    def chromium(self):\n"
        "        return P()\n"
        "    def __enter__(self):\n"
        "        return self\n"
        "    def __exit__(self, *a):\n"
        "        return False\n"
        "def sync_playwright():\n"
        "    return P()\n",
    )
    proc = _run("visual-auditor", "audit_ui", "--route", "/", "--project-root", str(tmp_path), env=env)
    assert proc.returncode != 0
    assert "dev server" in proc.stderr


def test_finalize_ticks_the_box_only_when_contrast_passes(tmp_path: Path) -> None:
    visual = tmp_path / ".heyeddi" / "audits" / "visual"
    for errors, mark in ((0, "[x]"), (2, "[ ]")):
        _write(visual / f"home-contrast-{date.today()}.json", json.dumps({"results": [{"errorCount": errors}]}))
        review = _write(visual / "reviews" / f"home-review-{date.today()}.md", "# Review\n")
        _run("visual-auditor", "finalize_visual_review", "--route", "/", "--project-root", str(tmp_path), "--skip-recapture")
        assert f"- {mark} `audit_contrast --check`" in review.read_text(encoding="utf-8")


def test_flutter_screen_without_cards_passes_when_brief_has_none(tmp_path: Path) -> None:
    vh = load_skill_script("design-handoff-flutter", "verify_handoff")
    names = [check[0] for check in vh.route_screen_checks(tmp_path, "/login", "## Implementation spec\nTextField")]
    assert names == ["/login screen exists"]
    names = [check[0] for check in vh.route_screen_checks(tmp_path, "/login", "Card( with EdgeInsets")]
    assert names == ["/login screen exists", "/login uses Card", "/login card padding"]
