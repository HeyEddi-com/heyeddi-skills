"""Cross-skill coherence: one working agreement, no stray stop rules, live central links.

Every release before v3.8.21 added an always-on rule that ended in "ask the user",
and agents stopped mid-task. These tests keep the agreement in one place
(`skills/heyeddi/templates/always-on/AGENTS.section.md` plus `reference/autonomy.md`
and `reference/testing.md`) and fail when a skill adds a new stop.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
HEYEDDI_REF = SKILLS / "heyeddi" / "reference"
TEMPLATE = SKILLS / "heyeddi" / "templates" / "always-on" / "AGENTS.section.md"
RULE = SKILLS / "heyeddi" / "templates" / "always-on" / "heyeddi-always-on.mdc"

STOP = re.compile(
    r"end the turn|end the response|stop and (ask|wait)|waits? for (explicit|the user|user|choice|a–e|approval)"
    r"|only on their yes|ask the user|copies the \*\*prompt|confirm first",
    re.IGNORECASE,
)
NEGATED = re.compile(r"\b(not|never|no)\b[^.]{0,40}$", re.IGNORECASE)

# Files allowed to stop, and why. Each must scope the stop to a request that asks for it.
ALLOWED_STOPS = {
    "heyeddi/reference/autonomy.md": "defines the only pauses",
    "heyeddi/templates/always-on/AGENTS.section.md": "says never end the turn",
    "heyeddi/templates/always-on/heyeddi-always-on.mdc": "says never end the turn",
    "taste-penpot/SKILL.md": "identity gate, design requests only",
    "taste-penpot/references/identity-gate.md": "identity gate, design requests only",
    "taste-penpot/context/VOCABULARY.md": "identity gate, design requests only",
    "heyeddi-design/reference/shape.md": "brief confirmation, design requests only",
    "heyeddi-design/reference/design-team.md": "identity pick, design requests only",
    "heyeddi-setup/SKILL.md": "setup interview runs only when the user asks for setup",
    "heyeddi/SKILL.md": "router summary of the identity gate, design requests only",
}


def _skill_docs() -> list[Path]:
    return [
        p
        for p in SKILLS.rglob("*")
        if p.suffix in {".md", ".mdc"} and p.is_file() and p.name != "PROSE_ANTI_SLOP.md" and "third-party" not in p.parts
    ]


def test_no_new_stop_rules_outside_the_allowlist() -> None:
    offenders: list[str] = []
    for path in _skill_docs():
        rel = path.relative_to(SKILLS).as_posix()
        if rel in ALLOWED_STOPS:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for hit in STOP.finditer(line):
                if NEGATED.search(line[: hit.start()]):
                    continue
                offenders.append(f"{rel}:{number}: {line.strip()[:100]}")
    assert not offenders, (
        "New stop or ask rule in a skill. Route it through @heyeddi reference/autonomy.md "
        "(decide, record, keep going) or add it to ALLOWED_STOPS with a reason:\n" + "\n".join(offenders)
    )


def test_allowed_stops_are_scoped_to_design_or_explicit_requests() -> None:
    for rel, reason in ALLOWED_STOPS.items():
        text = (SKILLS / rel).read_text(encoding="utf-8")
        if "design requests only" in reason:
            assert "build request" in text.lower(), f"{rel} stops without a build-request path"


def test_agreement_lives_in_the_template_and_points_at_central_refs() -> None:
    for path in (TEMPLATE, RULE):
        body = path.read_text(encoding="utf-8")
        for item in ("**Autonomy**", "**Setup**", "**Permissions**", "**Tests**", "**Engineering**", "**Cost**", "**Prose and links**", "**Ship**"):
            assert item in body, f"{path.name} missing {item}"
        assert "reference/autonomy.md" in body and "reference/testing.md" in body
        assert "check_permission.py" in body
        assert "Not strict TDD" not in body
        assert "full URL" in body and "gh pr view <n> --json url" in body, f"{path.name} lost the link rule"
    assert (HEYEDDI_REF / "autonomy.md").is_file()
    assert (HEYEDDI_REF / "testing.md").is_file()


def test_template_and_cursor_rule_carry_the_same_checklist() -> None:
    def items(text: str) -> list[str]:
        return [line for line in text.splitlines() if re.match(r"^\d+\. \*\*", line)]

    assert items(TEMPLATE.read_text(encoding="utf-8")) == items(RULE.read_text(encoding="utf-8"))


def test_repo_agents_md_matches_the_template() -> None:
    template = TEMPLATE.read_text(encoding="utf-8").strip()
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert template in agents, "AGENTS.md is stale: run ensure_always_on_agents.py --project-root ."


def test_heyeddi_reference_links_resolve() -> None:
    link = re.compile(r"@heyeddi`?\s*(?:→\s*)?`reference/([\w-]+\.md)`")
    broken: list[str] = []
    for path in [*_skill_docs(), ROOT / "AGENTS.md", *(ROOT / "docs").glob("*.md")]:
        for name in link.findall(path.read_text(encoding="utf-8")):
            if not (HEYEDDI_REF / name).is_file():
                broken.append(f"{path.relative_to(ROOT)} -> reference/{name}")
    assert not broken, "Broken @heyeddi reference links:\n" + "\n".join(broken)


def test_task_complete_sections_are_identical_except_the_skill_name() -> None:
    heading = "## When the task is complete: suggest next skills"
    bodies: dict[str, str] = {}
    for skill_md in SKILLS.glob("*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        if heading not in text:
            continue
        section = text.split(heading, 1)[1].split("\n## ", 1)[0]
        name = skill_md.parent.name
        bodies[name] = section.replace(f"--current-skill {name} ", "--current-skill <skill> ")
    assert len(set(bodies.values())) == 1, sorted(bodies)
    assert "run it now" in next(iter(bodies.values()))


def test_merge_rule_is_one_sentence_everywhere() -> None:
    old = re.compile(r"(requires|needs|without) \*\*authorize merge\*\*", re.IGNORECASE)
    stale = [
        str(p.relative_to(ROOT))
        for p in _skill_docs()
        if old.search(p.read_text(encoding="utf-8")) and "agent.permissions.merge" not in p.read_text(encoding="utf-8")
    ]
    assert not stale, "Merge rule restated without the policy: " + ", ".join(stale)
