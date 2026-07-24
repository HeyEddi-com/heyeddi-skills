#!/usr/bin/env python3
"""Orchestrate pre-merge checks including optional UI duplicate scan and visual audit."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from _skill_cli import emit, resolve_project_root, run_command


def status_from_output(output: str) -> str:
    if output.startswith("[skip]") or output.startswith("[error] command not found"):
        return "SKIP"
    if output.startswith("[exit") or "[error]" in output[:80]:
        return "FAIL"
    return "PASS"


def find_skill_script(root: Path, skill_name: str, script_rel: str) -> Path | None:
    candidates = [
        root / ".agents" / "skills" / skill_name / script_rel,
        root / ".cursor" / "skills" / skill_name / script_rel,
        Path(__file__).resolve().parents[2] / skill_name / script_rel,
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def run_skill_script(root: Path, skill_name: str, script_rel: str, extra_args: list[str]) -> str:
    script = find_skill_script(root, skill_name, script_rel)
    if not script:
        return "[skip] skill script not installed: " + skill_name
    cmd = [sys.executable, str(script), "--project-root", str(root), *extra_args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=script.parent)
    except subprocess.TimeoutExpired:
        return "[error] command timed out"
    except FileNotFoundError as exc:
        return f"[error] command not found: {exc}"
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return f"[exit {result.returncode}]\n{output}".strip()
    return output.strip() or "(success, no output)"


def routes_for_visual_audit(root: Path) -> list[str]:
    product = root / ".heyeddi" / "product.md"
    routes: list[str] = []
    if product.is_file():
        for match in __import__("re").finditer(r"`(/[^`]+)`", product.read_text()):
            route = match.group(1)
            if route not in routes:
                routes.append(route)
    return routes[:4] or ["/settings"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-merge gate")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--skip-duplicate-ui", action="store_true")
    parser.add_argument("--skip-prose-audit", action="store_true")
    parser.add_argument("--skip-visual-audit", action="store_true")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    rows: list[tuple[str, str, str]] = []

    pkg = root / "package.json"
    if pkg.is_file():
        data = json.loads(pkg.read_text())
        scripts = data.get("scripts", {})
        if "test" in scripts:
            out = run_command(["npm", "test"], root, timeout=300)
            rows.append(("test", status_from_output(out), out[:200]))
        out = run_command(["npm", "run", "build"], root, timeout=600)
        rows.append(("build", status_from_output(out), out[:200]))
    else:
        rows.append(("build", "SKIP", "no package.json"))

    if shutil.which("npx") and (root / "node_modules").is_dir():
        out = run_command(["npx", "vue-tsc", "--noEmit"], root)
        rows.append(("vue-tsc", status_from_output(out), out[:200]))
    else:
        rows.append(("vue-tsc", "SKIP", "npx or node_modules missing"))

    if not args.skip_duplicate_ui:
        out = run_skill_script(root, "no-duplicate-ui", "scripts/find_duplicate_ui.py", [])
        rows.append(("duplicate-ui", status_from_output(out), out[:200]))

    if not args.skip_prose_audit:
        out = run_skill_script(root, "heyeddi-design", "scripts/verify_prose.py", ["--check"])
        st = status_from_output(out)
        if st == "PASS" and '"ok": false' in out:
            st = "FAIL"
        rows.append(("prose-audit", st, out[:200]))
    else:
        rows.append(("prose-audit", "SKIP", "skipped via --skip-prose-audit"))

    if not args.skip_visual_audit:
        contrast_script = find_skill_script(root, "visual-auditor", "scripts/audit_contrast.py")
        if contrast_script and shutil.which("python3"):
            for route in routes_for_visual_audit(root):
                out = run_skill_script(
                    root,
                    "visual-auditor",
                    "scripts/audit_contrast.py",
                    ["--route", route, "--widths", "375,1440", "--check"],
                )
                label = f"contrast-audit{route}"
                st = status_from_output(out)
                if st == "FAIL" and "playwright" in out.lower():
                    st = "SKIP"
                if st == "PASS" and '"status": "fail"' in out:
                    st = "FAIL"
                rows.append((label, st, out[:200]))
        else:
            rows.append(("contrast-audit", "SKIP", "visual-auditor not installed"))

    lines = ["# Pre-merge Gate Report", "", "| Check | Status | Summary |", "|-------|--------|---------|"]
    for name, st, summary in rows:
        summary = summary.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {name} | {st} | {summary[:120]} |")
    fail_count = sum(1 for _, st, _ in rows if st == "FAIL")
    lines.append("")
    lines.append(f"**Overall:** {'BLOCKED' if fail_count else 'OK'} ({fail_count} failures)")
    emit("\n".join(lines))


if __name__ == "__main__":
    main()
