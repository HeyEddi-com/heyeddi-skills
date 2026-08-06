"""Detect HeyEddi skills hub updates. Never auto-install."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_REPO = "HeyEddi-com/skills"
DEFAULT_INSTALL = "npx skills add HeyEddi-com/skills -a cursor -y --skill '*'"
THROTTLE = timedelta(hours=24)
ENV_KILL = "HEYEDDI_SKILLS_UPDATE_CHECK"
FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
SEMVER_PART = re.compile(r"^(\d+)")


def sync_state_path(project_root: Path) -> Path:
    return project_root / ".heyeddi" / "sync-state.json"


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_semver(value: str | None) -> tuple[int, ...]:
    if not value:
        return (0,)
    text = value.strip().lstrip("vV")
    parts: list[int] = []
    for chunk in text.split("."):
        match = SEMVER_PART.match(chunk)
        parts.append(int(match.group(1)) if match else 0)
    return tuple(parts) if parts else (0,)


def version_lt(left: str | None, right: str | None) -> bool:
    return parse_semver(left) < parse_semver(right)


def _parse_frontmatter(skill_md: Path) -> dict[str, str]:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        fields[key.strip()] = val.strip().strip("\"'")
    return fields


def _install_skills_roots(project_root: Path, orchestrator_scripts: Path) -> list[Path]:
    roots: list[Path] = []
    # Sibling install tree (…/skills or …/.agents/skills)
    if orchestrator_scripts.name == "scripts":
        roots.append(orchestrator_scripts.parent.parent)
    for candidate in (
        project_root / ".agents" / "skills",
        project_root / ".cursor" / "skills",
    ):
        if candidate.is_dir():
            roots.append(candidate)
    # Dedupe while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for root in roots:
        key = str(root.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(root.resolve())
    return out


def installed_hub_version(project_root: Path, orchestrator_scripts: Path) -> tuple[str | None, list[str]]:
    """Return (max product-version or version among installed skills, sample names)."""
    best: str | None = None
    samples: list[str] = []
    for skills_root in _install_skills_roots(project_root, orchestrator_scripts):
        if not skills_root.is_dir():
            continue
        for path in sorted(skills_root.iterdir()):
            skill_md = path / "SKILL.md"
            if not skill_md.is_file():
                continue
            meta = _parse_frontmatter(skill_md)
            ver = meta.get("product-version") or meta.get("version") or ""
            if not ver:
                continue
            name = meta.get("name") or path.name
            if best is None or version_lt(best, ver):
                best = ver
            if len(samples) < 5:
                samples.append(f"{name}@{ver}")
    return best, samples


def registry_hub_version(hub_root: Path | None) -> str | None:
    if hub_root is None:
        return None
    registry = hub_root / "skills-registry.json"
    if not registry.is_file():
        return None
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    ver = data.get("version")
    return str(ver) if ver else None


def load_sync_state(project_root: Path) -> dict[str, Any]:
    path = sync_state_path(project_root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_sync_state(project_root: Path, updates: dict[str, Any]) -> Path:
    heyeddi = project_root / ".heyeddi"
    heyeddi.mkdir(parents=True, exist_ok=True)
    path = sync_state_path(project_root)
    state = load_sync_state(project_root)
    state.update(updates)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def update_check_enabled(state: dict[str, Any]) -> tuple[bool, str | None]:
    env = os.environ.get(ENV_KILL, "").strip().lower()
    if env in {"0", "false", "off", "no"}:
        return False, f"env {ENV_KILL}={env}"
    if state.get("skills_update_check") is False:
        return False, "sync-state skills_update_check=false"
    return True, None


def throttled(state: dict[str, Any], *, force: bool) -> bool:
    if force:
        return False
    raw = state.get("skills_update_last_check_at")
    if not isinstance(raw, str) or not raw:
        return False
    try:
        last = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(UTC) - last < THROTTLE


def fetch_latest_via_gh(repo: str, cwd: Path) -> tuple[str | None, str | None]:
    """Return (version, error). Uses gh only (no urllib)."""
    executable = shutil.which("gh")
    if executable is None:
        return None, "gh CLI not found"
    try:
        result = subprocess.run(
            [executable, "api", f"repos/{repo}/releases/latest", "--jq", ".tag_name"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return None, "gh api timed out"
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "gh api failed").strip()[:200]
        return None, err
    tag = (result.stdout or "").strip()
    if not tag:
        return None, "empty release tag"
    return tag.lstrip("vV"), None


def build_user_block(*, installed: str, latest: str, install_cmd: str, pin_cmd: str) -> str:
    return "\n".join(
        [
            "### Skills update available",
            "",
            f"Installed hub version: **{installed}**. Latest: **{latest}**.",
            "",
            "Skills change agent behavior. Do **not** auto-update.",
            "",
            "**Approve update?** Reply `update` / `yes` to run the install command, or `skip` to dismiss this version.",
            "",
            "Prompt:",
            "",
            f"`{install_cmd}`",
            "",
            f"Pinned: `{pin_cmd}`",
            "",
            "Kill switch (disable checks): set `.heyeddi/sync-state.json` → "
            '`"skills_update_check": false` or env '
            f"`{ENV_KILL}=off`.",
        ]
    )


def check_skills_update(
    project_root: Path,
    *,
    orchestrator_scripts: Path,
    hub_root: Path | None = None,
    latest_override: str | None = None,
    repo: str = DEFAULT_REPO,
    force: bool = False,
    dismiss: bool = False,
    disable: bool = False,
    enable: bool = False,
) -> dict[str, Any]:
    """Compare installed hub version to latest. Never installs."""
    state = load_sync_state(project_root)

    if disable:
        path = save_sync_state(
            project_root,
            {
                "skills_update_check": False,
                "skills_update_disabled_at": now_iso(),
            },
        )
        return {
            "status": "disabled",
            "update_available": False,
            "ask_user": False,
            "sync_state": str(path.relative_to(project_root)),
            "note": "Update checks off. Re-enable with check_skills_update --enable.",
        }

    if enable:
        path = save_sync_state(
            project_root,
            {
                "skills_update_check": True,
                "skills_update_enabled_at": now_iso(),
            },
        )
        state = load_sync_state(project_root)
        # fall through to run a check

    enabled, reason = update_check_enabled(state)
    if not enabled:
        return {
            "status": "skipped",
            "reason": reason,
            "update_available": False,
            "ask_user": False,
        }

    installed, samples = installed_hub_version(project_root, orchestrator_scripts)
    registry_ver = registry_hub_version(hub_root)

    if dismiss:
        target = latest_override or state.get("skills_update_latest_seen") or registry_ver
        if not target:
            return {
                "status": "error",
                "error": "nothing to dismiss: pass --latest or run a check first",
                "update_available": False,
                "ask_user": False,
            }
        path = save_sync_state(
            project_root,
            {
                "skills_update_dismissed_version": str(target).lstrip("vV"),
                "skills_update_dismissed_at": now_iso(),
                "installed_hub_version": installed,
            },
        )
        return {
            "status": "dismissed",
            "dismissed_version": str(target).lstrip("vV"),
            "update_available": False,
            "ask_user": False,
            "sync_state": str(path.relative_to(project_root)),
        }

    if throttled(state, force=force):
        return {
            "status": "throttled",
            "reason": f"last check within {int(THROTTLE.total_seconds() // 3600)}h (use --force)",
            "update_available": False,
            "ask_user": False,
            "installed_hub_version": installed,
            "last_check_at": state.get("skills_update_last_check_at"),
        }

    source = "override"
    latest: str | None = None
    fetch_error: str | None = None
    if latest_override:
        latest = latest_override.lstrip("vV")
    else:
        latest, fetch_error = fetch_latest_via_gh(repo, project_root)
        source = "github_release"
        if latest is None and registry_ver:
            latest = registry_ver
            source = "local_registry"
            fetch_error = None

    path = save_sync_state(
        project_root,
        {
            "skills_update_last_check_at": now_iso(),
            "skills_update_latest_seen": latest,
            "installed_hub_version": installed,
            "skills_update_check_source": source if latest else "failed",
        },
    )

    if latest is None:
        return {
            "status": "skipped",
            "reason": fetch_error or "could not determine latest version",
            "update_available": False,
            "ask_user": False,
            "installed_hub_version": installed,
            "sync_state": str(path.relative_to(project_root)),
        }

    dismissed = state.get("skills_update_dismissed_version")
    if isinstance(dismissed, str) and dismissed.lstrip("vV") == latest:
        return {
            "status": "dismissed",
            "update_available": True,
            "ask_user": False,
            "installed_hub_version": installed,
            "latest_hub_version": latest,
            "note": f"User dismissed {latest}. Pass --force after clearing dismissed, or --enable.",
            "sync_state": str(path.relative_to(project_root)),
        }

    if installed is None:
        return {
            "status": "unknown_install",
            "update_available": False,
            "ask_user": False,
            "latest_hub_version": latest,
            "note": "No installed skill product-version found under .agents/skills or skill tree.",
            "sync_state": str(path.relative_to(project_root)),
        }

    available = version_lt(installed, latest)
    pin_cmd = f"npx skills add https://github.com/{repo}/tree/v{latest} -a cursor -y --skill '*'"
    payload: dict[str, Any] = {
        "status": "update_available" if available else "up_to_date",
        "update_available": available,
        "ask_user": available,
        "installed_hub_version": installed,
        "latest_hub_version": latest,
        "source": source,
        "registry_hub_version": registry_ver,
        "sample_installed": samples,
        "never_auto_update": True,
        "install_command": DEFAULT_INSTALL,
        "pinned_install_command": pin_cmd,
        "sync_state": str(path.relative_to(project_root)),
    }
    if available:
        payload["user_block"] = build_user_block(
            installed=installed,
            latest=latest,
            install_cmd=DEFAULT_INSTALL,
            pin_cmd=pin_cmd,
        )
        payload["agent_instruction"] = (
            "Ask the user to approve before running any install command. "
            "On skip: check_skills_update --dismiss --latest "
            f"{latest}. Never run npx skills add without explicit approval."
        )
    save_sync_state(
        project_root,
        {"skills_update_last_result": payload["status"]},
    )
    return payload
