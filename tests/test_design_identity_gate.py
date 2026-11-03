"""Identity gate must exist and be wired into taste / design skills."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TASTE = REPO / "skills" / "taste-penpot"
DESIGN = REPO / "skills" / "heyeddi-design"
HEYEDDI = REPO / "skills" / "heyeddi"


def test_identity_gate_reference_exists() -> None:
    path = TASTE / "references" / "identity-gate.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "≥3" in text or "at least three" in text.lower() or ">=3" in text
    assert "Stop" in text or "stop" in text
    assert "Typography" in text or "typography" in text
    assert "hex" in text.lower()


def test_taste_skill_wires_identity_gate() -> None:
    skill = (TASTE / "SKILL.md").read_text(encoding="utf-8")
    assert "identity-gate.md" in skill
    assert "1.0 Identity gate" in skill or "Identity gate" in skill
    assert "version: 1.3.0" in skill
    anti = (TASTE / "context" / "ANTI_PATTERNS.md").read_text(encoding="utf-8")
    assert "identity-gate" in anti


def test_heyeddi_design_defers_to_identity_gate() -> None:
    brief = (DESIGN / "reference" / "brief-language.md").read_text(encoding="utf-8")
    assert "identity-gate" in brief
    shape = (DESIGN / "reference" / "shape.md").read_text(encoding="utf-8")
    assert "identity gate" in shape.lower()
    skill = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
    assert "identity gate" in skill.lower()


def test_heyeddi_router_mentions_identity_gate() -> None:
    skill = (HEYEDDI / "SKILL.md").read_text(encoding="utf-8")
    assert "identity gate" in skill.lower()
    assert "identity-gate.md" in skill
