#!/usr/bin/env python3
"""Audit npm/poetry dependency hygiene."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from _skill_cli import emit, resolve_project_root


def _run(cmd: list[str], cwd: Path, timeout: int = 600) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s: {' '.join(cmd)}"
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


def audit_dependencies(root: Path, *, max_major_behind: int = 1) -> tuple[bool, str]:
    issues: list[str] = []
    warnings: list[str] = []

    pkg_path = root / "package.json"
    if not pkg_path.is_file():
        return True, "no frontend package.json"

    if not (root / "package-lock.json").is_file() and not (root / "pnpm-lock.yaml").is_file():
        issues.append("missing lockfile (package-lock.json or pnpm-lock.yaml)")

    if not (root / "node_modules").is_dir():
        issues.append("node_modules missing: run npm install")

    pkg = json.loads(pkg_path.read_text())
    for name, script in pkg.get("scripts", {}).items():
        if str(script).strip().startswith("echo "):
            issues.append(f"stub script: {name}")

    if shutil.which("npm") and (root / "node_modules").is_dir():
        code, out = _run(["npm", "outdated", "--json", "--long"], root, timeout=120)
        # npm exits 1 when something is outdated; --long adds the dependency type.
        if code in (0, 1) and out.strip():
            try:
                outdated = json.loads(out)
                for dep, meta in outdated.items():
                    if isinstance(meta, dict) and meta.get("type") == "dependencies":
                        current = meta.get("current", "")
                        latest = meta.get("latest", "")
                        if _major_behind(current, latest) > max_major_behind:
                            warnings.append(f"{dep}: {current} -> latest {latest}")
            except json.JSONDecodeError:
                pass

    api = root / "backend" / "pyproject.toml"
    if api.is_file() and not shutil.which("poetry"):
        warnings.append("backend pyproject.toml but poetry not on PATH")

    if issues:
        return False, "FAIL: " + "; ".join(issues) + (
            (" | WARN: " + "; ".join(warnings[:5])) if warnings else ""
        )
    if warnings:
        return True, "WARN: " + "; ".join(warnings[:5])
    return True, "lockfile ok, deps installed, no stub scripts"


def _major_behind(current: str, latest: str) -> int:
    try:
        c = [int(x) for x in re.split(r"[.^]", current) if x.isdigit()]
        l = [int(x) for x in re.split(r"[.^]", latest) if x.isdigit()]
        if not c or not l:
            return 0
        return max(0, l[0] - c[0])
    except (ValueError, IndexError):
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit dependency hygiene")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--max-major-behind", type=int, default=1)
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    ok, detail = audit_dependencies(root, max_major_behind=args.max_major_behind)
    emit(json.dumps({"status": "ok" if ok else "fail", "detail": detail}, indent=2))


if __name__ == "__main__":
    main()
