"""Documented composable patterns pass their validator; validate_vue fails when it should."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parent.parent / "skills"
COMPOSABLES = SKILLS / "composable-patterns"
VALIDATE_VUE = SKILLS / "primevue-openprops-architect" / "scripts" / "validate_vue.py"


@pytest.mark.parametrize("pattern", ["fastapi-jwt", "firebase-client"])
def test_documented_pattern_passes_the_validator(tmp_path: Path, pattern: str) -> None:
    doc = (COMPOSABLES / "context" / f"{pattern}.md").read_text()
    code = re.search(r"```ts\n(.*?)```", doc, re.S).group(1)
    (tmp_path / "useThing.ts").write_text(code)
    proc = subprocess.run(
        [
            sys.executable,
            str(COMPOSABLES / "scripts" / "validate_composable.py"),
            "--project-root",
            str(tmp_path),
            "--path",
            "useThing.ts",
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def _validate(root: Path, bin_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATE_VUE), "--project-root", str(root)],
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": str(bin_dir)},
    )


def _npx(root: Path, exit_code: int) -> Path:
    bin_dir = root / "bin"
    bin_dir.mkdir()
    npx = bin_dir / "npx"
    npx.write_text(f'#!/bin/sh\necho "$@"\nexit {exit_code}\n')
    npx.chmod(0o755)
    return bin_dir


def _app(root: Path, tsconfig: str = "{}", installed: bool = True) -> None:
    (root / "package.json").write_text("{}")
    (root / "tsconfig.json").write_text(tsconfig)
    if installed:
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "vue-tsc").write_text("")


def test_validate_vue_fails_without_node_modules(tmp_path: Path) -> None:
    _app(tmp_path, installed=False)
    proc = _validate(tmp_path, _npx(tmp_path, 0))
    assert proc.returncode != 0
    assert "npm install" in proc.stdout + proc.stderr


def test_validate_vue_fails_on_type_errors(tmp_path: Path) -> None:
    _app(tmp_path)
    assert _validate(tmp_path, _npx(tmp_path, 2)).returncode != 0


def test_validate_vue_builds_project_references(tmp_path: Path) -> None:
    _app(tmp_path, tsconfig='{"files": [], "references": [{"path": "./tsconfig.app.json"}]}')
    proc = _validate(tmp_path, _npx(tmp_path, 0))
    assert proc.returncode == 0, proc.stderr
    assert "vue-tsc -b" in proc.stdout


def test_validate_vue_skips_a_project_without_node(tmp_path: Path) -> None:
    assert _validate(tmp_path, _npx(tmp_path, 0)).returncode == 0
