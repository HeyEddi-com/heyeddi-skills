"""Shared CLI helpers."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def emit(data: Any) -> None:
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, indent=2))


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def resolve_project_root(arg: str | None, *, auto_sync: bool = True) -> Path:
    root = Path(arg or os.environ.get("PROJECT_ROOT", ".")).resolve()
    if not root.is_dir():
        fail(f"project_root not found: {root}")
    if auto_sync:
        try:
            from _auto_sync import ensure_heyeddi  # noqa: PLC0415

            ensure_heyeddi(root)
        except Exception as exc:  # noqa: BLE001: never block skill tools on sync
            print(f"heyeddi auto-sync skipped: {exc}", file=sys.stderr)
    return root


def run_command(
    cmd: list[str],
    cwd: Path,
    timeout: int = 600,
    *,
    stdin_text: str | None = None,
) -> str:
    """Run a fixed argv command without a shell.

    The executable is resolved to an absolute path via ``shutil.which`` so the
    call never depends on a relative PATH lookup, and ``shell`` is always off —
    there is no string interpolation into a shell.

    Pass ``stdin_text`` for tools that read ``--input -`` / ``@-`` (e.g. multiline
    GitHub comment bodies via ``gh api --input -``).
    """
    if not cmd:
        return "[error] empty command"
    executable = shutil.which(cmd[0])
    if executable is None:
        return f"[error] command not found: {cmd[0]}"
    try:
        result = subprocess.run(
            [executable, *cmd[1:]],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            input=stdin_text,
        )
    except subprocess.TimeoutExpired:
        return f"[error] command timed out after {timeout}s: {cmd[0]}"

    # gh 2.105+ writes hints (for example "gh event listen") to stderr on success.
    # Callers parse gh stdout as JSON or a SHA, so drop stderr when gh succeeds.
    if result.returncode == 0 and Path(cmd[0]).name == "gh":
        output = result.stdout or ""
    else:
        output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return f"[exit {result.returncode}]\n{output}".strip()
    return output.strip() or "(success, no output)"


# --- gh is optional ---------------------------------------------------------------------
# Scripts that talk to GitHub call gh_status() first. When gh is missing or logged out they
# call degraded(): a structured result and exit 3. That is not a crash (traceback), not a
# pass (exit 0) and not a real failure (exit 1), so a caller can tell "could not check"
# from "checked and it is wrong".

EXIT_DEGRADED = 3

_GH_HINT = (
    "Install the GitHub CLI (https://cli.github.com) and run `gh auth login`, "
    "or set GH_TOKEN. The GitHub MCP tools also work for this step."
)


def gh_status(cwd: Path | None = None) -> dict[str, Any]:
    """Say whether the gh CLI is usable: state is ok, missing, unauthenticated or unavailable.

    Uses `gh auth token`, which needs no network. The token is discarded, never returned.
    """
    exe = shutil.which("gh")
    if exe is None:
        return {"ok": False, "state": "missing", "reason": "gh CLI not found on PATH", "hint": _GH_HINT}
    try:
        result = subprocess.run(
            [exe, "auth", "token"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=20,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "state": "unavailable", "reason": f"gh did not respond: {exc}", "hint": _GH_HINT}
    if result.returncode == 0 and (result.stdout or "").strip():
        return {"ok": True, "state": "ok", "reason": "", "hint": ""}
    return {
        "ok": False,
        "state": "unauthenticated",
        "reason": "gh is installed but not logged in",
        "hint": "Run `gh auth login`, or set GH_TOKEN. The GitHub MCP tools also work for this step.",
    }


def degraded(step: str, status: dict[str, Any], *, manual: list[str], **extra: Any) -> None:
    """Report that a GitHub step could not run, say how to do it by hand, and exit 3."""
    emit(
        {
            "status": "degraded",
            "step": step,
            "gh": {k: status.get(k) for k in ("state", "reason", "hint")},
            "manual": manual,
            **extra,
        }
    )
    sys.exit(EXIT_DEGRADED)
