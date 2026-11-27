"""Audit fixes 6-11: the gates stop blocking harmless work and keep blocking live changes."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "skills" / "heyeddi-local-first" / "scripts"
HEYEDDI = ROOT / "skills" / "heyeddi" / "scripts"
sys.path.insert(0, str(GATE))
sys.path.insert(0, str(HEYEDDI))

import session_worktree as sw  # noqa: E402
import worktree_guard as guard  # noqa: E402
from check_permission import check  # noqa: E402
from classify_command import ACTION_ALLOW, ACTION_DENY, classify  # noqa: E402

STACK = {"git": {"environments": {"production": "main", "staging": "staging"}, "default_branch": "dev"}}
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=cwd, check=True, capture_output=True, env=ENV,
    )


@pytest.fixture(autouse=True)
def _clean_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)


def _decision(command: str, cwd: Path | None = None, preset: str = "balanced") -> str:
    return check(command, cwd=cwd, stack={**STACK, "agent": {"preset": preset}}).decision


# --- 6: scripts are judged by what they run, not by prose in them -------------------------


@pytest.mark.parametrize(
    "script",
    [
        "skills/engineering-excellence/scripts/estimate_change_cost.py",
        "skills/heyeddi-local-first/scripts/classify_command.py",
    ],
)
def test_required_skill_scripts_are_not_denied(script: str) -> None:
    assert _decision(f"python3 {script} --project-root .", cwd=ROOT) == "auto"


@pytest.mark.parametrize("test_file", ["tests/test_local_first_gate.py", "tests/test_permission_policy.py"])
def test_running_tests_that_only_mention_live_commands_is_allowed(test_file: str) -> None:
    assert _decision(f"python3 -m pytest {test_file}", cwd=ROOT) == "auto"


def test_comments_docstrings_and_imports_are_not_commands(tmp_path: Path) -> None:
    (tmp_path / "report.py").write_text(
        '"""Reads terraform show output."""\nfrom __future__ import annotations\n'
        "# terraform apply runs in the pipeline\nimport json\n",
        encoding="utf-8",
    )
    assert classify("python3 report.py", cwd=tmp_path).action == ACTION_ALLOW


@pytest.mark.parametrize(
    "source",
    [
        'import subprocess\nsubprocess.run(["terraform", "apply"])\n',
        'import subprocess\n"""docs"""\ncmd = "terraform apply -auto-approve"\nsubprocess.run(cmd, shell=True)\n',
        'import os\nos.system("gcloud projects delete acme")\n',
        'from helpers import sh\nsh("terraform destroy")\n',
        'import subprocess\nTF = ["terraform", "-chdir", "infra"]\nsubprocess.run([*TF, "apply"])\n',
        "def broken(:\n    terraform apply\n",
    ],
)
def test_a_script_that_really_applies_stays_denied(tmp_path: Path, source: str) -> None:
    (tmp_path / "go.py").write_text(source, encoding="utf-8")
    assert classify("python3 go.py", cwd=tmp_path).action == ACTION_DENY


@pytest.mark.parametrize(
    "source",
    [
        'import subprocess\ndef test_x():\n    subprocess.run(["terraform", "apply"])\n',
        'import subprocess\nCMD = "terraform apply"\ndef test_x():\n    subprocess.run(CMD, shell=True)\n',
        'import os\ndef test_x():\n    os.system("kubectl delete pod api")\n',
        'import subprocess, pytest\n@pytest.mark.parametrize("c", ["terraform apply"])\n'
        "def test_x(c):\n    subprocess.run(c, shell=True)\n",
    ],
)
def test_a_test_file_that_really_applies_stays_denied(tmp_path: Path, source: str) -> None:
    (tmp_path / "test_live.py").write_text(source, encoding="utf-8")
    assert classify("python3 -m pytest test_live.py", cwd=tmp_path).action == ACTION_DENY


def test_an_edited_copy_of_the_classifier_is_not_trusted(tmp_path: Path) -> None:
    body = (GATE / "classify_command.py").read_text(encoding="utf-8")
    (tmp_path / "classify_command.py").write_text(
        body + '\nimport os\nos.system("terraform apply")\n', encoding="utf-8"
    )
    assert classify("python3 classify_command.py", cwd=tmp_path).action == ACTION_DENY


@pytest.mark.parametrize(
    "script", sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("skills/*/scripts/*.py") if p.name[0] != "_")
)
def test_no_hub_skill_script_is_denied_as_a_live_command(script: str) -> None:
    assert classify(f"python3 {script} --project-root .", cwd=ROOT).action != ACTION_DENY


@pytest.mark.parametrize(
    "source",
    [
        'import subprocess, sys\nsubprocess.run([sys.executable, "-c", payload])\nCMD = "terraform apply"\n',
        'import subprocess\ncmd = build()\nsubprocess.run(["bash", "-c", cmd])\nHINT = "terraform apply"\n',
    ],
)
def test_a_test_file_running_an_unreadable_payload_stays_denied(tmp_path: Path, source: str) -> None:
    (tmp_path / "test_live.py").write_text(source, encoding="utf-8")
    assert classify("python3 -m pytest test_live.py", cwd=tmp_path).action == ACTION_DENY


# --- 7: prose in a commit message or PR body is not a command ------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m 'docs: run `terraform apply` from the pipeline'",
        "gh pr create --title x --body 'Run `terraform apply` after merge'",
        "gh pr create --title x --body \"$(cat <<'EOF'\nDeploy notes\nterraform apply runs in CI\nEOF\n)\"",
        "git commit -F - <<'EOF'\nfix: x\n\nterraform apply runs in CI\nEOF",
        "gh pr comment 3 --body-file - <<'EOF'\nterraform destroy is blocked, don't run it\nEOF",
    ],
)
def test_quoted_prose_is_not_run(command: str) -> None:
    assert _decision(command) == "auto"


@pytest.mark.parametrize(
    "command",
    [
        'git commit -m "x `terraform apply`"',
        'gh pr create --body "$(terraform apply)"',
        "git commit -m 'x' && terraform apply",
        "bash <<'EOF'\nterraform apply\nEOF",
        "cat <<'EOF' | sh\nterraform apply\nEOF",
        "cat > go.sh <<'EOF'\nterraform apply\nEOF\nbash go.sh",
        "git commit -m \"$(bash <<'EOF'\nterraform apply\nEOF\n)\"",
        "git commit -F - <<EOF\n$(terraform apply)\nEOF",
        "git commit -F - <<'EOF'\nmsg\nEOF\nterraform apply",
        "echo \"git commit -F - <<'EOF'\"\nterraform apply\nEOF",
        "bash -c \"git commit -m '$(terraform apply)'\"",
        "eval '$(terraform apply)'",
        "git commit -m x # '\nterraform apply",
    ],
)
def test_text_that_a_shell_would_run_stays_denied(command: str) -> None:
    assert _decision(command) == "deny"


def _mcp(payload: dict) -> str:
    proc = subprocess.run(
        [sys.executable, str(GATE / "hook_before_mcp.py")],
        input=json.dumps(payload), capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)["permission"]


def test_mcp_prose_fields_are_not_commands() -> None:
    body = "Release notes\nterraform apply runs in CI"
    assert _mcp({"tool_name": "create_pull_request", "tool_input": {"title": "x", "body": body}}) == "allow"


@pytest.mark.parametrize(
    "payload",
    [
        {"tool_name": "run_terminal", "tool_input": {"command": "terraform apply"}},
        {"tool_name": "create_pull_request", "tool_input": {"script": "terraform apply"}},
        {"tool_name": "execute_command", "tool_input": {"message": "terraform apply"}},
        {"tool_name": "send", "tool_input": {"input": "terraform apply"}},
        {"tool_name": "firebase_deploy", "tool_input": {}},
    ],
)
def test_mcp_commands_stay_denied(payload: dict) -> None:
    assert _mcp(payload) == "deny"


# --- 8: a local database is local, a remote file is read before it is trusted ----------------


@pytest.mark.parametrize(
    "command",
    [
        'psql -h localhost -U app -d appdb -c "INSERT INTO users VALUES (1)"',
        "psql -h 127.0.0.1 --dbname app_test -f seed.sql",
        "psql -h localhost --database=appdb -c 'delete from users'",
    ],
)
def test_local_database_writes_are_allowed(command: str) -> None:
    assert _decision(command) == "auto"


@pytest.mark.parametrize(
    "command",
    [
        "psql -h 10.0.0.9 -d appdb -c 'update users set x=1'",
        "psql -h localhost -d prod_app -c 'update users set x=1'",
        "psql -h localhost -d 'host=10.0.0.9 dbname=app' -c 'update users set x=1'",
        "psql -h localhost -d postgresql://db.internal/app -c 'update users set x=1'",
        "psql -h localhost -h 10.0.0.9 -d appdb -c 'update users set x=1'",
        "psql -d appdb -h db -c 'update users set x=1'",
    ],
)
def test_remote_database_writes_stay_denied(command: str) -> None:
    assert _decision(command) == "deny"


def test_sql_files_against_a_remote_database_are_inspected(tmp_path: Path) -> None:
    (tmp_path / "drop.sql").write_text("DROP TABLE users;\n", encoding="utf-8")
    (tmp_path / "fill.sql").write_text("insert into t values (1);\n", encoding="utf-8")
    (tmp_path / "read.sql").write_text("select count(*) from users;\n", encoding="utf-8")
    drop = check('psql "$PROD_DATABASE_URL" -f drop.sql', cwd=tmp_path, stack=STACK)
    assert (drop.decision, drop.hard_limit) == ("deny", True)
    assert _decision('psql "$PROD_DATABASE_URL" --file=fill.sql', cwd=tmp_path) == "deny"
    assert _decision('psql "$PROD_DATABASE_URL" -f missing.sql', cwd=tmp_path) == "deny"
    assert _decision('psql "$STAGING_DATABASE_URL" -f fill.sql', cwd=tmp_path) == "ask"
    assert _decision('psql "$PROD_DATABASE_URL" -f read.sql', cwd=tmp_path) == "auto"


# --- 10: a branch that starts with a number is a branch ---------------------------------------


@pytest.mark.parametrize("branch", ["42-add-login", "2fa-flow", "v2-api", "1234"])
def test_numbered_branches_push_without_asking(branch: str) -> None:
    assert _decision(f"git push -u origin {branch}") == "auto"


@pytest.mark.parametrize("tag", ["v1.2.0", "1.2.3", "v2", "v1.0.0-rc.1", "2026.11.1", "+v1.2.0", "refs/tags/x"])
def test_tag_pushes_still_ask(tag: str) -> None:
    assert _decision(f"git push origin {tag}") == "ask"


def test_an_existing_tag_with_any_name_still_asks(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "feat/x")
    _git(tmp_path, "commit", "-qm", "r", "--allow-empty")
    _git(tmp_path, "tag", "42-final")
    assert _decision("git push origin 42-final", cwd=tmp_path) == "ask"


# --- 11: the push is judged where it runs -----------------------------------------------------


@pytest.fixture()
def checkout(tmp_path: Path) -> tuple[Path, Path]:
    """A main checkout on `main` and a feature worktree."""
    main, feature = tmp_path / "main", tmp_path / "feature-wt"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    _git(main, "commit", "-qm", "r", "--allow-empty")
    _git(main, "worktree", "add", "-q", "-b", "feat/x", str(feature))
    return main, feature


@pytest.mark.parametrize(
    "command",
    [
        "git -C ../feature-wt push",
        "cd ../feature-wt && git push",
        "cd ../feature-wt && git push origin HEAD",
        "git -C ../feature-wt push -u origin HEAD",
    ],
)
def test_feature_worktree_push_is_not_a_production_push(checkout: tuple[Path, Path], command: str) -> None:
    main, _ = checkout
    assert _decision(command, cwd=main) == "auto"


@pytest.mark.parametrize(
    ("command", "start"),
    [
        ("git push origin HEAD", "main"),
        ("git push origin @", "main"),
        ("git push", "main"),
        ("git -C ../main push", "feature"),
        ("cd ../main && git push origin HEAD", "feature"),
        ("cd ../nowhere; git push", "feature"),
        ('cd "$DIR" && git push', "feature"),
        ("git -C ../nowhere push origin HEAD", "feature"),
    ],
)
def test_production_push_still_asks(checkout: tuple[Path, Path], command: str, start: str) -> None:
    main, feature = checkout
    cwd = main if start == "main" else feature
    assert _decision(command, cwd=cwd, preset="autonomous") == "ask"


def test_force_push_of_head_on_main_is_denied(checkout: tuple[Path, Path]) -> None:
    main, _ = checkout
    assert _decision("git push --force origin HEAD", cwd=main) == "deny"


# --- 9: the guard lets a locked-out session make its own worktree, and nothing else -----------


@pytest.fixture()
def claimed(tmp_path: Path) -> Path:
    """A plain checkout another session claimed."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "commit", "-qm", "r", "--allow-empty")
    sw.claim(repo, "s-owner", task="t", pr=None)
    (repo / "tools").mkdir()
    shutil.copy(HEYEDDI / "session_worktree.py", repo / "tools" / "session_worktree.py")
    return repo


def _guard(cwd: Path, command: str) -> str:
    event = {"session_id": "s-other", "cwd": str(cwd), "tool_name": "Bash", "tool_input": {"command": command}}
    return guard.decide(event)[0]


REAL = HEYEDDI / "session_worktree.py"


@pytest.mark.parametrize(
    "command",
    [
        "git worktree list",
        "git worktree list --porcelain",
        "git worktree add ../mine -b fix/x",
        "git worktree add -b fix/x ../mine origin/main",
        "git fetch",
        "git fetch origin main --prune",
        "git branch",
        "git branch -a -vv",
        "git branch --list 'fix/*'",
        "gh pr view 1 --json url",
        "gh pr list",
        "gh pr checks 1",
        "git status 2>&1",
        "git log --oneline 2>/dev/null | head -3",
        "cat README.md >/dev/null 2>&1",
        f"python3 {REAL} list --path .",
        f"python3 {REAL} check --path . --action commit",
        "python3 tools/session_worktree.py list",
        f"git worktree add ../mine -b fix/x && python3 {REAL} claim --path ../mine --task t",
    ],
)
def test_recovery_commands_are_allowed(claimed: Path, command: str) -> None:
    assert _guard(claimed, command) == "allow", command


@pytest.mark.parametrize(
    "command",
    [
        "git worktree add inside -b fix/x",
        "git worktree add -f ../mine main",
        "git worktree add -B main ../mine",
        "git worktree remove .",
        "git worktree prune",
        "cd .. && git worktree add mine",
        "git fetch origin main:main",
        "git fetch -u origin +main:main",
        "git fetch --upload-pack='rm -rf .' origin",
        "git pull",
        "git branch newname",
        "git branch -D main",
        "git branch -a newname",
        "git branch --list -d main",
        "gh pr checkout 1",
        "gh pr merge 1",
        "git status > notes.txt",
        "git status 2>errors.log",
        "echo x >/dev/nullx",
        "echo \\>/dev/null; rm -rf .",
        "cat <(rm -rf .)",
        "rm -rf . 2>/dev/null",
        f"python3 {REAL} claim --path .",
        f"python3 {REAL} claim --task t",
        f"python3 {REAL} handoff --path . --to s-other",
        "python3 evil/session_worktree.py list",
        f"python3 -c 'print(1)' {REAL} list",
    ],
)
def test_the_foreign_checkout_stays_unwritable(claimed: Path, command: str) -> None:
    (claimed / "evil").mkdir()
    (claimed / "evil" / "session_worktree.py").write_text("import shutil\n", encoding="utf-8")
    assert _guard(claimed, command) == "deny", command


# --- Ways around the narrower rules that must stay closed -------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m \"$(bash -c \"$(cat <<'EOF'\nterraform apply\nEOF\n)\")\"",
        "git commit -m \"$(eval $(cat <<'EOF'\nterraform apply\nEOF\n))\"",
        "echo ${x:- #}; terraform apply",
    ],
)
def test_nested_or_confusing_shell_text_stays_denied(command: str) -> None:
    assert _decision(command) == "deny"


@pytest.mark.parametrize(
    "source",
    [
        'import subprocess as sp\ndef test_x():\n    sp.run(["terraform", "apply"])\n',
        'from os import system\ndef test_x():\n    system("terraform apply")\n',
        'import asyncio\nasync def test_x():\n    await asyncio.create_subprocess_shell("terraform apply")\n',
    ],
)
def test_aliased_process_calls_in_tests_stay_denied(tmp_path: Path, source: str) -> None:
    (tmp_path / "test_live.py").write_text(source, encoding="utf-8")
    assert classify("python3 -m pytest test_live.py", cwd=tmp_path).action == ACTION_DENY


def test_a_connection_string_beside_a_database_name_stays_remote() -> None:
    assert _decision("psql -h localhost -d appdb 'host=10.0.0.9' -c 'update users set x=1'") == "deny"


def test_a_cd_that_may_not_run_does_not_hide_a_production_push(checkout: tuple[Path, Path]) -> None:
    main, _ = checkout
    assert _decision("true || cd ../feature-wt; git push", cwd=main, preset="autonomous") == "ask"


def test_sql_file_after_an_unknown_cd_is_not_trusted(tmp_path: Path) -> None:
    (tmp_path / "read.sql").write_text("select 1;\n", encoding="utf-8")
    assert _decision('cd "$DIR" && psql "$PROD_DATABASE_URL" -f read.sql', cwd=tmp_path) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        f"python3 {REAL} claim --path ../mine --user-a",
        f"python3 {REAL} claim --path ../mine --pa .",
        f"python3 {REAL} claim --path ../mine --path=.",
        "ls # note\nrm -rf .",
    ],
)
def test_abbreviated_flags_and_comments_do_not_open_the_guard(claimed: Path, command: str) -> None:
    assert _guard(claimed, command) == "deny", command
