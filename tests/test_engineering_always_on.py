"""Always-on engineering excellence: plan gate, change gate, pre-merge wiring."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENG_SCRIPTS = ROOT / "skills" / "engineering-excellence" / "scripts"
PRE_MERGE = ROOT / "skills" / "pre-merge-gate" / "scripts" / "pre_merge_gate.py"
ORCH_SCRIPTS = ROOT / "skills" / "heyeddi-orchestrator" / "scripts"

sys.path.insert(0, str(ENG_SCRIPTS))
sys.path.insert(0, str(ORCH_SCRIPTS))

from audit_engineering import audit_engineering  # noqa: E402
from check_engineering_plan import check_engineering_plan  # noqa: E402
from _next_skill import suggest_next_skill  # noqa: E402


def _init_docs(project: Path) -> None:
    script = ENG_SCRIPTS / "init_engineering_docs.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--project-root", str(project), "--force"],
        cwd=str(ENG_SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_plan_gate_errors_when_docs_missing(tmp_path: Path) -> None:
    result = check_engineering_plan(tmp_path, plan_text=None, plan_label="(none)")
    assert result["ok"] is False
    assert result["error_count"] >= 3
    assert result["always_on"] is True
    assert any(f["severity"] == "error" for f in result["findings"])


def test_plan_gate_passes_after_init(tmp_path: Path) -> None:
    _init_docs(tmp_path)
    result = check_engineering_plan(tmp_path, plan_text=None, plan_label="(none)")
    assert result["ok"] is True
    assert result["error_count"] == 0
    assert "reuse-catalog.md" in " ".join(result["checklist"])


def test_plan_gate_errors_on_yagni_smell_without_reuse(tmp_path: Path) -> None:
    _init_docs(tmp_path)
    plan = "Add a UserManagerFactory and AbstractBaseService for future scale."
    result = check_engineering_plan(tmp_path, plan_text=plan, plan_label="plan.md")
    assert result["ok"] is False
    assert any(f["principle"] == "YAGNI" and f["severity"] == "error" for f in result["findings"])


def test_plan_gate_allows_abstraction_when_reuse_cited(tmp_path: Path) -> None:
    _init_docs(tmp_path)
    plan = (
        "Extend existing useUsers composable (reuse-catalog). "
        "No new Factory; YAGNI: second call site already exists."
    )
    result = check_engineering_plan(tmp_path, plan_text=plan, plan_label="plan.md")
    assert result["ok"] is True


def test_audit_errors_when_engineering_docs_missing(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    result = audit_engineering(tmp_path)
    assert result["ok"] is False
    errors = [f for f in result["findings"] if f["severity"] == "error"]
    assert errors
    assert all(f["principle"] == "Documentation" for f in errors)


def test_audit_check_cli_exit_codes(tmp_path: Path) -> None:
    script = ENG_SCRIPTS / "audit_engineering.py"
    missing = subprocess.run(
        [sys.executable, str(script), "--project-root", str(tmp_path), "--check"],
        cwd=str(ENG_SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert missing.returncode != 0

    _init_docs(tmp_path)
    ok = subprocess.run(
        [sys.executable, str(script), "--project-root", str(tmp_path), "--check"],
        cwd=str(ENG_SCRIPTS),
        capture_output=True,
        text=True,
    )
    assert ok.returncode == 0
    payload = json.loads(ok.stdout)
    assert payload["ok"] is True


def test_audit_warn_does_not_fail_check(tmp_path: Path) -> None:
    _init_docs(tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    fat = src / "FatView.vue"
    fat.write_text("\n".join(f"// line {i}" for i in range(450)), encoding="utf-8")
    result = audit_engineering(tmp_path)
    warns = [f for f in result["findings"] if f["severity"] == "warn"]
    errors = [f for f in result["findings"] if f["severity"] == "error"]
    assert warns
    assert not errors
    assert result["ok"] is True


def test_audit_extreme_file_is_error(tmp_path: Path) -> None:
    _init_docs(tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    fat = src / "GodFile.vue"
    fat.write_text("\n".join(f"// line {i}" for i in range(850)), encoding="utf-8")
    result = audit_engineering(tmp_path)
    assert result["ok"] is False
    assert any(
        f["severity"] == "error" and f["principle"] == "KISS" for f in result["findings"]
    )


def test_pre_merge_includes_engineering_audit(tmp_path: Path) -> None:
    """Gate wires engineering-audit; hub sibling resolve → PASS when docs exist."""
    _init_docs(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            str(PRE_MERGE),
            "--project-root",
            str(tmp_path),
            "--skip-backend",
            "--skip-duplicate-ui",
            "--skip-prose-audit",
            "--skip-visual-audit",
        ],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "engineering-audit" in out
    assert "| engineering-audit | PASS |" in out or "| engineering-audit | SKIP |" in out
    if "| engineering-audit | PASS |" in out:
        assert proc.returncode == 0


def test_pre_merge_skip_engineering_flag(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(PRE_MERGE),
            "--project-root",
            str(tmp_path),
            "--skip-backend",
            "--skip-duplicate-ui",
            "--skip-prose-audit",
            "--skip-visual-audit",
            "--skip-engineering-audit",
        ],
        cwd=str(PRE_MERGE.parent),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "| engineering-audit | SKIP |" in out
    assert proc.returncode == 0


def test_next_skill_handoff_to_engineering(tmp_path: Path) -> None:
    result = suggest_next_skill(tmp_path, current_skill="heyeddi-handoff", current_route="/settings")
    assert result["next"]["skill"] == "engineering-excellence"
    assert "audit_engineering" in result["next"]["prompt"]
    assert "/settings" in result["next"]["prompt"]


def test_next_skill_engineering_to_visual(tmp_path: Path) -> None:
    result = suggest_next_skill(
        tmp_path,
        current_skill="engineering-excellence",
        current_route="/settings",
        current_mode="audit",
    )
    assert result["next"]["skill"] == "visual-auditor"


def test_always_on_docs_exist() -> None:
    assert (ROOT / "docs" / "always-on-skills.md").is_file()
    assert (
        ROOT / "skills" / "engineering-excellence" / "reference" / "engineering-always-on.md"
    ).is_file()
    assert (ROOT / "skills" / "heyeddi-orchestrator" / "reference" / "always-on.md").is_file()


def test_engineering_skill_declares_always_on() -> None:
    body = (ROOT / "skills" / "engineering-excellence" / "SKILL.md").read_text(encoding="utf-8")
    assert "ALWAYS-ON" in body or "Always on" in body
    assert "check_engineering_plan" in body
    manifest = json.loads(
        (ROOT / "skills" / "engineering-excellence" / "manifest.json").read_text(encoding="utf-8")
    )
    names = {t["name"] for t in manifest["tools"]}
    assert "check_engineering_plan" in names
    assert "audit_engineering" in names


def test_pipeline_includes_engineering_excellence_handoff_section() -> None:
    skill_md = ROOT / "skills" / "engineering-excellence" / "SKILL.md"
    assert "## When the task is complete: suggest next skills" in skill_md.read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(
    "skill_name",
    [
        "heyeddi-orchestrator",
        "heyeddi-handoff",
        "project-engineering",
        "flutter-engineering",
        "design-handoff-flutter",
        "pre-merge-gate",
    ],
)
def test_implementers_mention_engineering_gate(skill_name: str) -> None:
    body = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
    assert "engineering" in body.lower()
    assert (
        "audit_engineering" in body
        or "check_engineering_plan" in body
        or "engineering-audit" in body
    )
