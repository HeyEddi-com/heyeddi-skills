---
name: heyeddi-ci-fails
description: "Diagnose and fix failing GitHub Checks on PR work by default: fetch evidence, write ephemeral ci-fails report, apply fixes, verify locally. Run automatically: do not wait for user to ask. Never merge without authorize merge. Companion to /heyeddi fails."
version: 1.1.1
product-version: 3.9.0
author: HeyEddi-com
---

# HeyEddi CI Fails

Local agent counterpart to App `/heyeddi fails`: fetch failing Checks, write a diagnosis report, **fix actionable failures**, verify with evidenced commands. **Stack-agnostic** (log-driven).

## Default behavior (no confirmation)

Run this skill **automatically** on any PR work: open PR, PR branch, review request, or before `@heyeddi-pr-respond`. Do **not** wait for the user to mention CI or ask you to fix failures.

- **Always** fetch and diagnose failing Checks
- **Always** apply fixes when the diagnosis identifies actionable failures
- **Always** commit + push fixes as part of the PR workflow
- Merge into dev / test / staging yourself once `@pre-merge-gate --signoff` exits 0. A production merge takes the user's **authorize merge** in the current turn; never run it earlier.

## Ephemeral artifacts (do not commit)

| File | Role |
|------|------|
| `pr-<N>-ci-fails-raw.json` | Raw gh evidence (failing and pending checks) |
| `pr-<N>-ci-fails.md` | Diagnosis report |

Both are written to the system temp directory (the scripts print the paths), never into the project. GitHub Checks remain SSOT.

Pending is not green: `fetch_failing_checks` reports `pending_count` and `green`.

## Pipeline

```
fetch_failing_checks --pr <N>
write_ci_fails_report --pr <N> --force
→ fill likely cause / proposed fix from logs
apply fixes when diagnosis identifies actionable failures (default: do not ask)
discover_and_verify [--run]
→ commit + push to PR branch when fixes applied
gh pr checks <N> --watch                  → run in the background until every check finishes
gh run view <run-id> --log-failed         → read each failure; fix, commit, push, watch again
gh run rerun <run-id> --failed            → flaky or infrastructure failure with no code cause (once, then treat it as real)
→ @heyeddi-pr-respond when the PR has review feedback; then ship:
pre_merge_gate.py --signoff --project-root .  → (.agents/skills/pre-merge-gate/scripts/) fix every FAIL and rerun
assert_no_merge --check --base <baseRefName> --planned-command "gh pr merge <N>" --project-root .
gh pr merge <N> --merge                   → base below production: run it. Production base: only after authorize merge
```

Also tell the user they can comment `/heyeddi fails` on the PR for hosted App analysis (billable when that path applies).

## Hard rules

- Never invent failure causes without citing check evidence
- Merge into dev / test / staging yourself once `@pre-merge-gate --signoff` exits 0. A production merge takes the user's **authorize merge** in the current turn; never run it earlier.
- Never claim Spot/GHA jobs ran without Check or Spot evidence

## Tools

| Tool | Purpose |
|------|---------|
| `fetch_failing_checks` | Read-only failing Checks rollup |
| `write_ci_fails_report` | Write `pr-<N>-ci-fails.md` |
| `discover_and_verify` | Evidenced verify after fixes |
| `assert_no_merge` | Check right before a merge: production needs authorize merge |

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
