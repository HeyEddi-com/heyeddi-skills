"""Ops documents: scaffolded once, and rejected while a required part is empty."""
from __future__ import annotations

from pathlib import Path

from _skill_loader import load_skill_script


def _ops():
    return load_skill_script("heyeddi-ops", "ops_docs")


def _filled(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace("TODO", "done"), encoding="utf-8")


def test_untouched_templates_fail_and_filled_ones_pass(tmp_path: Path) -> None:
    ops = _ops()
    created = ops.init(tmp_path, "api")
    assert [p.name for p in created] == ["threat-model.md", "api.md", "lessons.md"]
    assert ops.check(tmp_path)
    for path in created:
        _filled(path)
    assert ops.check(tmp_path) == []


def test_init_never_overwrites(tmp_path: Path) -> None:
    ops = _ops()
    runbook = ops.init(tmp_path, "api")[1]
    runbook.write_text("mine", encoding="utf-8")
    assert ops.init(tmp_path, "api") == []
    assert runbook.read_text(encoding="utf-8") == "mine"


def test_missing_section_and_accepted_risk_without_reason(tmp_path: Path) -> None:
    ops = _ops()
    threat, runbook, lessons = ops.init(tmp_path, "api")
    for path in (threat, runbook, lessons):
        _filled(path)
    runbook.write_text(runbook.read_text(encoding="utf-8").replace("## Rollback", "## Other"), encoding="utf-8")
    threat.write_text(threat.read_text(encoding="utf-8") + "| Token in state | |\n", encoding="utf-8")
    problems = "\n".join(ops.check(tmp_path))
    assert "Rollback" in problems
    assert "Token in state" in problems


def test_no_documents_is_a_failure(tmp_path: Path) -> None:
    assert _ops().check(tmp_path)


def test_service_name_cannot_leave_the_folder(tmp_path: Path) -> None:
    import pytest

    with pytest.raises(ValueError):
        _ops().init(tmp_path, "../x")
