---
name: pre-merge-gate
description: Runs pre-merge checks (backend + frontend + engineering excellence + optional UI audit). Any FAIL exits 1 (hard stop). Use when QA approves a PR or before merge to main.
version: 1.2.0
product-version: 3.4.7
author: HeyEddi-com
disable-model-invocation: true
---

# Pre-merge Gate

## Subagents (default)

Run gate via **Task** `shell` subagent: `pre_merge_gate.py`. Main chat triages FAIL lines and re-delegates fixes. See `reference/subagents.md`.

## When to use

- QA wants a single green/red report before approving a PR
- Before merging to `main` / `dev`
- After addressing review feedback: confirm all gates pass

## Hard stop

The script **exits 1** if any check is `FAIL`. Do not treat a markdown `BLOCKED` report with exit 0 as merge-ready — that bug is fixed. Agents must not merge (or say merge-ready) unless the process exits 0.

## Instructions

1. Run `python .agents/skills/pre-merge-gate/scripts/pre_merge_gate.py --project-root <root>`.
2. Read the markdown report: each check shows PASS/FAIL/SKIP.
3. Fix failing checks and re-run until exit code is 0.

**Eval / harness turns:** When the eval harness captures Playwright proof separately, run with `--skip-visual-audit` so the gate does not invoke contrast audit (no Playwright in agent turn).

## Checks

**Required when the tree exists**

- npm test + production build (`package.json`)
- `vue-tsc --noEmit` when `node_modules` is present (FAIL if frontend exists but toolchain missing)
- `backend` pytest (`backend/tests`, prefers `backend/.venv`)
- ruff **F821** on `backend/app` (undefined names / dropped imports)
- **engineering audit** (`@engineering-excellence` `audit_engineering --check`: errors fail; warns advisory)

**Optional (SKIP allowed if skill/tool missing; FAIL still hard-stops)**

- duplicate UI scan (`no-duplicate-ui`)
- prose audit (`heyeddi-design` `verify_prose.py`) — always-on for copy; skip only in emergency
- contrast audit on product routes (`visual-auditor`; SKIP if Playwright missing)

Flags: `--skip-duplicate-ui`, `--skip-prose-audit`, `--skip-engineering-audit`, `--skip-visual-audit`. `--skip-backend` and `--skip-engineering-audit` are emergency-only and must not be used for merge sign-off.

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
