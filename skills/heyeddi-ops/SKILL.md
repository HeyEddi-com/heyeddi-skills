---
name: heyeddi-ops
description: "Operating documents for a system: threat model with accepted risks, runbook (setup, verify, failure, rotation, rollback, teardown) and blameless incident lessons under .heyeddi/docs/ops/. Use for infrastructure changes, a new hosted service, a leaked secret, a production failure, or a teardown. Not for code audits (engineering-excellence) or merge checks (pre-merge-gate)."
version: 1.0.0
product-version: 3.11.0
author: HeyEddi-com
---

# HeyEddi Ops

Write down how a system is protected, run, recovered and removed, before someone needs it.

## When to use

- A change adds or moves infrastructure, or a new hosted service
- A secret leaked
- Something failed in production
- A service or environment is being torn down

## Instructions

1. `python scripts/ops_docs.py --project-root <root> --init --service <name>`. It never overwrites.
2. Fill every `TODO` from the repository, configs and recorded decisions. Do not hand the user a blank form. Unknown after looking: write "Not verified" and what would settle it.
3. Mark each step as run, read or not verified, with the date.
4. `python scripts/ops_docs.py --project-root <root> --check` until it passes.

Never write a secret's value, a person's name, or an account id into these files.

## Documents under `.heyeddi/docs/ops/`

| File | Content |
|------|---------|
| `threat-model.md` | Assets, threats and controls, accepted risks with reasons |
| `runbooks/<service>.md` | Setup, Verify, Failure, Rotation, Rollback, Teardown |
| `lessons.md` | Per incident: symptom, cause, fix, lesson |

## Leaked secret

In this order: revoke it, issue a new one, check the access logs, then clean history. Deleting the file is not a fix.

## Teardown

Read the plan, destroy in reverse build order, list what is left and what still bills, then revoke credentials.

Destructive commands and anything touching a hosted environment go through `@heyeddi-local-first` `check_permission.py` first. This skill writes documents; it does not run teardown, rotation or restore against a live system without that permission.

## Chain

- `@engineering-excellence`: habits that apply to every change
- `@heyeddi-local-first`: permission before any live action

## When the task is complete

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi-ops --project-root .
```
