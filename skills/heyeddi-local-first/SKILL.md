---
name: heyeddi-local-first
description: "ALWAYS-ON local-first gate for every agent. Prepare Terraform and config locally. terraform plan is allowed and must be summarized as a warning. classify_command.py --check exits 1 on terraform apply and other live cloud mutations. Use on any infra, Terraform, gcloud, Firebase, Kubernetes, or Google account change."
version: 1.0.0
product-version: 3.8.4
author: HeyEddi-com
---

# Local first

**Always on** for every agent that loads HeyEddi skills (Cursor, Claude, Codex, Cloud Run, or any other host). Edit code and Terraform in the repo. Check the plan. Do not change live systems.

This is the same kind of gate as `verify_setup --check`. The script exits 1 on a live mutation. Do not run that command.

## Hard gate

Before any Terraform, OpenTofu, Pulumi, gcloud, GAM, Firebase, kubectl, Helm, aws, gsutil, bq, or Google API write, run:

```bash
python .agents/skills/heyeddi-local-first/scripts/classify_command.py --check --command "<the exact command>"
```

From this hub, the script path is `skills/heyeddi-local-first/scripts/classify_command.py`.

| Exit | Meaning |
|------|---------|
| 0 and `"action": "allow"` | Run it. Reads and local config only. |
| 0 and `"action": "plan"` | Run it. Then warn the user with what the plan would create, change, or destroy. Stop. |
| 1 and `"blocked": true` | Do not run it. Edit the files instead. |

A plan command is `terraform plan`, `tofu plan`, `pulumi preview`, or `ansible-playbook --check`.

## Process

1. Change the Terraform, config, or app code in the working tree.
2. Run the checker on the plan command. Exit 0 with `action: plan` means run the plan.
3. Warn the user. Quote the resource addresses the plan would add, change, or destroy.
4. Commit and review that diff. Live apply stays in the project's deploy pipeline (Cloud Build `terraform-release` for HeyEddi CI) or in a terminal the human runs.

## What exits 1

- `terraform` / `tofu` `apply`, `destroy`, `import`, `refresh`, `state rm`, `workspace delete`
- `gcloud` writes (`delete`, `deploy`, `create`, `submit`, IAM changes). `list`, `describe`, `get`, `config`, and `auth` stay allowed.
- GAM writes, including calendar account changes. `gam info` and `gam print` stay allowed.
- `firebase deploy`, kubectl writes, `helm upgrade`, aws writes, `gsutil rm`, `bq` queries that are not `--dry_run`
- `curl -X POST`, PUT, PATCH, or DELETE to a Google API
- The same commands inside `bash -c`, `python -c`, `$(...)`, or a local `.sh` / `.py` script

`firebase emulators:start` is local and stays allowed.

## Tools

| Script | Purpose |
|--------|---------|
| `classify_command.py --check` | Exit 1 on a live mutation. Plan prints a warning and exits 0. |

## Related

- `@heyeddi` always-on list
- `@engineering-excellence` for the code change gate
- HeyEddi CI `cloudbuild.yaml` step `terraform-release` is the reviewed apply path
