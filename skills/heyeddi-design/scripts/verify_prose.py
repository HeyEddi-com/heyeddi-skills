#!/usr/bin/env python3
"""Detect AI prose slop (em/en dashes, banned filler) in UI copy surfaces."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from _skill_cli import emit, fail, resolve_project_root

EM_DASH = "\u2014"
EN_DASH = "\u2013"

DEFAULT_GLOBS = (
    "src/**/*.vue",
    "src/**/*.json",
    "src/locales/**/*",
    "locales/**/*",
)

HEYEDDI_COPY_FILES = (
    ".heyeddi/product.md",
    ".heyeddi/design.md",
)

SKIP_DIR_PARTS = frozenset(
    {
        "node_modules",
        "dist",
        ".git",
        "__tests__",
        "coverage",
    }
)

SKIP_FILE_SUFFIXES = (
    ".spec.ts",
    ".spec.js",
    ".test.ts",
    ".test.js",
    ".d.ts",
)

BANNED_WORDS = (
    "delve",
    "leverage",
    "utilize",
    "seamless",
    "robust",
    "streamline",
    "empower",
    "unlock",
    "tapestry",
    "holistic",
    "groundbreaking",
    "frictionless",
    "transformative",
    "revolutionize",
    "cutting-edge",
    "state-of-the-art",
    "world-class",
    "best-in-class",
    "next-generation",
)

BANNED_PHRASES = (
    "it is important to note",
    "it is worth noting",
    "happy to help",
    "great question",
    "certainly!",
    "absolutely!",
    "in today's landscape",
    "fast-paced world",
    "plays a crucial role",
    "plays a critical role",
    "plays a vital role",
    "at its core",
    "in conclusion",
    "in summary",
    "navigating the complexities",
)

WORD_RE = re.compile(
    r"\b(" + "|".join(re.escape(word) for word in BANNED_WORDS) + r")\b",
    re.IGNORECASE,
)


def should_skip_path(path: Path) -> bool:
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return True
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in SKIP_FILE_SUFFIXES)


def collect_scan_files(root: Path, extra_globs: list[str] | None = None) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    globs = list(DEFAULT_GLOBS) + (extra_globs or [])
    for pattern in globs:
        for path in root.glob(pattern):
            if not path.is_file() or should_skip_path(path):
                continue
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(path)
    for rel in HEYEDDI_COPY_FILES:
        path = root / rel
        if path.is_file() and path.resolve() not in seen:
            seen.add(path.resolve())
            files.append(path)
    return sorted(files)


def line_number_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def find_dash_violations(text: str, source: str) -> list[dict]:
    issues: list[dict] = []
    for idx, char in enumerate(text):
        if char not in (EM_DASH, EN_DASH):
            continue
        line = line_number_at(text, idx)
        line_text = text.splitlines()[line - 1].strip()
        dash_name = "em dash" if char == EM_DASH else "en dash"
        issues.append(
            {
                "type": "dash",
                "source": source,
                "line": line,
                "message": f"{dash_name} (U+{ord(char):04X}) in UI copy; use period, comma, colon, or ASCII ' - '",
                "excerpt": line_text[:160],
            }
        )
    return issues


def find_banned_violations(text: str, source: str) -> list[dict]:
    issues: list[dict] = []
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        start = 0
        while True:
            idx = lowered.find(phrase, start)
            if idx < 0:
                break
            line = line_number_at(text, idx)
            line_text = text.splitlines()[line - 1].strip()
            issues.append(
                {
                    "type": "phrase",
                    "source": source,
                    "line": line,
                    "message": f"banned AI filler phrase: {phrase!r}",
                    "excerpt": line_text[:160],
                }
            )
            start = idx + len(phrase)
    for match in WORD_RE.finditer(text):
        line = line_number_at(text, match.start())
        line_text = text.splitlines()[line - 1].strip()
        issues.append(
            {
                "type": "word",
                "source": source,
                "line": line,
                "message": f"banned AI filler word: {match.group(1)!r}",
                "excerpt": line_text[:160],
            }
        )
    return issues


def scan_text(text: str, source: str) -> list[dict]:
    issues: list[dict] = []
    issues.extend(find_dash_violations(text, source))
    issues.extend(find_banned_violations(text, source))
    return issues


def verify_file(path: Path, root: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [
            {
                "type": "read_error",
                "source": str(path.relative_to(root)),
                "line": 0,
                "message": str(exc),
                "excerpt": "",
            }
        ]
    rel = str(path.relative_to(root))
    return scan_text(text, rel)


def verify_project(root: Path, extra_globs: list[str] | None = None) -> dict:
    files = collect_scan_files(root, extra_globs)
    issues: list[dict] = []
    for path in files:
        issues.extend(verify_file(path, root))
    dash_count = sum(1 for issue in issues if issue["type"] == "dash")
    filler_count = sum(1 for issue in issues if issue["type"] in {"word", "phrase"})
    return {
        "ok": not issues,
        "files_scanned": len(files),
        "issue_count": len(issues),
        "dash_count": dash_count,
        "filler_count": filler_count,
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify UI copy has no AI prose slop")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--glob", action="append", default=[], help="Extra glob under project root")
    parser.add_argument("--check", action="store_true", help="Exit 1 if violations found")
    args = parser.parse_args()

    root = resolve_project_root(args.project_root)
    extra = args.glob or None
    result = verify_project(root, extra)
    emit(result)

    if args.check and not result.get("ok"):
        samples = result.get("issues") or []
        preview = "; ".join(
            f"{item['source']}:{item['line']} {item['message']}" for item in samples[:5]
        )
        fail(
            "prose verification failed: "
            f"{result.get('issue_count', 0)} issue(s) "
            f"({result.get('dash_count', 0)} dash, {result.get('filler_count', 0)} filler). "
            f"See context/PROSE_ANTI_SLOP.md. Examples: {preview}"
        )


if __name__ == "__main__":
    main()
