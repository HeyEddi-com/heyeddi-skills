"""Agent permission policy: presets, env detection, hard limits, legacy keys."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "heyeddi-local-first" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_permission import check  # noqa: E402
from permission_policy import resolve_policy  # noqa: E402

GIT = {"environments": {"production": "main", "staging": "staging"}, "default_branch": "main"}


def _stack(preset: str | None = None, **agent: object) -> dict:
    data: dict = {"git": dict(GIT), "agent": dict(agent)}
    if preset:
        data["agent"]["preset"] = preset
    return data


def _decision(command: str, stack: dict) -> str:
    return check(command, cwd=None, stack=stack).decision


BALANCED = [
    ("git commit -m 'feat: x'", "auto"),
    ("git push origin feat/login", "auto"),
    ("git push -u origin HEAD:feat/login", "auto"),
    ("git push origin main", "ask"),
    ("gh pr create --fill", "auto"),
    ("gh pr comment 12 --body hi", "auto"),
    ("gh pr view 12", "auto"),
    ("gh pr merge 12 --squash", "ask"),
    ("gh release create v1.2.0", "ask"),
    ("npm publish", "ask"),
    ("git push origin v1.2.0", "ask"),
    ("gcloud logging read 'severity>=ERROR' --project=acme-prod", "auto"),
    ("kubectl --context prod logs pod/api-1", "auto"),
    ("gcloud run deploy api --project=acme-dev", "auto"),
    ("gcloud run deploy api --project=acme-staging", "ask"),
    ("gcloud run deploy api --project=acme-prod", "deny"),
    ("psql $PROD_DATABASE_URL -c 'select count(*) from users'", "auto"),
    ("psql $PROD_DATABASE_URL -c 'update users set x=1'", "deny"),
    ("psql -c 'delete from users'", "auto"),  # local socket, no remote host
    ("terraform plan", "auto"),
    ("pytest -n 2", "auto"),
]


@pytest.mark.parametrize(("command", "expected"), BALANCED)
def test_balanced_preset(command: str, expected: str) -> None:
    assert _decision(command, _stack("balanced")) == expected


def test_missing_stack_defaults_to_balanced_not_a_block() -> None:
    assert _decision("git commit -m x", {}) == "auto"
    assert _decision("git push origin feat/x", {}) == "auto"
    assert resolve_policy({})["preset"] == "balanced"


def test_cautious_asks_on_routine_git_and_denies_staging_writes() -> None:
    stack = _stack("cautious")
    assert _decision("git commit -m x", stack) == "ask"
    assert _decision("gh pr create", stack) == "ask"
    assert _decision("gcloud logging read x --project=acme-prod", stack) == "ask"
    assert _decision("kubectl --context staging apply -f k.yaml", stack) == "deny"


def test_autonomous_runs_merge_and_release_but_prod_write_still_asks() -> None:
    stack = _stack("autonomous")
    assert _decision("gh pr merge 3", stack) == "auto"
    assert _decision("gh release create v2", stack) == "auto"
    assert _decision("kubectl --context staging apply -f k.yaml", stack) == "auto"
    assert _decision("gcloud run deploy api --project=acme-prod", stack) == "ask"


def test_prod_write_can_never_be_auto() -> None:
    stack = _stack("autonomous", permissions={"write": {"prod": "auto"}})
    assert resolve_policy(stack)["write"]["prod"] == "ask"
    assert _decision("gcloud run deploy api --project=acme-prod", stack) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "git push --force origin main",
        "git push origin +main",
        "git push origin --delete staging",
        "psql $PROD_URL -c 'drop table users'",
        "terraform destroy -var env=prod",
        "gcloud sql instances delete acme-prod-db",
        "gh repo delete acme/app --yes",
    ],
)
def test_hard_limits_hold_under_autonomous(command: str) -> None:
    verdict = check(command, cwd=None, stack=_stack("autonomous"))
    assert verdict.decision == "deny", command
    assert verdict.hard_limit, command


def test_force_push_to_feature_branch_is_a_normal_push() -> None:
    assert _decision("git push --force-with-lease origin feat/x", _stack("balanced")) == "auto"


def test_overrides_win_over_preset() -> None:
    stack = _stack("balanced", permissions={"merge": "auto", "write": {"staging": "auto"}})
    assert _decision("gh pr merge 4", stack) == "auto"
    assert _decision("gcloud run deploy api --project=acme-staging", stack) == "auto"


def test_legacy_commit_push_keys_still_honored() -> None:
    stack = {"git": dict(GIT), "agent": {"commit": "ask", "push": "auto"}}
    assert _decision("git commit -m x", stack) == "ask"
    assert _decision("git push origin feat/x", stack) == "auto"


def test_explicit_targets_beat_name_heuristics() -> None:
    stack = _stack("balanced")
    stack["targets"] = {"prod": ["acme-7781"]}
    assert _decision("gcloud run deploy api --project=acme-7781", stack) == "deny"


def test_unnamed_remote_write_is_treated_as_prod() -> None:
    assert _decision("gcloud run deploy api", _stack("balanced")) == "deny"


def test_chained_command_takes_the_strictest_segment() -> None:
    cmd = "git commit -m x && git push origin feat/x && gh pr merge 9"
    assert _decision(cmd, _stack("balanced")) == "ask"


def _cli(command: str, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "check_permission.py"), "--command", command, "--cwd", str(root), "--check", *extra],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_exit_codes_and_approval(tmp_path: Path) -> None:
    (tmp_path / ".heyeddi").mkdir()
    (tmp_path / ".heyeddi" / "stack.json").write_text(json.dumps(_stack("balanced")))
    assert _cli("git commit -m x", tmp_path).returncode == 0
    asked = _cli("gh pr merge 1", tmp_path)
    assert asked.returncode == 2
    assert json.loads(asked.stdout)["decision"] == "ask"
    assert _cli("gh pr merge 1", tmp_path, "--approved").returncode == 0
    assert _cli("gcloud run deploy api --project=acme-prod", tmp_path, "--approved").returncode == 1


# Review finding (PR #64): env detection must not be spoofable into a laxer env.
@pytest.mark.parametrize(
    "command",
    [
        "gcloud run deploy api --project=10.0.0.5 # dev",
        "gcloud run deploy api --project=p\"\"rod-acme # dev",
        "kubectl apply -f k.yaml --context=10.1.1.1 --labels team=dev",
        "gcloud run deploy api --project=acme-7781 --tag=dev",
        "psql -h 10.0.0.9 -c 'update users set x=1' # localhost",
        "psql -h 10.0.0.9 -c 'update users set x=1' --set=dev",
    ],
)
def test_env_spoofing_cannot_downgrade_a_write(command: str) -> None:
    assert _decision(command, _stack("balanced")) == "deny", command


def test_quoted_prod_name_is_still_prod() -> None:
    verdict = check("gcloud run deploy api --project=acme-p\"\"rod", cwd=None, stack=_stack("autonomous"))
    assert verdict.env == "prod"


def test_explicit_dev_target_only_counts_in_a_target_flag() -> None:
    stack = _stack("balanced")
    stack["targets"] = {"dev": ["acme-dev-123"]}
    assert _decision("gcloud run deploy api --project=acme-dev-123", stack) == "auto"
    assert _decision("gcloud run deploy api --project=10.0.0.5 --description=acme-dev-123", stack) == "deny"


def test_legit_target_flags_still_resolve() -> None:
    stack = _stack("balanced")
    assert _decision("gcloud run deploy api --project acme-dev", stack) == "auto"
    assert _decision("kubectl --context staging apply -f k.yaml", stack) == "ask"
    assert _decision("psql -h localhost -c 'update users set x=1'", stack) == "auto"
