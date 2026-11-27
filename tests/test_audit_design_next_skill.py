"""The next-skill chain must keep a build moving: backlog loop, no design pause, no merge ask."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "heyeddi" / "scripts"))

import _next_skill as ns  # noqa: E402

PAUSING = re.compile(r"@heyeddi-design shape|@taste-penpot design|ask the user", re.IGNORECASE)


def _entries() -> list[dict]:
    out = list(ns.DEFAULT_NEXT.values()) + [ns.DONE_NEXT]
    for modes in ns.MODE_NEXT.values():
        out.extend(modes.values())
    return out


def test_no_default_prompt_pauses_a_build() -> None:
    bad = [e["prompt"] for e in _entries() if PAUSING.search(e["prompt"])]
    assert not bad, bad


def test_merge_below_production_then_backlog(tmp_path: Path) -> None:
    step = ns.suggest_next_skill(tmp_path, current_skill="pre-merge-gate")["next"]
    text = step["prompt"] + " " + step["why"]
    assert "backlog.py" in text
    assert "dev / test / staging" in text
    assert "production" in text


def test_product_hands_off_to_the_backlog_loop(tmp_path: Path) -> None:
    for mode in (None, "audit"):
        step = ns.suggest_next_skill(tmp_path, current_skill="heyeddi-product", current_mode=mode)["next"]
        assert "backlog.py" in step["prompt"]


def test_intake_goes_to_specs_and_backlog_even_with_routing(tmp_path: Path) -> None:
    intake = tmp_path / ".heyeddi" / "docs" / "intake"
    intake.mkdir(parents=True)
    (intake / "skill-routing.json").write_text(
        json.dumps({"scaffold": ["project-engineering"], "routes": [{"route": "/a", "skill": "heyeddi-design"}]}),
        encoding="utf-8",
    )
    step = ns.suggest_next_skill(tmp_path, current_skill="heyeddi-intake")["next"]
    assert step["skill"] == "heyeddi-product"
    assert "backlog" in step["prompt"]


def test_setup_prompt_writes_defaults_without_an_interview(tmp_path: Path) -> None:
    prompt = ns.suggest_next_skill(tmp_path, current_skill="heyeddi")["next"]["prompt"]
    assert "write_setup.py --defaults" in prompt


def test_instruction_runs_in_scope_work_instead_of_handing_it_back(tmp_path: Path) -> None:
    instruction = ns.suggest_next_skill(tmp_path, current_skill="heyeddi-handoff")["instruction"]
    assert "run it now" in instruction
    assert "backlog" in instruction
    assert "paste" not in instruction
