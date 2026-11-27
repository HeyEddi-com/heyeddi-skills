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
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from _skill_cli import EXIT_DEGRADED, emit, gh_status, resolve_project_root, run_command

EMERGENCY_SKIP_FLAGS = (
    "skip_backend",
    "skip_engineering_audit",
    "skip_setup_audit",
    "skip_cost_estimate",
)

# Written by the gate's own checks or by skill auto-sync. They never make the tree dirty.
GENERATED_PATHS = re.compile(
    r"^(\.heyeddi/docs/(engineering-audit|cost-estimate)-[^/]*\.md"
    r"|\.heyeddi/audits/visual/[^/]*-contrast-\d{4}-\d{2}-\d{2}\.(md|json)"
    r"|\.heyeddi/skills-index\.(json|md)"
    r"|\.cursor/rules/heyeddi-always-on\.mdc)$"
)
ALWAYS_ON_BLOCK = re.compile(r"<!-- heyeddi-always-on:start -->.*?<!-- heyeddi-always-on:end -->", re.DOTALL)

# A reply that leaves a thread open on purpose: "**Declined:** <reason>".
DECLINE_MARKER = re.compile(r"^\s*(?:\*\*)?Declined(?:\*\*)?\s*:(?:\*\*)?(.*)", re.IGNORECASE | re.DOTALL)

CI_CONFIG_FILES = (
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    "cloudbuild.yaml",
    "Jenkinsfile",
)

DEV_SERVER_TIMEOUT = 90


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
    # gh 2.105+ writes hints to stderr on success; keep only stdout then.
    if result.returncode == 0 and Path(cmd[0]).name == "gh":
        output = result.stdout or ""
    else:
        output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return f"[exit {result.returncode}]\n{output}".strip()
    return output.strip() or "(success, no output)"


def run_context_secret_check(root: Path, rows: list[tuple[str, str, str]]) -> None:
    """Decision and design logs are committed and fed back to agents: no credentials in them."""
    docs = (".heyeddi/docs/engineering/decisions.md", ".heyeddi/design.md")
    if not any((root / doc).is_file() for doc in docs):
        rows.append(("context-secrets", "SKIP", "no .heyeddi decision or design log"))
        return
    out = run_skill_script(root, "heyeddi", "scripts/context_index.py", ["--check"])
    rows.append(("context-secrets", status_from_output(out), " ".join(out.split())[:200]))


def routes_for_visual_audit(root: Path) -> list[str]:
    product = root / ".heyeddi" / "product.md"
    routes: list[str] = []
    if product.is_file():
        for match in re.finditer(r"`(/[^`]+)`", product.read_text(encoding="utf-8")):
            route = match.group(1)
            if route not in routes:
                routes.append(route)
    return routes[:4]


def backend_python(root: Path) -> str | None:
    venv_py = root / "backend" / ".venv" / "bin" / "python"
    if venv_py.is_file():
        return str(venv_py)
    return shutil.which("python3") or shutil.which("python")


def declared_runner(root: Path) -> str | None:
    """`uv` or `poetry` when the backend or the repo root declares it."""
    for folder in (root / "backend", root):
        pyproject = folder / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8", errors="ignore") if pyproject.is_file() else ""
        if (folder / "uv.lock").is_file() or re.search(r"(?m)^\[tool\.uv[\].]", text):
            return "uv"
        if (folder / "poetry.lock").is_file() or re.search(r"(?m)^\[tool\.poetry[\].]", text):
            return "poetry"
    return None


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


def detect_pr_url(root: Path, pr: int | None) -> str | None:
    """Full PR URL so every report and summary can link it."""
    if pr is None or not shutil.which("gh"):
        return None
    out = run_command(["gh", "pr", "view", str(pr), "--json", "url", "-q", ".url"], root, timeout=60).strip()
    return out if out.startswith("https://") else None


def _outside_always_on(text: str) -> str:
    lines = ALWAYS_ON_BLOCK.sub("", text).splitlines()
    return "\n".join(line.rstrip() for line in lines if line.strip() and line.strip() != "# Agent instructions")


def is_generated(root: Path, status_line: str) -> bool:
    """True for a `git status --porcelain` line that only reflects generated content."""
    # run_command strips the output, so split on whitespace instead of fixed columns.
    parts = status_line.split(maxsplit=1)
    if len(parts) != 2:
        return False
    code, path = parts
    if GENERATED_PATHS.match(path):
        return True
    if path != "AGENTS.md" or not (root / path).is_file():
        return False
    before = "" if code == "??" else run_command(["git", "show", "HEAD:AGENTS.md"], root, timeout=60)
    if before.startswith("[exit") or before.startswith("[error]"):
        return False
    return _outside_always_on((root / path).read_text(encoding="utf-8")) == _outside_always_on(before)


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
    out = run_command(["git", "status", "--porcelain", "--untracked-files=all"], root, timeout=60)
    if out.startswith("[exit") or out.startswith("[error]"):
        rows.append(("git-clean", "FAIL", out[:200]))
        return
    # run_command maps empty stdout to "(success, no output)" — that is clean.
    listed = out.strip() and out.strip() != "(success, no output)" and not out.startswith("[skip]")
    dirty = [line.strip() for line in out.splitlines() if listed and line.strip() and not is_generated(root, line)]
    if dirty:
        rows.append(("git-clean", "FAIL", f"dirty working tree: {', '.join(dirty)[:160]}"))
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


def add_unverified_pr_rows(root: Path, rows: list[tuple[str, str, str]]) -> bool:
    """Mark the PR checks UNVERIFIED when gh is missing or logged out. True when it did."""
    status = gh_status(root)
    if status["ok"]:
        return False
    why = f"{status['reason']}; {status['hint']}".strip("; ")
    rows.append(("pr-checks", "UNVERIFIED", why))
    rows.append(("pr-review-threads", "UNVERIFIED", why))
    return True


def has_ci_config(root: Path) -> bool:
    """True when the repo configures CI, so a PR with no checks is not a pass."""
    workflows = root / ".github" / "workflows"
    if any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml")):
        return True
    if any((root / name).is_file() for name in CI_CONFIG_FILES):
        return True
    eddi = root / "eddi-ci.yaml"
    if eddi.is_file():
        return bool(re.search(r"(?m)^pipeline:[ \t]*\n[ \t]+\S", eddi.read_text(encoding="utf-8")))
    return False


def declined_reason(body: str) -> str | None:
    """The reason when a reply opens with the decline marker and says why, else None."""
    match = DECLINE_MARKER.match(body or "")
    if not match:
        return None
    reason = match.group(1).strip()
    return reason if len(re.findall(r"\w+", reason)) >= 3 else None


def triage_threads(nodes: list[Any], pr_author: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split unresolved threads into (blocking, declined by the PR author with a reason)."""
    blocking: list[dict[str, Any]] = []
    declined: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, dict) or node.get("isResolved"):
            continue
        comments = node.get("comments") or {}
        last = (comments.get("nodes") or [{}])[-1] or {}
        login = str((last.get("author") or {}).get("login") or "")
        is_reply = int(comments.get("totalCount") or 0) > 1
        by_author = bool(pr_author) and login.casefold() == pr_author.casefold()
        reason = declined_reason(str(last.get("body") or "")) if is_reply and by_author else None
        if reason is None:
            blocking.append(node)
        else:
            declined.append(
                {"path": node.get("path"), "line": node.get("line"), "url": last.get("url"), "reason": reason}
            )
    return blocking, declined


THREADS_QUERY = (
    "query($owner:String!,$name:String!,$n:Int!,$after:String){"
    "repository(owner:$owner,name:$name){"
    "pullRequest(number:$n){author{login} reviewThreads(first:100,after:$after){"
    "pageInfo{hasNextPage endCursor} nodes{isResolved path line "
    "comments(last:1){totalCount nodes{body url author{login}}}}}}}}"
)


def run_pr_checks(
    root: Path,
    pr: int,
    rows: list[tuple[str, str, str]],
    declined: list[dict[str, Any]] | None = None,
) -> None:
    if add_unverified_pr_rows(root, rows):
        return

    checks = run_command(["gh", "pr", "checks", str(pr)], root, timeout=120)
    # gh pr checks exits non-zero when failing/pending; treat pending as FAIL for sign-off
    st = status_from_output(checks)
    if st == "PASS" and re.search(r"\b(fail|pending|cancel)\b", checks, re.I):
        st = "FAIL"
    watch = f"`gh pr checks {pr} --watch`"
    if checks.strip() in {"", "(success, no output)"}:
        # No checks configured — soft pass with note
        rows.append(("pr-checks", "PASS", "no PR checks reported"))
    elif "no checks reported" in checks:
        if has_ci_config(root):
            note = f"CI is configured but no checks reported; run {watch} once they register, then rerun"
            rows.append(("pr-checks", "FAIL", note))
        else:
            rows.append(("pr-checks", "PASS", "no checks reported and the repo configures no CI"))
    elif st == "FAIL" and (checks.startswith("[exit 8]") or re.search(r"\bpending\b", checks)):
        rows.append(("pr-checks", st, f"checks pending: run {watch}, then rerun the gate. {checks}"[:200]))
    elif st == "PASS" and re.search(r"(?m)^HeyEddi Reviewer\tskipping\b", checks):
        # Seen when the automatic review cap is used up: the newest commit was never read.
        note = f"HeyEddi Reviewer skipped the latest commit: comment `/heyeddi review` on PR {pr}, then {watch}"
        rows.append(("pr-checks", "FAIL", note))
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
    nodes: list[Any] = []
    cursor = ""
    pr_author = ""
    while True:
        cmd = [
            "gh", "api", "graphql",
            "-f", f"query={THREADS_QUERY}",
            "-F", f"owner={owner}",
            "-F", f"name={name}",
            "-F", f"n={pr}",
        ]
        if cursor:
            cmd += ["-f", f"after={cursor}"]
        gql = run_command(cmd, root, timeout=120)
        if gql.startswith("[exit") or gql.startswith("[error]"):
            rows.append(("pr-review-threads", "FAIL", gql[:200]))
            return
        try:
            pull = json.loads(gql)["data"]["repository"]["pullRequest"]
            threads = pull["reviewThreads"]
            nodes += threads.get("nodes") or []
            page = threads.get("pageInfo") or {}
            pr_author = str((pull.get("author") or {}).get("login") or "")
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
            rows.append(("pr-review-threads", "FAIL", f"bad graphql json: {gql[:120]}"))
            return
        cursor = str(page.get("endCursor") or "")
        if not (page.get("hasNextPage") and cursor):
            break
    blocking, passed = triage_threads(nodes, pr_author)
    if declined is not None:
        declined.extend(passed)
    if blocking:
        rows.append(
            (
                "pr-review-threads",
                "FAIL",
                f"{len(blocking)} unresolved review thread(s); run @heyeddi-pr-respond",
            )
        )
    elif passed:
        rows.append(("pr-review-threads", "PASS", f"{len(passed)} declined with a reason (listed below)"))
    else:
        rows.append(("pr-review-threads", "PASS", "no unresolved review threads"))


def run_backend_checks(root: Path, rows: list[tuple[str, str, str]]) -> None:
    backend = root / "backend"
    if not backend.is_dir():
        rows.append(("backend-pytest", "SKIP", "no backend/"))
        rows.append(("backend-f821", "SKIP", "no backend/"))
        return

    runner = declared_runner(root)
    if runner:
        pytest_cmd = [runner, "run", "pytest"]
        ruff_cmd = [runner, "run", "ruff"]
    else:
        py = backend_python(root)
        if not py:
            rows.append(("backend-pytest", "FAIL", "python not found for backend tests"))
            rows.append(("backend-f821", "FAIL", "python not found for ruff F821"))
            return
        pytest_cmd = [py, "-m", "pytest"]
        ruff_cmd = [py, "-m", "ruff"]

    out = run_command([*pytest_cmd, "-q", "tests"], backend, timeout=900)
    st = status_from_output(out)
    if runner and st == "SKIP":
        st = "FAIL"
        out = f"{runner} is declared by the project: install it. " + out
    rows.append(("backend-pytest", st, out[:200]))

    app_dir = backend / "app"
    out = run_command([*ruff_cmd, "check", str(app_dir), "--select", "F821"], backend, timeout=120)
    st = status_from_output(out)
    missing = "ruff" in out and ("No module named" in out or "Failed to spawn" in out or "not found" in out)
    if st == "SKIP" or (st == "FAIL" and missing):
        st = "FAIL"
        out = "ruff required (backend dev dependencies); " + out
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
    deps_blob = json.dumps(
        {
            **(data.get("dependencies") or {}),
            **(data.get("devDependencies") or {}),
        }
    )
    has_vue = (root / "node_modules" / "vue").is_dir() or "vue" in deps_blob
    # Tooling-only package.json (e.g. skills hub) — no app test/build required
    app_like = has_vue or "vite" in deps_blob or (root / "src").is_dir()

    if "test" in scripts:
        out = run_command(["npm", "test", "--", "--run"], root, timeout=300)
        rows.append(("test", status_from_output(out), out[:200]))
    elif app_like:
        rows.append(("test", "FAIL", "package.json has no test script"))
    else:
        rows.append(("test", "SKIP", "tooling package.json (no app test script)"))

    if "build" in scripts:
        out = run_command(["npm", "run", "build"], root, timeout=600)
        rows.append(("build", status_from_output(out), out[:200]))
    elif app_like:
        rows.append(("build", "FAIL", "package.json has no build script"))
    else:
        rows.append(("build", "SKIP", "tooling package.json (no app build script)"))

    # vue-tsc only when Vue toolchain likely present
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


def frontend_dir(root: Path) -> Path | None:
    """The folder that holds a web or Flutter frontend, or None for API-only projects."""
    for folder in (root, root / "frontend"):
        if (folder / "pubspec.yaml").is_file():
            return folder
        package = folder / "package.json"
        if not package.is_file():
            continue
        text = package.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'"(vue|vite|quasar|@quasar/app-vite|react|svelte|next|nuxt)"\s*:', text) or (folder / "src").is_dir():
            return folder
    return None


def _reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2):
            return True
    except urllib.error.HTTPError:
        return True
    except (OSError, ValueError):
        return False


@contextmanager
def dev_server(folder: Path):
    """Yield an error string ('' when ready) with DEV_SERVER_URL pointing at the app.

    Uses the caller's DEV_SERVER_URL / FLUTTER_WEB_URL. Otherwise it starts `npm run dev`
    on a free port (never a fixed one another session may be serving) and stops it after.
    """
    if os.environ.get("DEV_SERVER_URL") or os.environ.get("FLUTTER_WEB_URL"):
        yield ""
        return
    how = "start the app yourself and rerun with DEV_SERVER_URL=<url>"
    package = folder / "package.json"
    try:
        scripts = json.loads(package.read_text(encoding="utf-8")).get("scripts") or {}
    except (OSError, json.JSONDecodeError):
        scripts = {}
    if "dev" not in scripts or not shutil.which("npm"):
        yield f"no `npm run dev` to start: {how}"
        return
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [shutil.which("npm"), "run", "dev", "--", "--port", str(port), "--strictPort", "--host", "127.0.0.1"],
        cwd=folder,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.monotonic() + DEV_SERVER_TIMEOUT
        while not _reachable(url) and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        if not _reachable(url):
            yield f"`npm run dev` did not serve {url}: {how}"
            return
        os.environ["DEV_SERVER_URL"] = url
        try:
            yield ""
        finally:
            os.environ.pop("DEV_SERVER_URL", None)
    finally:
        if hasattr(os, "killpg"):
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_visual_checks(root: Path, rows: list[tuple[str, str, str]], *, require: bool) -> None:
    folder = frontend_dir(root)
    if folder is None:
        rows.append(("contrast-audit", "SKIP", "no frontend in this project"))
        return
    routes = routes_for_visual_audit(root)
    if not routes:
        rows.append(("contrast-audit", "SKIP", "no routes listed in .heyeddi/product.md"))
        return
    contrast_script = find_skill_script(root, "visual-auditor", "scripts/audit_contrast.py")
    if not contrast_script:
        st = "FAIL" if require else "SKIP"
        rows.append(("contrast-audit", st, "visual-auditor not installed"))
        return

    with dev_server(folder) as problem:
        if problem:
            rows.append(("contrast-audit", "FAIL" if require else "SKIP", problem))
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
            if st in {"FAIL", "SKIP"} and "playwright" in out.lower():
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
    pr_url: str | None = None,
    declined: list[dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any], int]:
    fail_count = sum(1 for _, st, _ in rows if st == "FAIL")
    skip_count = sum(1 for _, st, _ in rows if st == "SKIP")
    unverified_count = sum(1 for _, st, _ in rows if st == "UNVERIFIED")
    blocked = fail_count > 0
    lines = [
        "# Pre-merge Gate Report",
        "",
        f"- **PR:** {(f'[#{pr}]({pr_url})' if pr_url else f'#{pr}') if pr is not None else 'none (local)'}",
        f"- **Sign-off mode:** {'yes' if signoff else 'no'}",
        "",
        "| Check | Status | Summary |",
        "|-------|--------|---------|",
    ]
    for name, st, summary in rows:
        summary = summary.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {name} | {st} | {summary[:120]} |")
    lines.append("")
    if declined:
        lines += ["## Declined threads (left open, passed)", ""]
        for item in declined:
            where = f"{item.get('path')}:{item.get('line')}"
            reason = " ".join(str(item.get("reason")).split())
            lines.append(f"- [{where}]({item.get('url')}): {reason}")
        lines.append("")
    if emergency_used and signoff:
        lines.append(
            f"**Emergency skips used under sign-off:** {', '.join(emergency_used)} → not merge-ready"
        )
        lines.append("")
        blocked = True
    # UNVERIFIED = a check that needs GitHub could not run. Not a failure, but not merge-ready.
    unverified = unverified_count > 0 and not blocked
    overall = "BLOCKED" if blocked else ("UNVERIFIED" if unverified else "OK")
    if unverified:
        lines.append(
            "**Not merge-ready:** PR checks could not be verified (gh missing or logged out). "
            "Check CI and review threads by hand or with the GitHub MCP tools, or run `gh auth login` "
            "and re-run. Exit code 3."
        )
        lines.append("")
    lines.append(
        f"**Overall:** {overall} ({fail_count} failures, {unverified_count} unverified, {skip_count} skips)"
    )
    payload = {
        "ok": not blocked and not unverified,
        "overall": overall,
        "pr": pr,
        "pr_url": pr_url,
        "signoff": signoff,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "unverified_count": unverified_count,
        "emergency_skips": emergency_used,
        "declined_threads": declined or [],
        "checks": [{"name": n, "status": s, "summary": m} for n, s, m in rows],
    }
    code = 1 if blocked else (EXIT_DEGRADED if unverified else 0)
    return "\n".join(lines), payload, code


def run_cost_estimate(root: Path, approved: str | None) -> str:
    """Run the cost check. An approval already recorded in decisions.md is not appended again."""
    cost_args = ["--check"]
    decisions = root / ".heyeddi" / "docs" / "engineering" / "decisions.md"
    recorded = None
    if approved:
        cost_args += ["--approved", approved]
        if decisions.is_file():
            text = decisions.read_text(encoding="utf-8")
            if f"Approved by the user: {approved}" in text:
                recorded = text
    out = run_skill_script(root, "engineering-excellence", "scripts/estimate_change_cost.py", cost_args)
    if recorded is not None:
        decisions.write_text(recorded, encoding="utf-8")
    return out


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
    parser.add_argument("--skip-cost-estimate", action="store_true", help="Emergency only")
    parser.add_argument("--skip-backend", action="store_true", help="Emergency only")
    parser.add_argument("--skip-flutter", action="store_true")
    parser.add_argument("--skip-git-clean", action="store_true", help="Skip dirty/unpushed checks")
    parser.add_argument(
        "--cost-approved",
        default=None,
        metavar="REASON",
        help="The user's reason for accepting an over-budget change; passed to estimate_change_cost --approved",
    )
    args = parser.parse_args()
    root = resolve_project_root(args.project_root)
    declined: list[dict[str, Any]] = []
    rows: list[tuple[str, str, str]] = []

    # --pr N implies sign-off. --signoff auto-detects the open PR unless --no-pr.
    # Bare local runs (tests / everyday) do not auto-attach a PR.
    if args.pr is not None:
        pr = args.pr
        signoff = True
    elif args.signoff and not args.no_pr:
        pr = detect_pr_number(root, None)
        signoff = True
        if pr is None:
            # No PR found. With gh unusable that means "could not look", not "there is none".
            add_unverified_pr_rows(root, rows)
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
    if args.skip_cost_estimate:
        emergency_used.append("--skip-cost-estimate")

    if signoff and not args.skip_git_clean:
        run_git_clean_checks(root, rows)

    if signoff and pr is not None:
        run_pr_checks(root, pr, rows, declined)

    if not args.skip_setup_audit:
        out = run_skill_script(root, "heyeddi-setup", "scripts/verify_setup.py", ["--check"])
        st = status_from_output(out)
        if st == "PASS" and '"complete": false' in out:
            st = "FAIL"
        rows.append(("setup-audit", st, out[:200]))
    else:
        st = "FAIL" if signoff else "SKIP"
        rows.append(("setup-audit", st, "skipped via --skip-setup-audit"))

    run_context_secret_check(root, rows)

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

    if not args.skip_cost_estimate:
        out = run_cost_estimate(root, args.cost_approved)
        st = status_from_output(out)
        if st == "PASS" and '"ok": false' in out:
            st = "FAIL"
        rows.append(("cost-estimate", st, out[:200]))
    else:
        st = "FAIL" if signoff else "SKIP"
        rows.append(("cost-estimate", st, "skipped via --skip-cost-estimate"))

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

    md, payload, code = build_report(
        rows, pr=pr, signoff=signoff, emergency_used=emergency_used, pr_url=detect_pr_url(root, pr), declined=declined
    )
    if args.json:
        emit(md + "\n\n```json\n" + json.dumps(payload, indent=2) + "\n```")
    else:
        emit(md)
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main()
