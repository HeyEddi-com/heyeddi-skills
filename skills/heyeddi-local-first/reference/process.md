# Local-first process

**Date:** 2026-10-23

Any agent that has this skill follows the same gate. The host does not matter.

## Order

1. Edit files in the repo.
2. `terraform fmt` and `terraform validate` when Terraform changed. Run `classify_command.py --check` first. Those commands are `allow`.
3. `terraform plan`. The checker returns `action: plan` and exit 0.
4. Reply with a warning: resources to add, change, and destroy. If the plan is empty, say that.
5. Leave apply to Cloud Build `terraform-release` after the diff is reviewed, or to a human terminal.

## Checker

```bash
python .agents/skills/heyeddi-local-first/scripts/classify_command.py --check --command "terraform plan"
```

Exit 1 means the command is a live change. Do not run it. Do not wrap it in `bash -c`, a script, or an API call to get past the checker.

## Deploy path

`terraform-release` still runs `terraform apply -auto-approve` on a saved plan after merge, and it still refuses plans that delete a non-IAM resource. Agents do not start that step with `gcloud builds submit`.
