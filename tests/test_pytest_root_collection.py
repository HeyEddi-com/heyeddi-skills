"""Plain `pytest` from the repo root must collect only the hub tests.

Scaffold and eval sample apps ship their own `tests/` that need their own
dependencies. Without `testpaths`, a bare `pytest` collected them and failed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bare_pytest_collects_only_hub_tests() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-2000:]
    collected = [line for line in result.stdout.splitlines() if "::" in line]
    assert collected, "expected hub tests to be collected"
    assert all(line.startswith("tests/") for line in collected), [
        line for line in collected if not line.startswith("tests/")
    ][:5]
