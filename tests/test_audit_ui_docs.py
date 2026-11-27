"""Stack and UI skill text: runnable commands, real APIs, existing files."""
from __future__ import annotations

import re
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "skills"
OWNED = (
    "aura-design-tokens",
    "backend-type-bridger",
    "cli-interface-design",
    "composable-patterns",
    "dart-type-bridger",
    "fancy-ui-craft",
    "flutter-engineering",
    "flutter-patterns",
    "layout-morph",
    "motion-physics",
    "primevue-aura",
    "primevue-openprops-architect",
    "project-engineering",
    "quasar-foundation",
    "vue-design-system",
)


def _docs() -> list[Path]:
    return [
        path
        for skill in OWNED
        for path in (SKILLS / skill).rglob("*.md")
        if path.name != "PROSE_ANTI_SLOP.md" and "third-party" not in path.parts
    ]


def _offenders(pattern: str) -> list[str]:
    return [str(p.relative_to(SKILLS)) for p in _docs() if re.search(pattern, p.read_text())]


def test_script_commands_run_from_the_project_root() -> None:
    assert _offenders(r"(?m)(^\s*|`)python3? scripts/") == []


def test_no_removed_or_unapproved_instructions() -> None:
    for pattern in (
        r"quasar build",
        r"<q-bottom-sheet>",
        r"plugins: \{[^}]*Morph",
        r"PascalCase path",
        r"design-tokens\.css",
        r"after the user approves",
        r"without team approval",
        r"eval agent turns",
        r"run setup until pass",
    ):
        assert _offenders(pattern) == [], pattern


def test_relative_references_exist() -> None:
    missing = []
    for path in _docs():
        for target in re.findall(r"`((?:\.\./)+docs/[\w./-]+\.md)`", path.read_text()):
            if not (path.parent / target).is_file():
                missing.append(f"{path.relative_to(SKILLS)}: {target}")
    skill = SKILLS / "flutter-engineering"
    listed = (skill / "SKILL.md").read_text().split("## References")[1].split("\n## ")[0]
    for target in re.findall(r"(?m)^- `(reference/[\w-]+\.md)`", listed):
        if not (skill / target).is_file():
            missing.append(f"flutter-engineering/SKILL.md: {target}")
    assert missing == []
