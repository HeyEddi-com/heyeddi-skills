"""Scaffold scripts: Vue stack, FastAPI CORS and extras, stack.json, Flutter on existing apps."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
PE = SKILLS / "project-engineering"
FE = SKILLS / "flutter-engineering"


def _run(script: Path, root: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _fake_tool(bin_dir: Path, name: str, exit_code: int = 0) -> Path:
    """A stand-in executable that records its argv."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    log = bin_dir / f"{name}.log"
    tool = bin_dir / name
    tool.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\nexit {exit_code}\n')
    tool.chmod(0o755)
    return log


def _env_with(bin_dir: Path) -> dict:
    return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"}


def test_vue_scaffold_follows_the_design_system(tmp_path: Path) -> None:
    assert _run(PE / "scripts" / "scaffold_vue.py", tmp_path).returncode == 0
    pkg = json.loads((tmp_path / "package.json").read_text())
    deps = {**pkg["dependencies"], **pkg["devDependencies"]}
    for name in (
        "quasar",
        "@quasar/extras",
        "@quasar/vite-plugin",
        "@vueuse/motion",
        "sass-embedded",
        "primevue",
        "primeicons",
        "@primeuix/themes",
    ):
        assert name in deps, name
    assert "open-props" not in deps
    main = (tmp_path / "src" / "main.ts").read_text()
    assert '".dark-mode"' in main
    assert "directives: { Morph }" in main
    assert "quasar/src/css/index.sass" in main
    assert "quasar(" in (tmp_path / "vite.config.ts").read_text()
    tokens = (tmp_path / "src" / "styles" / "tokens.css").read_text()
    assert "open-props" not in tokens
    for var in ("--app-bg", "--app-text-main", "--surface-1", "--text-1", "--size-3", "--q-primary"):
        assert f"{var}:" in tokens, var
    assert "OpenProps" not in (tmp_path / "DESIGN.md").read_text()
    for script in ("verify_theme.py", "verify_tokens.py"):
        proc = _run(SKILLS / "heyeddi-handoff" / "scripts" / script, tmp_path, "--check")
        assert proc.returncode == 0, proc.stdout + proc.stderr


def test_token_skill_matches_the_scaffold_stylesheet() -> None:
    skill = (SKILLS / "aura-design-tokens" / "SKILL.md").read_text()
    assert "src/styles/tokens.css" in skill
    assert "light-dark(" in skill


def _cors(root: Path) -> str:
    return (root / "backend" / "app" / "main.py").read_text()


def test_cors_allows_flutter_web_on_loopback_ip(tmp_path: Path) -> None:
    (tmp_path / ".heyeddi").mkdir()
    (tmp_path / ".heyeddi" / "stack.json").write_text(json.dumps({"frontend": "flutter", "web_port": 8085}))
    assert _run(PE / "scripts" / "scaffold_fastapi.py", tmp_path).returncode == 0
    assert "http://127.0.0.1:8085" in _cors(tmp_path)
    assert "http://localhost:8085" in _cors(tmp_path)


def test_cors_allows_vite_on_loopback_ip(tmp_path: Path) -> None:
    assert _run(PE / "scripts" / "scaffold_fastapi.py", tmp_path).returncode == 0
    assert "http://127.0.0.1:5173" in _cors(tmp_path)


def test_backend_dev_extras_include_ruff() -> None:
    data = tomllib.loads((PE / "scaffold" / "fastapi" / "pyproject.toml").read_text())
    dev = data["project"]["optional-dependencies"]["dev"]
    assert any(item.startswith("ruff") for item in dev)


def test_ensure_python_installs_dev_extras(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "pyproject.toml").write_text('[project]\nname = "x"\n')
    log = _fake_tool(tmp_path / "bin", "poetry")
    proc = _run(PE / "scripts" / "ensure_python.py", tmp_path, env=_env_with(tmp_path / "bin"))
    assert proc.returncode == 0
    assert "--all-extras" in log.read_text()


def test_heyeddi_scaffold_leaves_prefs_to_setup(tmp_path: Path) -> None:
    assert _run(PE / "scripts" / "scaffold_heyeddi.py", tmp_path).returncode == 0
    stack = json.loads((tmp_path / ".heyeddi" / "stack.json").read_text())
    assert not {"git", "agent", "setup"} & set(stack)
    verify = _run(SKILLS / "heyeddi-setup" / "scripts" / "verify_setup.py", tmp_path, "--check")
    assert verify.returncode != 0


USER_STACK = {"frontend": "vue", "agent": {"preset": "cautious"}, "git": {"pr_base": "main"}}


def _seed_stack(root: Path) -> Path:
    path = root / ".heyeddi" / "stack.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(USER_STACK))
    return path


def test_force_keeps_user_stack_settings(tmp_path: Path) -> None:
    for index, script in enumerate(
        (
            PE / "scripts" / "scaffold_heyeddi.py",
            FE / "scripts" / "scaffold_heyeddi.py",
            FE / "scripts" / "scaffold_flutter.py",
        )
    ):
        root = tmp_path / str(index)
        root.mkdir()
        path = _seed_stack(root)
        assert _run(script, root, "--force").returncode == 0
        stack = json.loads(path.read_text())
        assert stack["agent"] == {"preset": "cautious"}, script
        assert stack["git"] == {"pr_base": "main"}, script
        assert stack["api_port"] == 8090, script


EXISTING_PUBSPEC = "name: my_app\ndependencies:\n  flutter:\n    sdk: flutter\n"


def _existing_flutter_app(root: Path) -> None:
    (root / "lib").mkdir(parents=True)
    (root / "pubspec.yaml").write_text(EXISTING_PUBSPEC)
    (root / "lib" / "main.dart").write_text("void main() {}\n")


def test_flutter_scaffold_adds_no_demo_files_to_an_existing_app(tmp_path: Path) -> None:
    app = tmp_path / "app"
    _existing_flutter_app(app)
    log = _fake_tool(tmp_path / "bin", "flutter")
    proc = _run(FE / "scripts" / "scaffold_flutter.py", app, "--force", env=_env_with(tmp_path / "bin"))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (app / "pubspec.yaml").read_text() == EXISTING_PUBSPEC
    assert (app / "lib" / "main.dart").read_text() == "void main() {}\n"
    for rel in ("lib/app.dart", "lib/screens", "lib/router", "test/widget_test.dart"):
        assert not (app / rel).exists(), rel
    assert (app / "lib" / "services" / "api_client.dart").is_file()
    call = log.read_text()
    assert call.startswith("pub add")
    for dep in ("flutter_riverpod:^2", "go_router:", "dio:", "dev:flutter_lints:"):
        assert dep in call, dep
    audit = _run(FE / "scripts" / "audit_scaffold.py", app)
    assert json.loads(audit.stdout)["layers"]["flutter"]["missing_required"] == []


def test_flutter_scaffold_fails_when_dependencies_cannot_be_added(tmp_path: Path) -> None:
    app = tmp_path / "app"
    _existing_flutter_app(app)
    _fake_tool(tmp_path / "bin", "flutter", exit_code=1)
    proc = _run(FE / "scripts" / "scaffold_flutter.py", app, env=_env_with(tmp_path / "bin"))
    assert proc.returncode != 0


def test_flutter_scaffold_still_seeds_a_fresh_project(tmp_path: Path) -> None:
    assert _run(FE / "scripts" / "scaffold_flutter.py", tmp_path).returncode == 0
    for rel in ("pubspec.yaml", "lib/app.dart", "test/widget_test.dart"):
        assert (tmp_path / rel).is_file(), rel


def test_dev_server_info_runs_uvicorn_through_poetry(tmp_path: Path) -> None:
    (tmp_path / "backend" / "app").mkdir(parents=True)
    (tmp_path / "backend" / "app" / "main.py").write_text("app = None\n")
    for skill in (PE, FE):
        out = json.loads(_run(skill / "scripts" / "dev_server_info.py", tmp_path).stdout)
        command = next(s["command"] for s in out["servers"] if s["name"] == "fastapi")
        assert command.startswith("poetry run uvicorn"), skill.name


def test_dependency_audit_runs_from_an_installed_copy(tmp_path: Path) -> None:
    installed = tmp_path / ".agents" / "skills" / "project-engineering" / "scripts"
    installed.mkdir(parents=True)
    for source in (PE / "scripts").glob("*.py"):
        (installed / source.name).write_text(source.read_text())
    app = tmp_path / "app"
    app.mkdir()
    (app / "package.json").write_text(json.dumps({"scripts": {"test": "echo no"}}))
    proc = _run(installed / "audit_dependencies.py", app)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["status"] == "fail"
    assert "stub script: test" in result["detail"]
