#!/usr/bin/env python3
"""Manage the 'task complete → next skill' section on pipeline SKILL.md files."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

# Skills that own a user-facing workflow end (not utility/guardrail tools).
PIPELINE_SKILLS = {
    "heyeddi-intake",
    "heyeddi-product",
    "heyeddi",
    "heyeddi-design",
    "heyeddi-handoff",
    "design-handoff-flutter",
    "project-engineering",
    "flutter-engineering",
    "visual-auditor",
    "pre-merge-gate",
    "heyeddi-pr-review",
    "heyeddi-pr-respond",
}

OLD_HEADINGS = (
    "## End every turn — next skill",
    "## End every turn - next skill",
)
NEW_HEADING = "## When the task is complete: suggest next skills"
ORCH = ".agents/skills/heyeddi/scripts/suggest_next_skill.py"


def section_for(skill_name: str) -> str:
    return f"""
{NEW_HEADING}

When you have **finished the user's request** for this skill (not after every tool call or subagent phase), suggest what to run next:

1. Run:

   ```bash
   python {ORCH} --current-skill {skill_name} --project-root .
   ```

   Add `--route /path` if you worked a specific route.

2. Include the script's **`### Next step`** block in your **final** reply. The user copies the **Prompt** line into chat (e.g. `@heyeddi-design craft /settings`).

Pass `--mode shape` (or `craft`, `audit`, etc.) when you know which sub-command just finished.

See `@heyeddi` → `reference/next-skill-handoff.md`.
"""


def strip_old_sections(text: str) -> str:
    for heading in OLD_HEADINGS:
        if heading in text:
            text = re.sub(
                rf"{re.escape(heading)}[\s\S]*?(?=\n## |\Z)",
                "",
                text,
                count=1,
            )
    if NEW_HEADING in text:
        text = re.sub(
            rf"{re.escape(NEW_HEADING)}[\s\S]*?(?=\n## |\Z)",
            "",
            text,
            count=1,
        )
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def patch_pipeline_skill(path: Path, skill_name: str) -> None:
    text = strip_old_sections(path.read_text(encoding="utf-8"))
    if "\n## Related\n" in text:
        text = text.replace("\n## Related\n", section_for(skill_name) + "\n## Related\n", 1)
    else:
        text = text.rstrip() + section_for(skill_name) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        name = skill_dir.name
        if name in PIPELINE_SKILLS:
            patch_pipeline_skill(skill_md, name)
            print(f"pipeline: {name}")
        else:
            cleaned = strip_old_sections(skill_md.read_text(encoding="utf-8"))
            skill_md.write_text(cleaned, encoding="utf-8")
            print(f"stripped: {name}")


if __name__ == "__main__":
    main()
