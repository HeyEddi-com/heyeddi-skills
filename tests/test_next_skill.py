"""Tests for suggest_next_skill handoff."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "heyeddi-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _next_skill import suggest_next_skill  # noqa: E402


def test_default_chain_handoff_to_engineering(tmp_path: Path) -> None:
    result = suggest_next_skill(tmp_path, current_skill="heyeddi-handoff", current_route="/settings")
    assert result["next"]["skill"] == "engineering-excellence"
    assert "@engineering-excellence" in result["next"]["prompt"]
    assert "/settings" in result["next"]["prompt"]
    assert "**Prompt:**" in result["user_block"]
    assert "python scripts/" not in result["user_block"]


def test_default_chain_engineering_to_visual(tmp_path: Path) -> None:
    result = suggest_next_skill(
        tmp_path,
        current_skill="engineering-excellence",
        current_route="/settings",
    )
    assert result["next"]["skill"] == "visual-auditor"
    assert "@visual-auditor" in result["next"]["prompt"]


def test_design_shape_mode_suggests_handoff(tmp_path: Path) -> None:
    """After shape, stack implementer (vue default) is suggested — not in-skill craft."""
    result = suggest_next_skill(
        tmp_path,
        current_skill="heyeddi-design",
        current_route="/dashboard",
        current_mode="shape",
    )
    assert result["next"]["skill"] == "heyeddi-handoff"
    assert "implement" in result["next"]["prompt"]
    assert "/dashboard" in result["next"]["prompt"]


def test_routing_prefers_next_route(tmp_path: Path) -> None:
    intake = tmp_path / ".heyeddi" / "docs" / "intake"
    intake.mkdir(parents=True)
    routing = {
        "routes": [
            {"route": "/dashboard", "skill": "heyeddi-design", "mode": "craft", "feature": "dash"},
            {"route": "/settings", "skill": "heyeddi-handoff", "feature": "settings"},
        ]
    }
    (intake / "skill-routing.json").write_text(json.dumps(routing), encoding="utf-8")

    result = suggest_next_skill(
        tmp_path,
        current_skill="heyeddi-design",
        current_route="/dashboard",
    )
    assert result["next"]["skill"] == "heyeddi-handoff"
    assert "@heyeddi-handoff" in result["next"]["prompt"]
    assert result["next"]["source"] == "skill-routing.json"


def test_pipeline_skills_have_handoff_section() -> None:
    pipeline = {
        "heyeddi-intake",
        "heyeddi-product",
        "heyeddi-orchestrator",
        "heyeddi-design",
        "heyeddi-handoff",
        "design-handoff-flutter",
        "project-engineering",
        "flutter-engineering",
        "visual-auditor",
        "engineering-excellence",
        "pre-merge-gate",
        "heyeddi-pr-review",
        "heyeddi-pr-respond",
    }
    heading = "## When the task is complete: suggest next skills"
    missing: list[str] = []
    for name in pipeline:
        skill_md = ROOT / "skills" / name / "SKILL.md"
        if heading not in skill_md.read_text(encoding="utf-8"):
            missing.append(name)
    assert not missing, f"missing task-complete section: {missing}"
