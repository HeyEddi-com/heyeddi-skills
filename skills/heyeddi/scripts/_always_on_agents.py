"""Install thin always-on AGENTS.md + Cursor alwaysApply rule into a project.

Skills stay playbooks/scripts. These files inject the short checklist every chat.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

START = "<!-- heyeddi-always-on:start -->"
END = "<!-- heyeddi-always-on:end -->"
_MARKER_BLOCK = re.compile(
    re.escape(START) + r".*?" + re.escape(END),
    re.DOTALL,
)

_TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "always-on"


def _read_template(name: str) -> str:
    path = _TEMPLATES / name
    if not path.is_file():
        raise FileNotFoundError(f"missing always-on template: {path}")
    return path.read_text(encoding="utf-8").strip() + "\n"


def _merge_agents_md(existing: str | None, section: str) -> str:
    section = section.strip() + "\n"
    if not existing or not existing.strip():
        return "# Agent instructions\n\n" + section
    if _MARKER_BLOCK.search(existing):
        return _MARKER_BLOCK.sub(section.rstrip(), existing).rstrip() + "\n"
    # Preserve user AGENTS.md; append managed block once.
    return existing.rstrip() + "\n\n" + section


def ensure_always_on_agents(project_root: Path, *, force_rule: bool = True) -> dict[str, Any]:
    """Write/update root AGENTS.md managed section + `.cursor/rules/heyeddi-always-on.mdc`."""
    root = project_root.resolve()
    written: list[str] = []
    skipped: list[str] = []

    agents_section = _read_template("AGENTS.section.md")
    agents_path = root / "AGENTS.md"
    before = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else None
    after = _merge_agents_md(before, agents_section)
    if before != after:
        agents_path.write_text(after, encoding="utf-8")
        written.append("AGENTS.md")
    else:
        skipped.append("AGENTS.md")

    rule_body = _read_template("heyeddi-always-on.mdc")
    rules_dir = root / ".cursor" / "rules"
    rule_path = rules_dir / "heyeddi-always-on.mdc"
    if rule_path.is_file() and rule_path.read_text(encoding="utf-8") == rule_body and not force_rule:
        skipped.append(".cursor/rules/heyeddi-always-on.mdc")
    else:
        rules_dir.mkdir(parents=True, exist_ok=True)
        if (not rule_path.is_file()) or force_rule or rule_path.read_text(encoding="utf-8") != rule_body:
            rule_path.write_text(rule_body, encoding="utf-8")
            written.append(".cursor/rules/heyeddi-always-on.mdc")
        else:
            skipped.append(".cursor/rules/heyeddi-always-on.mdc")

    return {
        "ok": True,
        "written": written,
        "skipped": skipped,
        "agents_md": "AGENTS.md",
        "cursor_rule": ".cursor/rules/heyeddi-always-on.mdc",
    }
