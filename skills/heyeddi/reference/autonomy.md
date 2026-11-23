# Autonomy: run the request to completion

**Date:** 2026-11-23

This is the working contract for every HeyEddi skill. Where a skill says something else about asking, waiting, or reporting, this file wins.

## The rule

A request to build, fix, or change something approves the whole pipeline for it: plan gate, tests first, code, audits, cost estimate, visual QA, and the commit, push, and PR that `check_permission` allows. Do the work on a feature branch (a worktree when `git.worktrees` is true). The branch is the safety net. The user reviews the result and decides at merge.

"Implement these 3 features" means all 3, end to end, in one run.

## Never end the turn for

- A status report or a gate result
- Confirming a plan you were asked to carry out
- Choosing between reasonable options: pick the one the skill recommends and record why
- A cost estimate, even over budget (see the cost rule below)
- Scan or audit findings: fix the verified ones in the files you touch
- A next-step suggestion: if it is part of the request, run it yourself
- A missing optional tool (Penpot server, `gh`, DevTools MCP): use the documented fallback

## When information is missing

1. Read `.heyeddi/` (product.md, design.md, routing, stack.json).
2. Run the skill's read-only scripts.
3. Inspect the repo: code, OpenAPI, tests.
4. Still open: take the default the skill documents, or the most conservative reading, and record it. A decision that matters goes to `append_decision.py`; the rest goes under **Assumptions** in the final summary.
5. Keep going.

## The only pauses

| Pause | What to do |
|-------|-----------|
| `check_permission` exits 2 (ask) | Ask once for that step. Keep doing everything else. Batch it with other open questions. |
| `check_permission` exits 1 (deny) | Not a pause. Hand that one step to the user or the pipeline and finish the rest. |
| Two readings lead to a different data model, public API, or irreversible migration, and the repo cannot settle it | Build what does not depend on the answer, then ask once. |
| The request is itself a design or discovery conversation ("design", "redesign", "new look", `@heyeddi-design shape`, `@heyeddi-intake`) | The identity gate, brief confirmation, and discovery interview run as written. In a build request they do not stop: see `@taste-penpot` `references/identity-gate.md`. |
| A secret or login only the user has | Do the rest; list it under **Needs you**. |

## Cost

`estimate_change_cost.py` runs after edits and never stops the work. If the plan names a cost driver, put its $/month in the plan and continue. Over budget: keep the change on the branch and make the cost warning the first line of the final summary, with the range, top drivers, and the cheaper option. The merge is the decision point: `@pre-merge-gate` fails an over-budget change until the user approves it (`--approved "<reason>"`). When the user asked to hear about cost before building, warn first and continue only after their answer.

## Final summary

One message at the end, in this order. Leave out empty sections.

```markdown
**Cost:** over budget: $X to $Y/month, driver, cheaper option   ← only when over budget or a limit fires
**Done:** what changed, per feature
**Tests:** layers run (unit / integration / frontend), layers skipped and why
**Assumptions:** defaults you picked and where they are recorded
**Needs you:** batched questions, asks from check_permission, denied steps, missing secrets
**Next:** only work outside this request
```
