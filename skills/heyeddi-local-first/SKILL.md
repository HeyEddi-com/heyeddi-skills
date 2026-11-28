---
name: heyeddi-local-first
description: "ALWAYS-ON permission and local-first gate for every agent. check_permission.py decides allow / ask / deny for commit, push, PR, merge, release, and dev / staging / prod reads and writes from the agent preset in .heyeddi/stack.json (default balanced). terraform plan is allowed and must be summarized. Use before any git write, gh write, publish, database client, infra, Terraform, gcloud, Firebase, Kubernetes, or Google account change."
version: 1.0.1
product-version: 3.10.0
author: HeyEddi-com
---

# Local first

**Always on** for every agent that loads HeyEddi skills (Cursor, Claude, Codex, Cloud Run, or any other host). Edit code and Terraform in the repo. `check_permission.py` alone decides what may run against a live system: under `balanced`, reads run, dev writes run, staging writes ask once, and prod writes are denied.

## Permission gate

Before commit, push, PR writes, merge, release or publish, a database client, or any Terraform, OpenTofu, Pulumi, gcloud, GAM, Firebase, kubectl, Helm, aws, gsutil, bq, or Google API command, run:

```bash
python .agents/skills/heyeddi-local-first/scripts/check_permission.py --check --command "<the exact command>"
```

From this hub, the script path is `skills/heyeddi-local-first/scripts/check_permission.py`.

| Exit | `decision` | Agent does |
|------|-----------|------------|
| 0 | `auto` | Run it. No question, no status report. |
| 2 | `ask` | Ask once. Batch it with any other open question. On a yes, rerun with `--approved` and continue. Keep working on everything else while you wait. |
| 1 | `deny` | Never run it, not through `bash -c`, a script, or an API. Hand that one step to the user or the deploy pipeline and finish the rest of the task. |

The policy is `agent.preset` plus `agent.permissions` in `.heyeddi/stack.json` (`@heyeddi-setup` `reference/stack-schema.md`). No policy means `balanced`:

| Action | `balanced` |
|--------|-----------|
| Commit, push a feature branch, open or update a PR, rerun CI | auto |
| Merge into dev, test, staging, or a stacked parent (after `@pre-merge-gate --signoff` exits 0) | auto |
| Merge or push into the production branch (never better than ask, under any preset) | ask |
| Push to the staging branch, release, publish, push a tag | ask |
| Read dev, staging, prod (logs, describe, `SELECT`, look-and-navigate) | auto |
| Write dev | auto |
| Write staging | ask |
| Write prod | deny (deploy pipeline) |

Hard limits, under every preset: force push or delete on a protected branch, destructive statements on prod (`DROP`, `TRUNCATE`, `delete`, `destroy`), `gh repo delete`, prod writes never better than `ask`.

The env comes from the command's shell words, with quotes removed and `# comments` dropped. A prod name anywhere (or a `targets.prod` entry from `stack.json`) makes it prod. Dev or staging come only from target values: `--project`, `--context`, `--host`, `--profile` and similar flags, connection URLs, and `$..._URL` variables, and only when every target value agrees. An IP, an unnamed target, or a label like `--tags=dev` never lowers it: an unnamed remote write counts as prod.

`classify_command.py` stays as the infra classifier underneath. `"action": "plan"` (`terraform plan`, `tofu plan`, `pulumi preview`, `ansible-playbook --check`) runs; summarize what it would create, change, or destroy, then keep going.

A plan command is `terraform plan`, `tofu plan`, `pulumi preview`, or `ansible-playbook --check`.

## Process

1. Change the Terraform, config, or app code in the working tree.
2. Run the gate on the plan command. Exit 0 means run the plan.
3. Warn the user. Quote the resource addresses the plan would add, change, or destroy.
4. Commit and review that diff. Run an apply when `check_permission.py` allows that exact command (a named dev target; staging after one yes). A prod apply stays in the project's deploy pipeline (Cloud Build `terraform-release` for HeyEddi CI). Then keep going with the rest of the task.

## What counts as a live write

Under `balanced` these run on dev, ask on staging, and are denied on prod or an unnamed target.

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
| `check_permission.py --check` | The gate. Exit 0 allow, 2 ask, 1 deny. `--approved` after the user's yes. |
| `classify_command.py --check` | Internal to the gate: spots live infrastructure writes. Its exit 1 means "live write", not "forbidden"; `check_permission.py` decides. |

## Related

- `@heyeddi` always-on list
- `@engineering-excellence` for the code change gate
- HeyEddi CI `cloudbuild.yaml` step `terraform-release` is the reviewed apply path
