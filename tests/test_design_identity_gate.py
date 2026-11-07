"""Identity gate + Penpot layout hard gates must exist and be wired into skills."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TASTE = REPO / "skills" / "taste-penpot"
DESIGN = REPO / "skills" / "heyeddi-design"
HEYEDDI = REPO / "skills" / "heyeddi"


def test_identity_gate_reference_exists() -> None:
    path = TASTE / "references" / "identity-gate.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    assert (
        "3–5" in text
        or "3-5" in text
        or "3 to 5" in lower
        or "≥3" in text
        or "at least three" in lower
        or ">=3" in text
    )
    assert "identity-thinking.md" in text
    assert "what it is" in lower and "why it is" in lower and "how it is" in lower
    assert "Stop" in text or "stop" in text
    assert "Typography" in text or "typography" in text
    assert "hex" in lower
    assert "scaffolding" in lower or "mvp" in lower


def test_taste_skill_wires_identity_gate() -> None:
    skill = (TASTE / "SKILL.md").read_text(encoding="utf-8")
    assert "identity-gate.md" in skill
    assert "1.0 Identity gate" in skill or "Identity gate" in skill
    m = re.search(r"^version:\s*(\d+)\.(\d+)\.(\d+)\s*$", skill, re.M)
    assert m, "taste-penpot SKILL.md must declare version"
    major, minor, patch = map(int, m.groups())
    assert (major, minor, patch) >= (1, 3, 0)
    anti = (TASTE / "context" / "ANTI_PATTERNS.md").read_text(encoding="utf-8")
    assert "identity-gate" in anti


def test_layout_hard_gates_and_heyeddi_mcp() -> None:
    gates = TASTE / "references" / "layout-hard-gates.md"
    assert gates.is_file()
    gates_text = gates.read_text(encoding="utf-8")
    assert "text-wall" in gates_text.lower() or "Text-wall" in gates_text
    assert "hifi.html" in gates_text
    assert "@heyeddi/penpot-mcp-server" in gates_text or "HeyEddi-com/penpot-mcp-server" in gates_text

    skill = (TASTE / "SKILL.md").read_text(encoding="utf-8")
    assert "layout-hard-gates.md" in skill
    assert "Penpot MCP install" in skill
    assert "github:HeyEddi-com/penpot-mcp-server" in skill
    assert "@heyeddi/penpot-mcp-server" in skill

    mcp = (TASTE / "references" / "penpot-mcp.md").read_text(encoding="utf-8")
    assert "set_frame_layout" in mcp
    assert "parentId" in mcp
    assert "github:HeyEddi-com/penpot-mcp-server" in mcp


def test_heyeddi_design_defers_to_identity_gate() -> None:
    brief = (DESIGN / "reference" / "brief-language.md").read_text(encoding="utf-8")
    assert "identity-gate" in brief
    shape = (DESIGN / "reference" / "shape.md").read_text(encoding="utf-8")
    assert "identity gate" in shape.lower()
    skill = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
    assert "identity gate" in skill.lower()
    assert "layout-hard-gates" in skill or "layout hard gates" in skill.lower()


def test_heyeddi_router_mentions_identity_gate() -> None:
    skill = (HEYEDDI / "SKILL.md").read_text(encoding="utf-8")
    assert "identity gate" in skill.lower()
    assert "identity-gate.md" in skill
    assert "heyeddi/penpot-mcp-server" in skill or "layout-hard-gates" in skill
