#!/usr/bin/env python3
"""Discover evidenced test/build commands and optionally run them.

Never invent commands. Only propose/run when repo evidence exists for:
npm/pnpm/yarn scripts, pytest, go test, cargo test, or Makefile targets.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root, run_command

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "coverage",
    "__pycache__",
}


def _package_manager(root: Path) -> str | None:
    if (root / "pnpm-lock.yaml").is_file() and shutil.which("pnpm"):
        return "pnpm"
    if (root / "yarn.lock").is_file() and shutil.which("yarn"):
        return "yarn"
    if (root / "package.json").is_file() and shutil.which("npm"):
        return "npm"
    return None


def discover(root: Path) -> list[dict[str, Any]]:
    """Return evidenced commands only (never guessed)."""
    commands: list[dict[str, Any]] = []

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts") or {}
        except (OSError, json.JSONDecodeError):
            scripts = {}
        pm = _package_manager(root)
        if pm:
            for name in ("test", "test:unit", "test:ci", "lint", "typecheck", "build"):
                if name in scripts:
                    commands.append(
                        {
                            "argv": [pm, "run", name],
                            "evidence": f"package.json scripts.{name}",
                            "kind": "npm",
                        }
                    )

    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"
    has_pytest = False
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="ignore")
        if "pytest" in text.lower() or "[tool.pytest" in text:
            has_pytest = True
    if (root / "pytest.ini").is_file() or (root / "conftest.py").is_file():
        has_pytest = True
    if any((root / name).is_dir() for name in ("tests", "test")):
        if pyproject.is_file() or requirements.is_file() or has_pytest:
            has_pytest = True
    if has_pytest and shutil.which("pytest"):
        commands.append({"argv": ["pytest"], "evidence": "pytest config or tests/", "kind": "pytest"})
    elif has_pytest and shutil.which("python"):
        commands.append(
            {
                "argv": ["python", "-m", "pytest"],
                "evidence": "pytest config or tests/ (via python -m)",
                "kind": "pytest",
            }
        )

    if (root / "go.mod").is_file() and shutil.which("go"):
        commands.append({"argv": ["go", "test", "./..."], "evidence": "go.mod", "kind": "go"})

    if (root / "Cargo.toml").is_file() and shutil.which("cargo"):
        commands.append({"argv": ["cargo", "test"], "evidence": "Cargo.toml", "kind": "cargo"})

    makefile = root / "Makefile"
    if makefile.is_file() and shutil.which("make"):
        try:
            text = makefile.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        for target in ("test", "check", "lint", "ci"):
            # Makefile target at column 0: `test:` or `test :`
            if re.search(rf"^{re.escape(target)}\s*:", text, re.M):
                commands.append(
                    {
                        "argv": ["make", target],
                        "evidence": f"Makefile target `{target}`",
                        "kind": "make",
                    }
                )

    # Deduplicate by argv tuple
    seen: set[tuple[str, ...]] = set()
    unique: list[dict[str, Any]] = []
    for cmd in commands:
        key = tuple(cmd["argv"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(cmd)
    return unique


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover and optionally run evidenced verify commands")
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute discovered commands (default: discover only)",
    )
    parser.add_argument(
        "--kinds",
        default=None,
        help="Comma filter: npm,pytest,go,cargo,make",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    commands = discover(root)
    if args.kinds:
        allowed = {k.strip() for k in args.kinds.split(",") if k.strip()}
        commands = [c for c in commands if c.get("kind") in allowed]

    results: list[dict[str, Any]] = []
    if args.run:
        for cmd in commands:
            out = run_command(list(cmd["argv"]), root)
            failed = out.startswith("[exit") or out.startswith("[error]")
            results.append(
                {
                    "argv": cmd["argv"],
                    "evidence": cmd["evidence"],
                    "ok": not failed,
                    "output_excerpt": out[:2000],
                }
            )
            if failed:
                emit(
                    json.dumps(
                        {
                            "status": "failed",
                            "discovered": commands,
                            "results": results,
                            "note": "Do not invent alternate commands. Fix failures or report missing evidence.",
                        },
                        indent=2,
                    )
                )
                raise SystemExit(1)

    emit(
        json.dumps(
            {
                "status": "ok",
                "discovered": commands,
                "results": results if args.run else None,
                "note": (
                    "Only evidenced npm/pytest/go/cargo/make commands are listed. "
                    "Never invent test commands without repo evidence."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
