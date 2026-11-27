"""PR and CI skill text must not stop an agent or contradict the working agreement."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", ["heyeddi-pr-respond", "heyeddi-ci-fails", "heyeddi-pr-review", "pre-merge-gate"])
def test_agent_can_invoke_pipeline_skills(skill: str) -> None:
    assert "disable-model-invocation" not in _read(f"skills/{skill}/SKILL.md").split("---")[1]


def test_ci_pack_ships_what_its_rules_call() -> None:
    pack = set(json.loads(_read("packs/heyeddi-ci-skills.json"))["skills"])
    needed = {"heyeddi", "heyeddi-setup", "heyeddi-local-first", "pre-merge-gate", "engineering-excellence", "heyeddi-product"}
    assert needed <= pack
    for name in pack:
        assert (ROOT / "plugins" / "heyeddi-ci-skills" / "skills" / name / "SKILL.md").is_file(), name


def test_merge_rule_is_not_garbled() -> None:
    bad = re.compile(r"unless only a production merge|Only merge can need a question")
    hits = [str(p.relative_to(ROOT)) for p in SKILLS.rglob("*.md") if bad.search(p.read_text(encoding="utf-8"))]
    assert not hits


@pytest.mark.parametrize(
    ("rel", "gone"),
    [
        ("docs/pr-workflows.md", r"pr-<N>-tracking|pr-<N>-replies|\*\*quote-reply\*\*|check_doc_drift"),
        ("docs/design-excellence.md", r"\u2014 wait\b|wait for A"),
        ("docs/clarify-before-act.md", r"Irreversible stack choice|conflicts with `product.md`"),
        ("docs/skills-roadmap.md", r"disable-model-invocation: true` \u2014 QA runs"),
        ("skills/heyeddi-pr-respond/context/EXAMPLES.md", r"\.heyeddi/docs/pr-42"),
        ("skills/heyeddi-pr-respond/reference/subagents.md", r"pr-<N>-replies\.md|posted\.json"),
        ("skills/heyeddi-pr-respond/reference/workflow.md", r"when your team requires"),
        ("skills/heyeddi-pr-review/reference/subagents.md", r"pre_merge_gate|check_doc_drift|Product fit"),
        ("skills/heyeddi-ci-config/SKILL.md", r"ask once|ask before|confirm intent|Tell the user to commit"),
        ("skills/heyeddi-ci-config/context/ANTI_PATTERNS.md", r"confirm if intent"),
        ("skills/heyeddi-ci-fails/context/EXAMPLES.md", r"Do not merge"),
        ("skills/heyeddi-ci-guide/context/VOCABULARY.md", r"`ask` \(the default\)"),
        ("scripts/publish-ci-pack-repo.sh", r"PLACEHOLDER|fail-closed|default asks for"),
        ("README.md", r"diff, product, docs, engineering, tests"),
        ("docs/team-cheat-sheet.md", r"committed diff, product, docs, eng, tests"),
    ],
)
def test_stale_text_is_gone(rel: str, gone: str) -> None:
    assert not re.search(gone, _read(rel)), rel


@pytest.mark.parametrize("rel", ["skills/heyeddi-ci-fails/SKILL.md", "skills/heyeddi-pr-respond/SKILL.md"])
def test_pipelines_run_to_green_and_merge(rel: str) -> None:
    text = _read(rel)
    for needed in ("gh pr checks <N> --watch", "gh run view", "--log-failed", "gh run rerun",
                   "pre_merge_gate.py --signoff", "gh pr merge <N>"):
        assert needed in text, f"{rel}: {needed}"


def test_replies_examples_pass_the_draft() -> None:
    text = _read("skills/heyeddi-pr-respond/context/EXAMPLES.md")
    calls = [l for l in text.splitlines() if re.search(r"python .*(post_thread_replies|verify_response)\.py", l)]
    assert calls and all("--replies-text" in line for line in calls)


def test_out_of_scope_findings_are_fixed_and_declines_are_marked() -> None:
    workflow = _read("skills/heyeddi-pr-respond/reference/workflow.md")
    assert "its own branch and PR" in workflow
    skill = _read("skills/heyeddi-pr-respond/SKILL.md")
    assert "**Declined:** <reason>" in skill
    assert "**Declined:**" in _read("skills/pre-merge-gate/SKILL.md")
