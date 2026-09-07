#!/usr/bin/env python3
"""Deprecated alias — use assert_runners_claims.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    print(
        "WARN: assert_runners_placeholder is deprecated; use assert_runners_claims",
        file=sys.stderr,
    )
    target = Path(__file__).resolve().parent / "assert_runners_claims.py"
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
