#!/usr/bin/env python3
"""Orchestrate pre-merge ship checks (stack-aware + optional PR sign-off).

Any FAIL makes the process exit 1 (hard stop). SKIP is for absent trees or
optional tooling. Emergency --skip-* flags are SKIP unless --signoff / PR mode,
where they become FAIL.

After @heyeddi-pr-review → @heyeddi-pr-respond, run this gate before merge.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _skill_cli import emit, resolve_project_root, run_command

EMERGENCY_SKIP_FLAGS = (
    "skip_backend",
    "skip_engineering_audit",
    "skip_setup_audit",
)


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
        for match in re.finditer(r"`(/[^`]+)`", product.read_text(encoding="utf-8")):
            route = match.group(1)
            if route not in routes:
                routes.append(route)
    return routes[:4] or ["/settings"]


def backend_python(root: Path) -> str | None:
    venv_py = root / "backend" / ".venv" / "bin" / "python"
    if venv_py.is_file():
        return str(venv_py)
    return shutil.which("python3") or shutil.which("python")


def detect_stack(root: Path) -> dict[str, bool]:
    return {
        "vue": (root / "package.json").is_file(),
        "flutter": (root / "pubspec.yaml").is_file(),
        "backend": (root / "backend").is_dir(),
    }


def detect_pr_number(root: Path, explicit: int | None) -> int | None:
    if explicit is not None:
        return explicit
    if not shutil.which("gh"):
        return None
    out = run_command(
        ["gh", "pr", "view", "--json", "number", "-q", ".number"],
        root,
        timeout=60,
    )
    if out.startswith("[exit") or out.startswith("[error]"):
        return None
    try:
        return int(out.strip())
    except ValueError:
        return None


def run_git_clean_checks(root: Path, rows: list[tuple[str, str, str]]) -> None:
    # .git may be a dir or a worktree file
    if not (root / ".git").exists():
        rows.append(("git-clean", "SKIP", "no .git"))
        rows.append(("git-pushed", "SKIP", "no .git"))
        return
    if not shutil.which("git"):
        rows.append(("git-clean", "FAIL", "git not found"))
        rows.append(("git-pushed", "FAIL", "git not found"))
        return
    out = run_command(["git", "status", "--porcelain"], root, timeout=60)
    if out.startswith("[exit") or out.startswith("[error]"):
        rows.append(("git-clean", "FAIL", out[:200]))
        return
    if out.strip() and not out.startswith("[skip]"):
        rows.append(("git-clean", "FAIL", f"dirty working tree: {out.strip()[:160]}"))
    else:
        rows.append(("git-clean", "PASS", "working tree clean"))

    # Unpushed commits when upstream exists
    up = run_command(["git", "rev-parse", "--abbrev-ref", "@{u}"], root, timeout=30)
    if up.startswith("[exit") or up.startswith("[error]"):
        rows.append(("git-pushed", "SKIP", "no upstream configured"))
        return
    ahead = run_command(["git", "rev-list", "--count", "@{u}..HEAD"], root, timeout=30)
    if ahead.startswith("[exit") or ahead.startswith("[error]"):
        rows.append(("git-pushed", "FAIL", ahead[:200]))
        return
    try:
        count = int(ahead.strip() or "0")
    except ValueError:
        rows.append(("git-pushed", "FAIL", f"bad ahead count: {ahead[:80]}"))
        return
    if count > 0:
        rows.append(("git-pushed", "FAIL", f"{count} commit(s) not pushed to upstream"))
    else:
        rows.append(("git-pushed", "PASS", "branch synced with upstream"))


def run_pr_checks(root: Path, pr: int, rows: list[tuple[str, str, str]]) -> None:
    if not shutil.which("gh"):
        rows.append(("pr-checks", "FAIL", "gh CLI required for PR sign-off"))
        rows.append(("pr-review-threads", "FAIL", "gh CLI required for PR sign-off"))
        return

    checks = run_command(["gh", "pr", "checks", str(pr)], root, timeout=120)
    # gh pr checks exits non-zero when failing/pending; treat pending as FAIL for sign-off
    st = status_from_output(checks)
    if st == "PASS" and re.search(r"\b(fail|pending|cancel)\b", checks, re.I):
        st = "FAIL"
    if checks.strip() in {"", "(success, no output)"}:
        # No checks configured — soft pass with note
        rows.append(("pr-checks", "PASS", "no PR checks reported"))
    else:
        rows.append(("pr-checks", st, checks[:200]))

    # Unresolved review threads via GraphQL
    repo_out = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        root,
        timeout=60,
    )
    if repo_out.startswith("[exit") or repo_out.startswith("[error]"):
        rows.append(("pr-review-threads", "FAIL", f"repo resolve failed: {repo_out[:120]}"))
        return
    owner_repo = repo_out.strip()
    if "/" not in owner_repo:
        rows.append(("pr-review-threads", "FAIL", f"bad repo: {owner_repo}"))
        return
    owner, name = owner_repo.split("/", 1)
    query = (
        "query($owner:String!,$name:String!,$n:Int!){"
        "repository(owner:$owner,name:$name){"
        "pullRequest(number:$n){reviewThreads(first:100){nodes{isResolved}}}}}"
    )
    gql = run_command(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"n={pr}",
        ],
        root,
        timeout=120,
    )
    if gql.startswith("[exit") or gql.startswith("[error]"):
        rows.append(("pr-review-threads", "FAIL", gql[:200]))
        return
    try:
        data = json.loads(gql)
        nodes = (
            data.get("data", {})
            .get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
            .get("nodes")
            or []
        )
        unresolved = [n for n in nodes if isinstance(n, dict) and not n.get("isResolved")]
        if unresolved:
            rows.append(
                (
                    "pr-review-threads",
                    "FAIL",
                    f"{len(unresolved)} unresolved review thread(s); run @heyeddi-pr-respond",
                )
            )
        else:
            rows.append(("pr-review-threads", "PASS", "no unresolved review threads"))
    except json.JSONDecodeError:
        rows.append(("pr-review-threads", "FAIL", f"bad graphql json: {gql[:120]}"))


def run_backend_checks(root: Path, rows: list[tuple[str, str, str]]) -> None:
    backend = root / "backend"
    if not backend.is_dir():
        rows.append(("backend-pytest", "SKIP", "no backend/"))
        rows.append(("backend-f821", "SKIP", "no backend/"))
        return

    py = backend_python(root)
    if not py:
        rows.append(("backend-pytest", "FAIL", "python not found for backend tests"))
        rows.append(("backend-f821", "FAIL", "python not found for ruff F821"))
        return

    out = run_command([py, "-m", "pytest", "-q", "tests"], backend, timeout=900)
    rows.append(("backend-pytest", status_from_output(out), out[:200]))

    app_dir = backend / "app"
    out = run_command([py, "-m", "ruff", "check", str(app_dir), "--select", "F821"], backend, timeout=120)
    st = status_from_output(out)
    if st == "SKIP" or (st == "FAIL" and "No module named" in out and "ruff" in out):
        st = "FAIL"
        out = "ruff required (backend[dev]); " + out
    rows.append(("backend-f821", st, out[:200]))


def run_frontend_checks(root: Path, rows: list[tuple[str, str, str]]) -> None:
    pkg = root / "package.json"
    if not pkg.is_file():
        rows.append(("test", "SKIP", "no package.json"))
        rows.append(("build", "SKIP", "no package.json"))
        rows.append(("vue-tsc", "SKIP", "no package.json"))
        return

    data = json.loads(pkg.read_text(encoding="utf-8"))
    scripts = data.get("scripts", {})
    if "test" in scripts:
        out = run_command(["npm", "test", "--", "--run"], root, timeout=300)
        rows.append(("test", status_from_output(out), out[:200]))
    else:
        rows.append(("test", "FAIL", "package.json has no test script"))
    out = run_command(["npm", "run", "build"], root, timeout=600)
    rows.append(("build", status_from_output(out), out[:200]))

    # vue-tsc only when Vue toolchain likely present
    has_vue = (root / "node_modules" / "vue").is_dir() or "vue" in json.dumps(data.get("dependencies", {}))
    if has_vue and shutil.which("npx") and (root / "node_modules").is_dir():
        out = run_command(["npx", "vue-tsc", "--noEmit"], root, timeout=300)
        rows.append(("vue-tsc", status_from_output(out), out[:200]))
    elif has_vue:
        rows.append(("vue-tsc", "FAIL", "Vue project but npx/node_modules missing"))
    else:
        rows.append(("vue-tsc", "SKIP", "no Vue dependency detected"))


def run_flutter_checks(root: Path, rows: list[tuple[str, str, str]]) -> None:
    if not (root / "pubspec.yaml").is_file():
        rows.append(("dart-analyze", "SKIP", "no pubspec.yaml"))
        rows.append(("flutter-test", "SKIP", "no pubspec.yaml"))
        return

    dart = shutil.which("dart")
    flutter = shutil.which("flutter")
    if dart:
        out = run_command(["dart", "analyze"], root, timeout=300)
        rows.append(("dart-analyze", status_from_output(out), out[:200]))
    elif flutter:
        out = run_command(["flutter", "analyze"], root, timeout=300)
        rows.append(("dart-analyze", status_from_output(out), out[:200]))
    else:
        rows.append(("dart-analyze", "FAIL", "dart/flutter not found for Flutter project"))

    if flutter:
        out = run_command(["flutter", "test"], root, timeout=900)
        rows.append(("flutter-test", status_from_output(out), out[:200]))
    elif dart:
        out = run_command(["dart", "test"], root, timeout=900)
        rows.append(("flutter-test", status_from_output(out), out[:200]))
    else:
        rows.append(("flutter-test", "FAIL", "dart/flutter not found for tests"))


def changed_prose_globs(root: Path, pr: int | None) -> list[str]:
    """Extra verify_prose globs for changed markdown outside default surfaces."""
    names: list[str] = []
    if pr and shutil.which("gh"):
        out = run_command(["gh", "pr", "diff", str(pr), "--name-only"], root, timeout=120)
        if not (out.startswith("[exit") or out.startswith("[error]")):
            names = [line.strip() for line in out.splitlines() if line.strip()]
    if not names:
        out = run_command(["git", "diff", "--name-only", "HEAD"], root, timeout=60)
        if not (out.startswith("[exit") or out.startswith("[error]")):
            names = [line.strip() for line in out.splitlines() if line.strip()]
    globs: list[str] = []
    for name in names:
        if not name.endswith((".md", ".mdx")):
            continue
        # Defaults already cover .heyeddi/product.md + design.md; still fine to re-scan
        if name.startswith("src/") or "/locales/" in name:
            continue
        globs.append(name)
    # de-dupe, cap
    seen: set[str] = set()
    out_globs: list[str] = []
    for g in globs:
        if g not in seen:
            seen.add(g)
            out_globs.append(g)
        if len(out_globs) >= 40:
            break
    return out_globs


def run_visual_checks(root: Path, rows: list[tuple[str, str, str]], *, require: bool) -> None:
    contrast_script = find_skill_script(root, "visual-auditor", "scripts/audit_contrast.py")
    routes = routes_for_visual_audit(root)
    if not contrast_script:
        st = "FAIL" if require else "SKIP"
        rows.append(("contrast-audit", st, "visual-auditor not installed"))
        return
    if not shutil.which("python3"):
        st = "FAIL" if require else "SKIP"
        rows.append(("contrast-audit", st, "python3 missing"))
        return

    any_playwright_skip = False
    for route in routes:
        out = run_skill_script(
            root,
            "visual-auditor",
            "scripts/audit_contrast.py",
            ["--route", route, "--widths", "375,1440", "--check"],
        )
        label = f"contrast-audit{route}"
        st = status_from_output(out)
        if st == "FAIL" and "playwright" in out.lower():
            any_playwright_skip = True
            st = "FAIL" if require else "SKIP"
        if st == "PASS" and '"status": "fail"' in out:
            st = "FAIL"
        rows.append((label, st, out[:200]))
    if any_playwright_skip and require:
        rows.append(("contrast-playwright", "FAIL", "Playwright required for visual sign-off"))


def build_report(
    rows: list[tuple[str, str, str]],
    *,
    pr: int | None,
    signoff: bool,
    emergency_used: list[str],
) -> tuple[str, dict[str, Any], int]:
    fail_count = sum(1 for _, st, _ in rows if st == "FAIL")
    skip_count = sum(1 for _, st, _ in rows if st == "SKIP")
    blocked = fail_count > 0
    lines = [
        "# Pre-merge Gate Report",
        "",
        f"- **PR:** {pr if pr is not None else 'none (local)'}",
        f"- **Sign-off mode:** {'yes' if signoff else 'no'}",
        "",
        "| Check | Status | Summary |",
        "|-------|--------|---------|",
    ]
    for name, st, summary in rows:
        summary = summary.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {name} | {st} | {summary[:120]} |")
    lines.append("")
    if emergency_used and signoff:
        lines.append(
            f"**Emergency skips used under sign-off:** {', '.join(emergency_used)} → not merge-ready"
        )
        lines.append("")
        blocked = True
    overall = "BLOCKED" if blocked else "OK"
    lines.append(f"**Overall:** {overall} ({fail_count} failures, {skip_count} skips)")
    payload = {
        "ok": not blocked,
        "overall": overall,
        "pr": pr,
        "signoff": signoff,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "emergency_skips": emergency_used,
        "checks": [{"name": n, "status": s, "summary": m} for n, s, m in rows],
    }
    return "\n".join(lines), payload, (1 if blocked else 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-merge ship gate")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--pr", type=int, default=None, help="PR number (enables PR sign-off checks)")
    parser.add_argument("--no-pr", action="store_true", help="Do not auto-detect PR")
    parser.add_argument(
        "--signoff",
        action="store_true",
        help="Merge sign-off: fail emergency skips; enable git-clean + PR checks when PR known",
    )
    parser.add_argument("--json", action="store_true", help="Also emit JSON object after markdown")
    parser.add_argument("--skip-duplicate-ui", action="store_true")
    parser.add_argument("--skip-prose-audit", action="store_true")
    parser.add_argument("--skip-visual-audit", action="store_true")
    parser.add_argument("--skip-engineering-audit", action="store_true", help="Emergency only")
    parser.add_argument("--skip-setup-audit", action="store_true", help="Emergency only")
    parser.add_argument("--skip-backend", action="store_true", help="Emergency only")
    parser.add_argument("--skip-flutter", action="store_true")
    parser.add_argument("--skip-git-clean", action="store_true", help="Skip dirty/unpushed checks")
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    rows: list[tuple[str, str, str]] = []

    # --pr N implies sign-off. --signoff auto-detects the open PR unless --no-pr.
    # Bare local runs (tests / everyday) do not auto-attach a PR.
    if args.pr is not None:
        pr = args.pr
        signoff = True
    elif args.signoff and not args.no_pr:
        pr = detect_pr_number(root, None)
        signoff = True
    else:
        pr = None
        signoff = bool(args.signoff)

    emergency_used: list[str] = []
    if args.skip_backend:
        emergency_used.append("--skip-backend")
    if args.skip_engineering_audit:
        emergency_used.append("--skip-engineering-audit")
    if args.skip_setup_audit:
        emergency_used.append("--skip-setup-audit")

    if signoff and not args.skip_git_clean:
        run_git_clean_checks(root, rows)

    if signoff and pr is not None:
        run_pr_checks(root, pr, rows)

    if not args.skip_setup_audit:
        out = run_skill_script(root, "heyeddi-setup", "scripts/verify_setup.py", ["--check"])
        st = status_from_output(out)
        if st == "PASS" and '"complete": false' in out:
            st = "FAIL"
        rows.append(("setup-audit", st, out[:200]))
    else:
        st = "FAIL" if signoff else "SKIP"
        rows.append(("setup-audit", st, "skipped via --skip-setup-audit"))

    stack = detect_stack(root)
    run_frontend_checks(root, rows)

    if args.skip_backend:
        st = "FAIL" if signoff else "SKIP"
        rows.append(("backend-pytest", st, "skipped via --skip-backend"))
        rows.append(("backend-f821", st, "skipped via --skip-backend"))
    else:
        run_backend_checks(root, rows)

    if args.skip_flutter:
        rows.append(("dart-analyze", "SKIP", "skipped via --skip-flutter"))
        rows.append(("flutter-test", "SKIP", "skipped via --skip-flutter"))
    else:
        run_flutter_checks(root, rows)

    if not args.skip_duplicate_ui:
        out = run_skill_script(root, "no-duplicate-ui", "scripts/find_duplicate_ui.py", [])
        rows.append(("duplicate-ui", status_from_output(out), out[:200]))
    else:
        rows.append(("duplicate-ui", "SKIP", "skipped via --skip-duplicate-ui"))

    if not args.skip_prose_audit:
        extra = changed_prose_globs(root, pr)
        prose_args = ["--check"]
        for g in extra:
            prose_args.extend(["--glob", g])
        out = run_skill_script(root, "heyeddi-design", "scripts/verify_prose.py", prose_args)
        st = status_from_output(out)
        if st == "PASS" and '"ok": false' in out:
            st = "FAIL"
        note = out[:160]
        if extra:
            note = f"globs={len(extra)}; " + note
        rows.append(("prose-audit", st, note[:200]))
    else:
        rows.append(("prose-audit", "SKIP", "skipped via --skip-prose-audit"))

    if not args.skip_engineering_audit:
        out = run_skill_script(
            root,
            "engineering-excellence",
            "scripts/audit_engineering.py",
            ["--check"],
        )
        st = status_from_output(out)
        if st == "PASS" and '"ok": false' in out:
            st = "FAIL"
        rows.append(("engineering-audit", st, out[:200]))
    else:
        st = "FAIL" if signoff else "SKIP"
        rows.append(("engineering-audit", st, "skipped via --skip-engineering-audit"))

    if not args.skip_visual_audit:
        # Require visual when product routes exist and we are in sign-off
        require_visual = signoff and (root / ".heyeddi" / "product.md").is_file()
        run_visual_checks(root, rows, require=require_visual)
    else:
        rows.append(("contrast-audit", "SKIP", "skipped via --skip-visual-audit"))

    if signoff and emergency_used:
        rows.append(
            (
                "signoff-emergency-skips",
                "FAIL",
                "emergency skips not allowed for merge sign-off: " + ", ".join(emergency_used),
            )
        )

    md, payload, code = build_report(rows, pr=pr, signoff=signoff, emergency_used=emergency_used)
    if args.json:
        emit(md + "\n\n```json\n" + json.dumps(payload, indent=2) + "\n```")
    else:
        emit(md)
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main()
