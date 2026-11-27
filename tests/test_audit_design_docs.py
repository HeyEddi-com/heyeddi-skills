"""Doc contracts for build runs: self-invocable skills, backlog loop, real script names."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SELF_INVOKED = ("heyeddi-handoff", "design-handoff-flutter", "ux-flow-auditor", "design-system-generalizer")


def _text(rel: str) -> str:
    return (SKILLS / rel).read_text(encoding="utf-8")


def test_pipeline_skills_can_be_invoked_by_the_agent() -> None:
    for name in SELF_INVOKED:
        assert "disable-model-invocation" not in _text(f"{name}/SKILL.md"), name


def test_bootstrap_does_not_disable_them_again() -> None:
    source = (ROOT / "scripts" / "bootstrap-all-skills.py").read_text(encoding="utf-8")
    blocks = re.split(r"\ndef define_", source)
    for name in (*SELF_INVOKED, "visual-auditor", "heyeddi-design"):
        for block in blocks:
            if f'name = "{name}"' in block:
                assert "disable=True" not in block, name


def test_task_complete_section_runs_the_backlog() -> None:
    heading = "## When the task is complete: suggest next skills"
    for skill_md in SKILLS.glob("*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        if heading in text:
            section = text.split(heading, 1)[1].split("\n## ", 1)[0]
            assert "backlog.py --project-root . next" in section, skill_md.parent.name
            assert "Otherwise put" not in section, skill_md.parent.name


def test_product_skill_has_the_backlog_loop() -> None:
    skill = _text("heyeddi-product/SKILL.md")
    assert "## Backlog loop" in skill
    for needle in ("backlog.py", "pre-merge-gate", "done", "production"):
        assert needle in skill
    assert "NEVER implement fixes" not in _text("heyeddi-product/context/ANTI_PATTERNS.md")


def test_visual_auditor_examples_name_real_scripts() -> None:
    for name in re.findall(r"scripts/(\w+\.py)", _text("visual-auditor/context/EXAMPLES.md")):
        assert (SKILLS / "visual-auditor" / "scripts" / name).is_file(), name


def test_penpot_server_is_the_heyeddi_one() -> None:
    for rel in ("heyeddi-design/reference/design-team.md", "heyeddi-handoff/SKILL.md"):
        assert "@heyeddi/penpot-mcp-server" in _text(rel), rel
        assert "only connection is `@zcubekr" not in _text(rel)
        assert "`@zcubekr/penpot-mcp-server` only" not in _text(rel)


def test_taste_has_no_extra_install_question_and_gate_d_has_a_build_path() -> None:
    assert "ask once and install" not in _text("taste-penpot/SKILL.md")
    gates = _text("taste-penpot/references/layout-hard-gates.md")
    assert gates.count("Build request with a blocked export") == 1
    assert "build-request fallback" in gates.split("## Done checklist")[1]
