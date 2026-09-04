#!/usr/bin/env python3
"""
Test HeyEddi skills in this hub.

Layers:
  1. structure — SKILL.md, manifest.json, scripts exist and align
  2. smoke     — invoke each manifest tool against fixtures/sample-vue-app
  3. cloud     — same invocations via scripts/cloud/invoke_skill_tool.py

Usage:
  python3 scripts/test-skills.py              # all skills
  python3 scripts/test-skills.py visual-auditor
  python3 scripts/test-skills.py --list
  python3 scripts/test-skills.py --structure-only
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
FIXTURE_ROOT = REPO_ROOT / "fixtures" / "sample-vue-app"
FLUTTER_FIXTURE_ROOT = REPO_ROOT / "fixtures" / "sample-flutter-app"
INVOKE_TOOL = REPO_ROOT / "scripts" / "cloud" / "invoke_skill_tool.py"
REGISTER_TOOLS = REPO_ROOT / "scripts" / "cloud" / "register_tools.py"

FLUTTER_SKILLS = frozenset(
    {
        "flutter-engineering",
        "flutter-patterns",
        "dart-type-bridger",
        "design-handoff-flutter",
    }
)

PRODUCT_TRANSLATOR_FIXTURE = REPO_ROOT / "fixtures" / "sample-vue-app"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


@dataclass
class TestResult:
    skill: str
    tool: str
    layer: str
    ok: bool
    detail: str = ""


@dataclass
class RunReport:
    results: list[TestResult] = field(default_factory=list)

    def add(self, **kwargs: Any) -> None:
        self.results.append(TestResult(**kwargs))

    @property
    def failed(self) -> list[TestResult]:
        return [r for r in self.results if not r.ok]

    def print_summary(self) -> None:
        passed = sum(1 for r in self.results if r.ok)
        total = len(self.results)
        print(f"\n{'=' * 60}")
        print(f"Results: {passed}/{total} passed")
        for r in self.failed:
            print(f"  FAIL [{r.layer}] {r.skill}/{r.tool}: {r.detail}")
        print(f"{'=' * 60}")


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm


def validate_structure(skill_dir: Path, report: RunReport) -> None:
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    manifest_path = skill_dir / "manifest.json"

    if not skill_md.is_file():
        report.add(skill=name, tool="(structure)", layer="structure", ok=False, detail="missing SKILL.md")
        return

    fm = parse_frontmatter(skill_md)
    if fm.get("name") != name:
        report.add(
            skill=name,
            tool="(structure)",
            layer="structure",
            ok=False,
            detail=f"frontmatter name={fm.get('name')!r} != folder {name!r}",
        )
    else:
        report.add(skill=name, tool="(structure)", layer="structure", ok=True, detail="SKILL.md frontmatter")

    body = skill_md.read_text(encoding="utf-8")
    pipeline_handoff = "## When the task is complete: suggest next skills"
    if not fm.get("deprecated") and name in {
        "heyeddi-intake",
        "heyeddi-product",
        "heyeddi-orchestrator",
        "heyeddi-design",
        "heyeddi-handoff",
        "design-handoff-flutter",
        "project-engineering",
        "flutter-engineering",
        "visual-auditor",
        "pre-merge-gate",
        "heyeddi-pr-review",
        "heyeddi-pr-respond",
    }:
        if pipeline_handoff not in body:
            report.add(
                skill=name,
                tool="(structure)",
                layer="structure",
                ok=False,
                detail="missing task-complete next-skill section",
            )
        else:
            report.add(
                skill=name,
                tool="(structure)",
                layer="structure",
                ok=True,
                detail="task-complete next-skill section",
            )

    if not (skill_dir / "context" / "VOCABULARY.md").is_file():
        report.add(skill=name, tool="(structure)", layer="structure", ok=False, detail="missing context/VOCABULARY.md")
    if not (skill_dir / "scripts" / "_skill_cli.py").is_file():
        report.add(skill=name, tool="(structure)", layer="structure", ok=False, detail="missing scripts/_skill_cli.py")

    if not manifest_path.is_file():
        report.add(skill=name, tool="(structure)", layer="structure", ok=False, detail="missing manifest.json")
        return

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        report.add(skill=name, tool="(structure)", layer="structure", ok=False, detail=f"invalid manifest: {exc}")
        return

    if manifest.get("skill") != name:
        report.add(
            skill=name,
            tool="(structure)",
            layer="structure",
            ok=False,
            detail=f"manifest skill={manifest.get('skill')!r}",
        )

    for tool in manifest.get("tools", []):
        script = skill_dir / tool.get("script", "")
        tool_name = tool.get("name", "?")
        if not script.is_file():
            report.add(
                skill=name,
                tool=tool_name,
                layer="structure",
                ok=False,
                detail=f"missing script {tool.get('script')}",
            )
        else:
            report.add(skill=name, tool=tool_name, layer="structure", ok=True, detail="script exists")


def default_args_for_tool(tool_name: str, skill_name: str, fixture_root: Path) -> dict[str, Any]:
    """Default CLI args per tool for fixture smoke tests."""
    args: dict[str, Any] = {"project_root": str(fixture_root)}
    if tool_name in {
        "capture_screenshots",
        "extract_layout",
        "audit_contrast",
        "load_visual_context",
        "finalize_visual_review",
        "load_handoff",
        "describe_handoff",
        "verify_handoff",
        "verify_tokens",
        "verify_theme",
        "verify_prose",
        "scan_patterns",
        "init_engineering_docs",
        "audit_engineering",
        "check_engineering_plan",
        "init_ux_flows",
        "trace_flow",
    }:
        args["route"] = "/settings"
    if tool_name == "audit_contrast":
        fixture = REPO_ROOT / "skills" / "visual-auditor" / "fixtures" / "contrast-violations.html"
        if fixture.is_file():
            args["fixture"] = str(fixture)
            args["route"] = "/"
            args["widths"] = "375"
    if tool_name == "load_visual_context":
        args["write_review"] = True
    if tool_name == "append_fix_log":
        args["issue"] = "Smoke test contrast issue"
        args["fix"] = "Adjusted token in fixture"
        args["spec_ref"] = "design.md semantic text"
        args["files"] = "src/views/SettingsView.vue"
    if tool_name == "finalize_visual_review":
        args["skip_recapture"] = True
    if tool_name == "trace_flow":
        args["task_id"] = "update-profile"
    if tool_name == "append_decision":
        args["title"] = "Smoke test ADR"
        args["context"] = "Eval fixture"
        args["decision"] = "Use composables for API access"
        args["consequences"] = "None in fixture"
    if tool_name == "diff_violations":
        args["golden"] = "/settings"
        args["target"] = "/settings"
    if tool_name == "sync" and skill_name == "heyeddi-orchestrator":
        args["skip_update_check"] = True
    if tool_name == "check_skills_update":
        args["latest"] = "99.0.0"
        args["force"] = True
    if tool_name == "fetch_pr_comments":
        args["pr"] = 42
        fixture = REPO_ROOT / "skills" / skill_name / "fixtures" / "sample-pr-comments.json"
        if fixture.is_file():
            args["fixture"] = str(fixture)
    if tool_name == "fetch_pr_context":
        args["pr"] = 42
        fixture = REPO_ROOT / "skills" / skill_name / "fixtures" / "sample-pr-diff.json"
        if fixture.is_file():
            args["fixture"] = str(fixture)
    if tool_name in ("check_doc_drift", "audit_pr_changes"):
        args["pr"] = 42
        fixture = REPO_ROOT / "skills" / "heyeddi-pr-review" / "fixtures" / "sample-pr-diff.json"
        if fixture.is_file():
            args["fixture"] = str(fixture)
    if tool_name == "write_pr_review":
        args["pr"] = 42
        args["force"] = True
        fixture = REPO_ROOT / "skills" / "heyeddi-pr-review" / "fixtures" / "sample-pr-diff.json"
        if fixture.is_file():
            args["fixture"] = str(fixture)
    if tool_name == "verify_pr_review":
        args["pr"] = 42
    if tool_name == "verify_response":
        args["pr"] = 42
        fixture = REPO_ROOT / "skills" / "heyeddi-pr-respond" / "fixtures" / "sample-pr-comments.json"
        if fixture.is_file():
            args["fixture"] = str(fixture)
        _seed_pr_respond_docs(fixture_root)
    if tool_name == "post_thread_replies":
        args["pr"] = 42
        args["dry_run"] = True
        _seed_pr_respond_docs(fixture_root)
    if tool_name == "validate_composable":
        args["path"] = "src/composables/useApi.ts"
    if tool_name == "write_test_stub":
        args["path"] = "src/views/SettingsView.vue"
    if tool_name == "dev_server_info":
        args["route"] = "/settings"
    if tool_name == "audit_dependencies":
        pass
    if tool_name in ("scaffold_vue", "scaffold_stack", "scaffold_fastapi", "scaffold_firebase", "scaffold_flutter"):
        args["dry_run"] = True
    if tool_name in ("write_product", "write_translation", "write_routing", "generate_wireframe", "prepare_mockup_prompts", "seed_brief", "build_routing"):
        args["dry_run"] = True
    if tool_name == "write_product":
        args["json"] = json.dumps(
            {
                "product_name": "SmokeTest",
                "audience_summary": "Small teams",
                "stack_note": "Vue + FastAPI",
                "personas": [
                    {
                        "name": "Alex",
                        "role": "Lead",
                        "primary_job": "Track team",
                        "anxiety": "Missed updates",
                        "design_implication": "Clear dashboard",
                    },
                    {
                        "name": "Sam",
                        "role": "Buyer",
                        "primary_job": "Evaluate tools",
                        "anxiety": "Wrong pick",
                        "design_implication": "Trustworthy marketing",
                    },
                ],
                "route_intent": [
                    {
                        "route": "/",
                        "register": "brand",
                        "primary_persona": "Sam",
                        "mindset": "Comparing",
                        "success_feeling": "Trust",
                    },
                    {
                        "route": "/settings",
                        "register": "product",
                        "primary_persona": "Alex",
                        "mindset": "Focused",
                        "success_feeling": "Saved",
                    },
                ],
                "pages": [
                    {"route": "/", "view": "HomeView", "purpose": "Landing"},
                    {"route": "/settings", "view": "SettingsView", "purpose": "Profile"},
                ],
                "competitors": ["Linear"],
                "competitive_edge": "Simpler roster view",
                "anti_audience": "Enterprise SSO-only",
                "voice_tone": "Plain, confident",
                "design_references": ["Linear — crisp", "Stripe — calm data"],
                "anti_references": ["Generic admin template"],
            }
        )
    if tool_name == "build_routing":
        pass
    if tool_name == "verify_intake":
        pass
    if tool_name == "write_translation":
        args["user_prompt"] = "Smoke test app"
        args["summary"] = "Test product for skill smoke"
    if tool_name == "write_routing":
        args["json"] = '{"routes":[{"route":"/settings","skill":"heyeddi-handoff"}]}'
    if tool_name == "prepare_mockup_prompts":
        args["feature"] = "settings"
        args["route"] = "/settings"
    if tool_name == "generate_wireframe":
        args["feature"] = "settings"
        args["route"] = "/settings"
    if tool_name == "seed_brief":
        args["feature"] = "settings"
    if tool_name == "write_feature_spec":
        args["dry_run"] = True
        args["json"] = json.dumps(
            {
                "route": "/settings",
                "title": "Settings",
                "user_stories": ["As a user, I want to save profile so that my team sees updates."],
                "acceptance_criteria": ["Save button persists changes"],
            }
        )
    if tool_name == "write_review_plan":
        args["title"] = "Smoke review"
        args["force"] = True
    if tool_name == "verify_product":
        args["skip_features"] = True
    if tool_name == "suggest_skills":
        args["user_prompt"] = "Build TaskFlow Vue app with settings handoff"
    if tool_name == "init_workflow_sync":
        pass
    if tool_name == "load_workflow_context":
        args["route"] = "/settings"
    if tool_name == "append_pillar_opinion":
        args["pillar"] = "product"
        args["route"] = "/settings"
        args["opinion"] = "Smoke test — settings AC look complete"
        args["docs_updated"] = ".heyeddi/docs/product/features/settings.md"
    if tool_name == "write_skills_index":
        args["dry_run"] = True
    if tool_name == "sync":
        args["dry_run"] = True
        args["skip_workflow"] = True
    if tool_name == "validate_provider":
        args["path"] = "lib/services/api_client.dart"
    return args


def _seed_pr_respond_docs(fixture_root: Path) -> None:
    """Minimal tracking + replies so verify/post smoke tools can run offline."""
    docs = fixture_root / ".heyeddi" / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    tracking = docs / "pr-42-tracking.md"
    replies = docs / "pr-42-replies.md"
    if not tracking.is_file():
        tracking.write_text(
            """# PR 42 tracking

| Comment ID | Type | Author | Summary | Action | Status |
|------------|------|--------|---------|--------|--------|
| 9001001 | inline | qa-reviewer | Pagination | fix | RESPONDED |
| 9001002 | inline | backend-lead | Depends | fix | RESPONDED |
| DC_10001 | discussion | product-owner | Loading | fix | RESPONDED |
| 8001 | review | backend-lead | Address notes | partial | RESPONDED |
| 8002 | review | qa-reviewer | LGTM | decline | RESPONDED |
""",
            encoding="utf-8",
        )
    if not replies.is_file():
        replies.write_text(
            """# PR #42 replies

## Comment 9001001 (inline)
Fixed - Pagination is 1-based.

## Comment 9001002 (inline)
Fixed - Removed redundant Depends.

## Comment DC_10001 (discussion)
@product-owner Added loading skeleton.

## Comment 8001 (review)
@backend-lead Addressed inline notes.

## Comment 8002 (review)
@qa-reviewer Thanks.

## Summary
Responded to 5/5 comments. Ready for re-review.
""",
            encoding="utf-8",
        )


def is_acceptable_output(output: str) -> bool:
    if not output.strip():
        return False
    if "Traceback (most recent call last)" in output:
        return False
    if "SyntaxError" in output or "IndentationError" in output:
        return False
    return True


def run_direct(skill_dir: Path, script: str, args: dict[str, Any]) -> str:
    script_path = skill_dir / script
    if script_path.suffix == ".sh":
        cmd = ["bash", str(script_path)]
    else:
        cmd = [sys.executable, str(script_path)]
    for key, value in args.items():
        flag = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                cmd.append(flag)
            continue
        if isinstance(value, list):
            for item in value:
                cmd.extend([flag, str(item)])
        else:
            cmd.extend([flag, str(value)])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=skill_dir)
    return (result.stdout or "") + (result.stderr or "")


def run_cloud_invoker(skill_dir: Path, script: str, args: dict[str, Any], fixture_root: Path) -> str:
    result = subprocess.run(
        [
            sys.executable,
            str(INVOKE_TOOL),
            "--skill-dir",
            str(skill_dir),
            "--script",
            script,
            "--project-root",
            str(fixture_root),
            "--args-json",
            json.dumps(args),
        ],
        capture_output=True,
        text=True,
    )
    return (result.stdout or "") + (result.stderr or "")


def smoke_test_tool(skill_dir: Path, tool: dict[str, Any], fixture_root: Path, report: RunReport) -> None:
    name = skill_dir.name
    tool_name = tool["name"]
    script = tool["script"]
    args = default_args_for_tool(tool_name, name, fixture_root)

    for layer, runner in (("smoke", run_direct), ("cloud", run_cloud_invoker)):
        try:
            if layer == "cloud":
                output = run_cloud_invoker(skill_dir, script, args, fixture_root)
            else:
                output = run_direct(skill_dir, script, args)
        except Exception as exc:  # noqa: BLE001
            report.add(skill=name, tool=tool_name, layer=layer, ok=False, detail=str(exc))
            continue
        ok = is_acceptable_output(output)
        detail = output.strip().splitlines()[0][:120] if output.strip() else "empty output"
        report.add(skill=name, tool=tool_name, layer=layer, ok=ok, detail=detail)


def fixture_for_skill(skill_name: str) -> Path:
    if skill_name in ("heyeddi-intake", "heyeddi-product"):
        return PRODUCT_TRANSLATOR_FIXTURE if PRODUCT_TRANSLATOR_FIXTURE.is_dir() else FIXTURE_ROOT
    if skill_name in FLUTTER_SKILLS and FLUTTER_FIXTURE_ROOT.is_dir():
        return FLUTTER_FIXTURE_ROOT
    return FIXTURE_ROOT


def list_skills() -> list[str]:
    return sorted(
        p.name
        for p in SKILLS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".") and (p / "SKILL.md").is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Test skills in this hub")
    parser.add_argument("skill", nargs="?", help="Test one skill by name")
    parser.add_argument("--list", action="store_true", help="List skill names")
    parser.add_argument("--structure-only", action="store_true", help="Skip smoke/cloud invocations")
    parser.add_argument("--fixture", default=str(FIXTURE_ROOT), help="Fixture project root")
    args = parser.parse_args()

    fixture_root = Path(args.fixture).resolve()
    use_default_fixture = args.fixture == str(FIXTURE_ROOT)

    if args.list:
        for name in list_skills():
            print(name)
        return 0

    if not fixture_root.is_dir():
        print(f"Fixture missing: {fixture_root}", file=sys.stderr)
        return 1

    names = [args.skill] if args.skill else list_skills()
    report = RunReport()

    for name in names:
        skill_dir = SKILLS_DIR / name
        if not skill_dir.is_dir():
            report.add(skill=name, tool="(all)", layer="structure", ok=False, detail="skill not found")
            continue
        validate_structure(skill_dir, report)
        if args.structure_only:
            continue
        manifest = json.loads((skill_dir / "manifest.json").read_text())
        skill_fixture = fixture_for_skill(name) if use_default_fixture else fixture_root
        for tool in manifest.get("tools", []):
            smoke_test_tool(skill_dir, tool, skill_fixture, report)

    # Registry sanity
    if REGISTER_TOOLS.is_file() and not args.structure_only:
        reg = subprocess.run(
            [sys.executable, str(REGISTER_TOOLS), str(REPO_ROOT)],
            capture_output=True,
            text=True,
        )
        ok = reg.returncode == 0 and "Traceback" not in reg.stderr
        detail = "tools registered" if ok else (reg.stderr or reg.stdout)[:120]
        report.add(skill="(hub)", tool="register_tools", layer="cloud", ok=ok, detail=detail)

    report.print_summary()
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
