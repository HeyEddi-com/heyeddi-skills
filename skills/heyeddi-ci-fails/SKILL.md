---
name: heyeddi-ci-fails
description: "Diagnose and fix failing GitHub Checks on PR work by default: fetch evidence, write ephemeral ci-fails report, apply fixes, verify locally. Run automatically — do not wait for user to ask. Never merge without authorize merge. Companion to /heyeddi fails."
version: 1.1.0
product-version: 3.8.22
author: HeyEddi-com
disable-model-invocation: true
---

# HeyEddi CI Fails

Local agent counterpart to App `/heyeddi fails`: fetch failing Checks, write a diagnosis report, **fix actionable failures**, verify with evidenced commands. **Stack-agnostic** (log-driven).

## Default behavior (no confirmation)

Run this skill **automatically** on any PR work — open PR, PR branch, review request, or before `@heyeddi-pr-respond`. Do **not** wait for the user to mention CI or ask you to fix failures.

- **Always** fetch and diagnose failing Checks
- **Always** apply fixes when the diagnosis identifies actionable failures
- **Always** commit + push fixes as part of the PR workflow
- Only merge can need a question: merge follows `agent.permissions.merge` (default `ask`: the user says **authorize merge** in the current turn)

## Ephemeral artifacts (do not commit)

| File | Role |
|------|------|
| `pr-<N>-ci-fails-raw.json` | Raw gh evidence |
| `pr-<N>-ci-fails.md` | Diagnosis report |

Never commit these. GitHub Checks remain SSOT.

## Pipeline

```
fetch_failing_checks --pr <N>
write_ci_fails_report --pr <N> --force
→ fill likely cause / proposed fix from logs
apply fixes when diagnosis identifies actionable failures (default — do not ask)
discover_and_verify [--run]
assert_no_merge --check
→ commit + push to PR branch when fixes applied
```

Also tell the user they can comment `/heyeddi fails` on the PR for hosted App analysis (billable when that path applies).

## Hard rules

- Never invent failure causes without citing check evidence
- Never merge unless merge follows `agent.permissions.merge` (default `ask`: the user says **authorize merge** in the current turn)
- Never claim Spot/GHA jobs ran without Check or Spot evidence

## Tools

| Tool | Purpose |
|------|---------|
| `fetch_failing_checks` | Read-only failing Checks rollup |
| `write_ci_fails_report` | Write `pr-<N>-ci-fails.md` |
| `discover_and_verify` | Evidenced verify after fixes |
| `assert_no_merge` | Merge hard gate |

## Without the gh CLI

`gh` is optional. Every script here that talks to GitHub checks for it first. When `gh` is missing or logged out, the script prints `{"status": "degraded", ...}` with the reason and a `manual` list, and exits **3**.

- Exit 3 is not a pass and not a failure. It means the step could not run.
- Do not retry in a loop and do not report the step as done.
- Do the step by hand with the GitHub MCP tools named in `manual`; if that is not possible, keep going and list `gh auth login` under **Needs you**.
- Nothing is posted, verified or signed off when a script exits 3.

## When complete

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py \
  --current-skill heyeddi-ci-fails --project-root .
```
