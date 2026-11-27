"""A missing SDK or a failing check must fail the Flutter scripts, not skip."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "flutter-engineering" / "scripts"


def _run(name: str, root: Path, path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), "--project-root", str(root)],
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": path},
    )


def _app(root: Path) -> Path:
    (root / "pubspec.yaml").write_text("name: my_app\n")
    return root


@pytest.mark.parametrize("script", ["run_tests.py", "verify_build.py", "ensure_flutter.py"])
def test_missing_sdk_fails(tmp_path: Path, script: str) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    proc = _run(script, _app(tmp_path), str(empty))
    assert proc.returncode != 0
    assert json.loads(proc.stdout)["status"] == "fail"


@pytest.mark.parametrize("script", ["run_tests.py", "verify_build.py", "ensure_flutter.py"])
def test_failing_command_fails(tmp_path: Path, script: str) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    flutter = bin_dir / "flutter"
    flutter.write_text("#!/bin/sh\nexit 1\n")
    flutter.chmod(0o755)
    proc = _run(script, _app(tmp_path), str(bin_dir))
    assert proc.returncode != 0
    assert json.loads(proc.stdout)["status"] == "fail"


def test_failing_backend_tests_fail(tmp_path: Path) -> None:
    (tmp_path / "backend" / "tests").mkdir(parents=True)
    (tmp_path / "backend" / "pyproject.toml").write_text('[project]\nname = "x"\n')
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    poetry = bin_dir / "poetry"
    poetry.write_text("#!/bin/sh\nexit 1\n")
    poetry.chmod(0o755)
    proc = _run("run_backend_tests.py", tmp_path, str(bin_dir))
    assert proc.returncode != 0
    assert json.loads(proc.stdout)["status"] == "fail"
