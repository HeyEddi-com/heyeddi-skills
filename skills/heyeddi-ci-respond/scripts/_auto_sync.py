"""Ensure `.heyeddi/` exists via filesystem scan only (no dynamic code loading)."""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_ENSURED: set[str] = set()
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(skill_md: Path) -> dict[str, str]:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = _FRONTMATTER.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        fields[key.strip()] = val.strip().strip("\"'")
    return fields


def _install_skills_root(here: Path) -> Path | None:
    """Parent of skill folders: …/skills or …/.agents/skills."""
    here = here.resolve()
    # …/<skill>/scripts → …/<skills-root>
    if here.name == "scripts":
        return here.parent.parent
    return None


def _scan_sibling_skills(skills_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not skills_root.is_dir():
        return entries
    for path in sorted(skills_root.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        skill_md = path / "SKILL.md"
        if not skill_md.is_file():
            continue
        meta = _parse_frontmatter(skill_md)
        name = meta.get("name") or path.name
        entries.append(
            {
                "name": name,
                "folder": path.name,
                "description": (meta.get("description") or "")[:240],
                "version": meta.get("version") or "",
                "installed": True,
                "at": f"@{name}",
            }
        )
    return entries


def _write_minimal_index(project_root: Path, skills_root: Path) -> dict[str, Any]:
    heyeddi = project_root / ".heyeddi"
    heyeddi.mkdir(parents=True, exist_ok=True)
    skills = _scan_sibling_skills(skills_root)
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalog: dict[str, Any] = {
        "index_version": 1,
        "generated_at": generated,
        "generator": "heyeddi-auto-sync-minimal",
        "skill_count": len(skills),
        "installed_count": len(skills),
        "skills": skills,
        "note": "Minimal index from install-tree SKILL.md scan. Run @heyeddi-orchestrator sync for full catalog.",
    }
    json_path = heyeddi / "skills-index.json"
    json_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        "# HeyEddi skills index",
        "",
        f"Generated: `{generated}` (minimal auto-sync)",
        "",
        "| Skill | Version |",
        "|-------|---------|",
    ]
    for entry in skills:
        md_lines.append(f"| `{entry['name']}` | {entry.get('version') or ' - '} |")
    md_lines.append("")
    (heyeddi / "skills-index.md").write_text("\n".join(md_lines), encoding="utf-8")
    return {
        "ok": True,
        "written": [".heyeddi/skills-index.json", ".heyeddi/skills-index.md"],
        "skill_count": len(skills),
        "generated_at": generated,
    }


def ensure_heyeddi(
    project_root: Path,
    *,
    refresh_index: bool = True,
    once_per_process: bool = True,
) -> dict[str, Any] | None:
    """Create `.heyeddi/` and a minimal skills index when missing."""
    key = str(project_root.resolve())
    if once_per_process and key in _ENSURED:
        return None

    if once_per_process:
        _ENSURED.add(key)

    heyeddi = project_root / ".heyeddi"
    heyeddi.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"status": "ok"}

    index_path = heyeddi / "skills-index.json"
    if refresh_index and not index_path.is_file():
        skills_root = _install_skills_root(Path(__file__).resolve().parent)
        if skills_root is None:
            return {"status": "skipped", "reason": "cannot resolve install skills root"}
        result.update(_write_minimal_index(project_root, skills_root))
    return result
