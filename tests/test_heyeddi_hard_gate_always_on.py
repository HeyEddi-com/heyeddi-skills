"""@heyeddi must require ensure_always_on_agents / sync before chat-only replies."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "heyeddi" / "SKILL.md"
ALWAYS_ON = ROOT / "skills" / "heyeddi" / "reference" / "always-on.md"
ANTI = ROOT / "skills" / "heyeddi" / "context" / "ANTI_PATTERNS.md"


def test_skill_declares_hard_gate_before_routing() -> None:
    body = SKILL.read_text(encoding="utf-8")
    assert "## Hard gate (first action — no exceptions)" in body
    assert "ensure_always_on_agents.py" in body
    assert "Forbidden:** Chat-only `@heyeddi`" in body or "Forbidden:** Chat-only" in body
    assert "Attaching the skill is not enough" in body


def test_always_on_ref_requires_script_first() -> None:
    body = ALWAYS_ON.read_text(encoding="utf-8")
    assert "Hard gate on `@heyeddi`" in body
    assert "No chat-only escape" in body


def test_anti_patterns_ban_chat_only() -> None:
    body = ANTI.read_text(encoding="utf-8")
    assert "Chat-only `@heyeddi`" in body
