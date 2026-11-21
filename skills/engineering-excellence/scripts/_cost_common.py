"""Shared constants and helpers for the cost detectors."""
from __future__ import annotations

import re

CODE_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".dart", ".go", ".rb", ".java", ".kt", ".cs", ".php")
CONFIG_EXT = (".tf", ".yaml", ".yml", ".json", ".toml", ".env", ".sh")
SKIP_NAMES = ("cost-rates.json", "budget.json")
DOC_EXT = (".md", ".txt", ".rst", ".mdc")
TEST_PATH = re.compile(r"(^|/)(tests?|fixtures|__tests__|spec)/|(^|/)test_|_test\.|\.(spec|test)\.")

POLL_KEY = re.compile(r"(?:refetchInterval|pollInterval|pollingInterval)\s*:\s*(\d[\d_]*)")
SET_INTERVAL = re.compile(r"setInterval\s*\(")
TRAILING_MS = re.compile(r"[}\)]\s*,\s*(\d[\d_]*)\s*\)")


def poll_intervals_ms(text: str) -> list[int]:
    """Intervals in ms, including timer calls whose callback spans several lines."""
    found = [int(m.group(1).replace("_", "")) for m in POLL_KEY.finditer(text)]
    for m in SET_INTERVAL.finditer(text):
        tail = TRAILING_MS.search(text, m.end(), m.end() + 1500)
        simple = re.match(r"[^,\n]*,\s*(\d[\d_]*)\s*\)", text[m.end():m.end() + 200])
        hit = simple or tail
        if hit:
            found.append(int(hit.group(1).replace("_", "")))
    return found


SECONDS_PER_MONTH = 30 * 24 * 3600


def _finding(driver: str, path: str, message: str, *, low=None, high=None,
             confidence: str = "low", cheaper: str = "", severity: str = "warn") -> dict:
    return {
        "driver": driver,
        "severity": severity,
        "file": path,
        "message": message,
        "low": None if low is None else round(low, 2),
        "high": None if high is None else round(high, 2),
        "confidence": confidence,
        "cheaper": cheaper,
    }


def _skip(path: str) -> bool:
    """Docs, tests, fixtures, and rate files never run in production."""
    name = path.rsplit("/", 1)[-1]
    return name in SKIP_NAMES or path.endswith(DOC_EXT) or bool(TEST_PATH.search(path))


def _is_code(path: str) -> bool:
    return path.endswith(CODE_EXT) and not _skip(path)
