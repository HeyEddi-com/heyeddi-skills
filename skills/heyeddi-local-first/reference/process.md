# Local-first process

**Date:** 2026-11-26

Any agent that has this skill follows the same gate. The host does not matter.

## Order

1. Edit files in the repo.
2. `terraform fmt` and `terraform validate` when Terraform changed.
3. `terraform plan`. Summarize the resources to add, change, and destroy, or say the plan is empty, and keep going.
4. Before any command that changes a live system, run the gate on the exact command.
5. Exit 0: run it. Exit 2: ask once, keep working, rerun with `--approved` on a yes. Exit 1: leave that one step to the deploy pipeline or the user and finish the rest.

## Gate

```bash
python .agents/skills/heyeddi-local-first/scripts/check_permission.py --check --command "terraform plan"
```

`check_permission.py` is the only gate. It uses `classify_command.py` internally to spot infrastructure writes. A denied command stays denied: do not wrap it in `bash -c`, a script, or an API call to get past the checker.

## Deploy path

`terraform-release` runs `terraform apply -auto-approve` on a saved plan after merge, and it still refuses plans that delete a non-IAM resource. Agents do not start that step with `gcloud builds submit`.
