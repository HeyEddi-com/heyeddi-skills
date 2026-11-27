# Autonomy: run the request to completion

**Date:** 2026-11-26

This is the working contract for every HeyEddi skill. Where a skill says something else about asking, waiting, or reporting, this file wins.

## The rule

A request to build, fix, or change something approves the whole pipeline for it: plan gate, tests first, code, audits, cost estimate, visual QA, and the commit, push, and PR that `check_permission` allows. Do the work on a feature branch (a worktree when `git.worktrees` is true). The branch is the safety net. Merging into dev, test, or staging is part of the request: pass `@pre-merge-gate --signoff` (fix every FAIL and rerun), then merge. Only a production merge waits for the user.

"Implement these 3 features" means all 3, end to end, in one run.

## Never end the turn for

- A "go". A request or an approved plan covers every step, phase, and ticket in it. Finish one, start the next. `scripts/finish_guard.py` is a Stop hook that sends the agent back to work

- A status report or a gate result
- Confirming a plan you were asked to carry out
- Choosing between reasonable options: pick the one the skill recommends and record why
- A cost estimate, even over budget (see the cost rule below)
- Scan or audit findings: fix the verified ones in the files you touch
- A next-step suggestion: if it is part of the request, run it yourself
- A missing optional tool (Penpot server, `gh`, DevTools MCP): use the documented fallback

## Finish before you report

A list of things you did not do is not a result. Do them.

Before the final summary, go through the request item by item and check the branch against it. Whatever the request needs to work is part of the request: the code, the wiring behind the UI, error and empty states, tests, migrations, config, docs, and the failures your change causes. If an item is missing, half-built, stubbed, untested, or failing, go back and do it. Repeat until the check is clean.

Silence in a doc, spec, plan, brief, or ticket is not a reason to skip anything. Documents never list everything. Decide how the missing piece should work, build it, and record the choice.

Never write "not done", "I did not do", "not covered", "the doc does not say", "remaining work", or "follow-up" about work you can do. The only items that may stay open are the ones in **The only pauses** below, each with the exact error or missing access that blocks it.

A check you are allowed to run is yours to run. "I haven't checked whether there is data; look before merging" is unfinished work: run the read (`check_permission` allows reads on dev, staging, and prod under `balanced`) and report what you found.

A tool or package the work needs is yours to add: declare it in the project's dependencies, install it, and run the project's own script. "This machine doesn't seem to have Poetry" is never a result, and calling around the script is not the fix.

Never ask to commit, push a feature branch, or open or update a PR when `check_permission` exits 0, in this repo or a second one the user named. Never go into a sibling folder on your own (`reference/session-worktrees.md`).

## The backlog

The backlog is work to do, not a place to park it. When the request is done, take the next backlog item you can do and do it, one branch and PR each, until none is left that you can do. Never move a doable item to the backlog, and never end a run by listing doable items. Only an item blocked on something in **The only pauses** stays.

## When information is missing

1. Read `.heyeddi/` (product.md, design.md, routing, stack.json).
2. Run the skill's read-only scripts.
3. Inspect the repo: code, OpenAPI, tests.
4. Still open: take the default the skill documents, or the reading that delivers a complete working feature, and record it. Careful applies to destructive and irreversible steps, not to how much of the request you build. A decision that matters goes to `append_decision.py`; the rest goes under **Assumptions** in the final summary.
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

One message at the end, in this order. Leave out empty sections. Every PR, issue, commit, or CI run named here is a full URL link, never a bare `#64`.

```markdown
**Cost:** over budget: $X to $Y/month, driver, cheaper option   ← only when over budget or a limit fires
**Done:** what changed, per feature, with links: PR, commits, CI runs
**Tests:** layers run (unit / integration / frontend), layers skipped and why
**Assumptions:** defaults you picked and where they are recorded
**Needs you:** only what you cannot do yourself: batched questions from the pause table, asks from check_permission, denied steps, missing secrets or logins
**Next:** new work nobody asked for, one line at most. Never leftovers from this request
```
