"""Audit fixes 4, 12, 16-18, 20, 23-25: prose matches the policy and nothing waits for no reason."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
HEYEDDI = SKILLS / "heyeddi" / "scripts"
SETUP = SKILLS / "heyeddi-setup" / "scripts"
sys.path.insert(0, str(HEYEDDI))
sys.path.insert(0, str(SKILLS / "heyeddi-local-first" / "scripts"))

import finish_guard  # noqa: E402
from permission_policy import PRESETS, ask_at_least  # noqa: E402

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _read(rel: str) -> str:
    return (SKILLS / rel).read_text(encoding="utf-8")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=cwd, check=True, capture_output=True, env=ENV,
    )


# --- 4: the setup preset table is the policy ---------------------------------------------------


@pytest.mark.parametrize("preset", ["cautious", "balanced", "autonomous"])
def test_setup_preset_table_matches_the_policy(preset: str) -> None:
    text = _read("heyeddi-setup/SKILL.md")
    row = next(line for line in text.splitlines() if line.startswith(f"| `{preset}` |"))
    cells = [cell.strip().split(" ")[0] for cell in row.strip("|").split("|")][1:]
    policy = PRESETS[preset]
    assert cells == [
        policy["commit"],
        policy["merge"],
        ask_at_least(policy["push_protected"]),
        policy["release"],
        policy["read"]["prod"],
        policy["write"]["staging"],
        policy["write"]["prod"],
    ]


# --- 12: setup defaults never name a feature branch as production -------------------------------


def _defaults(root: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SETUP / "write_setup.py"), "--project-root", str(root), "--defaults"],
        capture_output=True, text=True, check=False, env=ENV,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads((root / ".heyeddi" / "stack.json").read_text(encoding="utf-8"))["git"]


@pytest.mark.parametrize("trunk", ["main", "master", "trunk"])
def test_defaults_on_a_feature_branch_pick_the_trunk(tmp_path: Path, trunk: str) -> None:
    _git(tmp_path, "init", "-q", "-b", trunk)
    _git(tmp_path, "commit", "-qm", "r", "--allow-empty")
    _git(tmp_path, "checkout", "-qb", "feat/login")
    git = _defaults(tmp_path)
    assert git["environments"]["production"] == trunk
    assert git["default_branch"] == trunk


def test_defaults_with_no_recognisable_trunk_fall_back_to_main(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "feat/a")
    _git(tmp_path, "commit", "-qm", "r", "--allow-empty")
    _git(tmp_path, "checkout", "-qb", "feat/b")
    assert _defaults(tmp_path)["environments"]["production"] == "main"


# --- 16: a failed build fails -------------------------------------------------------------------

VERIFY = SKILLS / "verify-build" / "scripts" / "verify_build.sh"


def _verify(root: Path) -> int:
    return subprocess.run(
        ["bash", str(VERIFY), "--project-root", str(root)], capture_output=True, text=True, check=False
    ).returncode


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm not installed")
@pytest.mark.parametrize(("script", "ok"), [("exit 3", False), ("true", True)])
def test_verify_build_exit_code_follows_the_build(tmp_path: Path, script: str, ok: bool) -> None:
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {"build": script}}), encoding="utf-8")
    assert (_verify(tmp_path) == 0) is ok


def test_verify_build_without_package_json_fails(tmp_path: Path) -> None:
    assert _verify(tmp_path) != 0


# --- 17: local-first prose agrees with the gate ---------------------------------------------------


def test_local_first_prose_does_not_forbid_what_the_policy_allows() -> None:
    docs = "\n".join(
        _read(f"heyeddi-local-first/{rel}")
        for rel in ("SKILL.md", "reference/process.md", "context/EXAMPLES.md", "manifest.json")
    )
    for stale in ("Do not change live systems", "would change. Stop.", "Hard gate for every agent",
                  "Exit 1 means the command is a live change. Do not run it", "Leave apply to Cloud Build"):
        assert stale not in docs, stale
    assert "check_permission.py" in _read("heyeddi-local-first/reference/process.md")


# --- 18: cross-pillar sync ends -----------------------------------------------------------------


def _script(name: str, root: Path, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HEYEDDI / name), "--project-root", str(root), *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _opine(root: Path, pillar: str, route: str = "/a") -> dict:
    return _script("append_pillar_opinion.py", root, "--pillar", pillar, "--route", route, "--opinion", "ok")


def _pending(root: Path, route: str = "/a") -> list[str]:
    return _script("load_workflow_context.py", root, "--route", route)["pending_sibling_notes"]


def test_replies_request_nobody_and_the_route_finishes(tmp_path: Path) -> None:
    _script("init_workflow_sync.py", tmp_path)
    assert _opine(tmp_path, "product")["request_pillars"] == ["ux", "design"]
    assert _pending(tmp_path)
    assert _opine(tmp_path, "ux")["request_pillars"] == []
    assert _pending(tmp_path), "design has not answered yet"
    assert _opine(tmp_path, "design")["request_pillars"] == []
    assert _pending(tmp_path) == []
    assert _opine(tmp_path, "product")["request_pillars"] == ["ux", "design"], "new work asks again"


def test_a_reply_on_one_route_does_not_answer_another(tmp_path: Path) -> None:
    _script("init_workflow_sync.py", tmp_path)
    _opine(tmp_path, "product", "/a")
    assert _opine(tmp_path, "ux", "/ab")["request_pillars"] == ["product", "design"]
    assert _pending(tmp_path, "/a")


# --- 20: Go the language is not a "go" ------------------------------------------------------------


@pytest.mark.parametrize(
    "ending",
    [
        "Rebuilt the Go service and its tests pass.",
        "Updated the go.mod file.",
        "Done: the Go, Vue and API layers.",
        "Bumped your go toolchain to 1.25.",
        "The app now works on the go.",
        "I'd say Go is the better fit, and the port is done.",
        "We need the go compiler in CI, and it is installed now.",
        "Ported to the Go.",
    ],
)
def test_mentions_of_go_pass(ending: str) -> None:
    assert not finish_guard.decide({"last_assistant_message": ending}), ending


@pytest.mark.parametrize(
    "ending",
    [
        'Phase 2 is ready for your "go".',
        "I need your go before merging.",
        "Phase 2 starts on your go.",
        "I still need the go-ahead.",
        "Awaiting the go to continue.",
        "Say go and I will start.",
        "Give me the 'go' and I'll push.",
        "If you say go, I'll finish the PR.",
        "I was waiting for your go on RR-2.",
    ],
)
def test_real_go_waits_are_blocked(ending: str) -> None:
    assert finish_guard.decide({"last_assistant_message": ending}), ending


# --- 23, 24, 25: wording that made agents stop or fail ----------------------------------------------


def test_router_runs_the_target_skill_after_routing() -> None:
    text = _read("heyeddi/context/ANTI_PATTERNS.md")
    assert "this skill routes only" not in text
    assert "same turn" in text


def test_update_notice_does_not_wait_for_a_reply(tmp_path: Path) -> None:
    data = _script("check_skills_update.py", tmp_path, "--latest", "99.0.0", "--force")
    assert "Reply `update`" not in data["user_block"]
    assert "Needs you" in data["agent_instruction"]
    assert "keep working" in data["agent_instruction"].lower()
    assert "Ask the user to approve before" not in data["agent_instruction"]
    assert "Never run npx skills add without explicit approval" in data["agent_instruction"]


def test_plan_checklist_runs_the_cost_estimate_without_check() -> None:
    text = _read("engineering-excellence/scripts/check_engineering_plan.py")
    assert "estimate_change_cost.py --check" not in text
    assert "estimate_change_cost.py" in text
