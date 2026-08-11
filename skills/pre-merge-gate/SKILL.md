---
name: pre-merge-gate
description: Runs pre-merge checks (tests, build, types, optional UI audit) and returns a markdown pass/fail report. Use when QA approves a PR or before merge to main.
version: 1.0.0
product-version: 3.4.2
author: HeyEddi-com
disable-model-invocation: true
---

# Pre-merge Gate

## Subagents (default)

Run gate via **Task** `shell` subagent: `pre_merge_gate.py`. Main chat triages FAIL lines and re-delegates fixes. See `reference/subagents.md`.

## When to use

- QA wants a single green/red report before approving a PR
- Before merging frontend-heavy changes
- After addressing review feedback: confirm all gates pass

## Instructions

1. Run `python scripts/pre_merge_gate.py --project-root <root>`.
2. Read the markdown report: each check shows PASS/FAIL/SKIP.
3. Fix failing checks and re-run until all required checks pass.

**Eval / harness turns:** When the eval harness captures Playwright proof separately, run with `--skip-visual-audit` so the gate does not invoke `audit_ui.py` (no dev server in agent turn).

## Checks

- npm test (if script exists)
- verify build
- vue-tsc (if available)
- duplicate UI scan (`no-duplicate-ui` when installed)
- prose audit on Vue/locale copy (`heyeddi-design` `verify_prose.py` when installed)
- visual audit on product routes (`visual-auditor` when installed; skips if Playwright missing)

Use `--skip-duplicate-ui`, `--skip-prose-audit`, or `--skip-visual-audit` to omit optional UI gates.
## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill (not after every tool call or subagent phase), suggest what to run next:

1. Run:

   ```bash
   python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py --current-skill pre-merge-gate --project-root .
   ```

   Add `--route /path` if you worked a specific route.

2. Include the script's **`### Next step`** block in your **final** reply. The user copies the **Prompt** line into chat (e.g. `@heyeddi-design craft /settings`).

Pass `--mode shape` (or `craft`, `audit`, etc.) when you know which sub-command just finished.

See `@heyeddi-orchestrator` → `reference/next-skill-handoff.md`.

