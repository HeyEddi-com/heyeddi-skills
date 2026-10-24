"""Local-first gate: plan is allowed, live mutations are denied."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "heyeddi-local-first" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from classify_command import ACTION_ALLOW, ACTION_DENY, ACTION_PLAN, classify  # noqa: E402


def _action(command: str, cwd: Path | None = None) -> str:
    return classify(command, cwd=cwd).action


def test_terraform_plan_is_a_warning_not_a_block() -> None:
    decision = classify("terraform -chdir=infra plan -out=/tmp/production.tfplan")
    assert decision.action == ACTION_PLAN
    assert decision.tool == "terraform"
    assert _action("terraform plan -destroy") == ACTION_PLAN
    assert _action("tofu plan") == ACTION_PLAN


def test_terraform_apply_and_destroy_are_denied() -> None:
    for command in (
        "terraform apply",
        "terraform apply -auto-approve",
        "terraform -chdir=infra apply -auto-approve tfplan",
        "terraform -chdir infra destroy",
        "terraform import google_project_service.calendar calendar.googleapis.com",
        "terraform state rm google_service_account.calendar",
        "terraform workspace delete production",
        "terraform refresh",
        "tofu apply",
    ):
        assert _action(command) == ACTION_DENY, command


def test_terraform_reads_stay_allowed() -> None:
    for command in (
        "terraform fmt -check",
        "terraform validate",
        "terraform init -input=false",
        "terraform state list",
        "terraform output -raw api_service_name",
        "terraform workspace select production",
    ):
        assert _action(command) == ACTION_ALLOW, command


def test_wrappers_and_chained_apply_are_denied() -> None:
    assert _action("cd infra && terraform apply -auto-approve") == ACTION_DENY
    assert _action("sudo terraform apply") == ACTION_DENY
    assert _action('bash -c "terraform apply -auto-approve"') == ACTION_DENY
    assert _action("echo $(terraform apply)") == ACTION_DENY
    assert _action("terraform plan && terraform apply") == ACTION_DENY
    assert _action('python3 -c "subprocess.run([\'terraform\', \'apply\'])"') == ACTION_DENY


def test_echo_of_the_word_apply_is_not_a_live_change() -> None:
    assert _action('echo "terraform apply is not this command"') == ACTION_ALLOW


def test_script_that_applies_is_denied(tmp_path: Path) -> None:
    script = tmp_path / "apply.sh"
    script.write_text("#!/bin/sh\nterraform apply -auto-approve\n", encoding="utf-8")
    assert _action(f"bash {script}", cwd=tmp_path) == ACTION_DENY
    assert _action(str(script), cwd=tmp_path) == ACTION_DENY


def test_gcloud_and_workspace_writes_are_denied() -> None:
    assert _action("gcloud compute instances list") == ACTION_ALLOW
    assert _action("gcloud config set project heyeddi") == ACTION_ALLOW
    assert _action("gcloud projects delete heyeddi") == ACTION_DENY
    assert _action("gcloud run deploy heyeddi-production-api --image=x --quiet") == ACTION_DENY
    assert _action("gcloud builds submit") == ACTION_DENY
    assert _action("gcloud iam service-accounts keys create key.json --iam-account=x") == ACTION_DENY
    assert _action("gam update user eddi@heyeddi.com calendar") == ACTION_DENY
    assert _action("gam info user eddi@heyeddi.com") == ACTION_ALLOW
    assert (
        _action("curl -X POST https://www.googleapis.com/calendar/v3/calendars -d '{}'")
        == ACTION_DENY
    )
    assert _action("curl -s https://www.googleapis.com/calendar/v3/users/me/calendarList") == ACTION_ALLOW


def test_firebase_kubectl_helm_aws_pulumi() -> None:
    assert _action("firebase deploy --only functions") == ACTION_DENY
    assert _action("firebase emulators:start") == ACTION_ALLOW
    assert _action("kubectl get pods") == ACTION_ALLOW
    assert _action("kubectl delete pod api") == ACTION_DENY
    assert _action("helm upgrade api ./chart") == ACTION_DENY
    assert _action("helm list") == ACTION_ALLOW
    assert _action("aws s3 ls") == ACTION_ALLOW
    assert _action("aws s3 rm s3://bucket/key") == ACTION_DENY
    assert _action("aws eks update-kubeconfig --name prod") == ACTION_ALLOW
    assert _action("pulumi preview") == ACTION_PLAN
    assert _action("pulumi up --yes") == ACTION_DENY
    assert _action("gsutil ls gs://heyeddi-terraform-state") == ACTION_ALLOW
    assert _action("gsutil rm gs://bucket/object") == ACTION_DENY
    assert _action("bq ls") == ACTION_ALLOW
    assert _action("bq query --nouse_legacy_sql 'DELETE FROM t'") == ACTION_DENY


def test_check_exits_1_on_apply_and_0_on_plan() -> None:
    script = SCRIPTS / "classify_command.py"

    def run(command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), "--check", "--command", command],
            text=True,
            capture_output=True,
            check=False,
        )

    plan = run("terraform plan")
    assert plan.returncode == 0
    plan_body = json.loads(plan.stdout)
    assert plan_body["action"] == "plan"
    assert "Do not apply" in plan_body["warning"]
    denied = run("terraform apply -auto-approve")
    assert denied.returncode == 1
    assert json.loads(denied.stdout)["blocked"] is True


def test_hook_json_for_plan_and_apply() -> None:
    hook = SCRIPTS / "hook_before_shell.py"

    def run(command: str) -> dict:
        proc = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps({"command": command, "cwd": "/tmp"}),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)

    plan = run("terraform plan")
    assert plan["permission"] == "allow"
    assert "warn" in plan["agent_message"]
    denied = run("terraform apply -auto-approve")
    assert denied["permission"] == "deny"
    assert "Blocked live change" in denied["user_message"]


def test_install_user_hook_merges(tmp_path: Path) -> None:
    cursor = tmp_path / "cursor"
    cursor.mkdir()
    (cursor / "hooks.json").write_text(
        json.dumps({"version": 1, "hooks": {"beforeShellExecution": [{"command": "echo keep"}]}}),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "install_user_hook.py"), "--cursor-dir", str(cursor)],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Installed" in proc.stdout
    data = json.loads((cursor / "hooks.json").read_text(encoding="utf-8"))
    commands = [entry["command"] for entry in data["hooks"]["beforeShellExecution"]]
    assert "echo keep" in commands
    assert any(command.endswith("./hooks/hook_before_shell.py") for command in commands)
    assert (cursor / "hooks" / "classify_command.py").is_file()
    assert data["hooks"]["beforeMCPExecution"][0]["failClosed"] is True
