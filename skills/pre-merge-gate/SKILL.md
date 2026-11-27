---
name: pre-merge-gate
description: "Ship gate after review→respond: setup, stack tests/build/analyze, engineering + prose, optional UI contrast, and with --signoff/--pr also git-clean, CI checks, and unresolved review threads. Any FAIL exits 1. Use before claiming merge-ready or merging to main."
version: 2.0.2
product-version: 3.8.27
author: HeyEddi-com
---

# Pre-merge Gate

Final **merge readiness** gate. It does **not** replace `@heyeddi-pr-review` (line findings) or `@heyeddi-pr-respond` (thread replies).

## Flow

```
@heyeddi-pr-review   → inline findings (or Approve)
@heyeddi-pr-respond  → fix/decline + reply every thread
@pre-merge-gate --signoff   → this skill (local + PR CI + open threads)
→ below production: merge. Production: wait for authorize merge
→ any FAIL: fix it and run the gate again
```

## Subagents (default)

Run via **Task** `shell`: `pre_merge_gate.py`. Main chat triages FAIL rows and re-delegates fixes. See `reference/subagents.md`.

## When to use

- Before claiming merge-ready or merging to `main` / `dev`
- After `@heyeddi-pr-respond` finishes
- QA wants one green/red report

## Hard stop

The script **exits 1** if any check is `FAIL`. Do not treat a markdown `BLOCKED` report as merge-ready. Agents must not merge (or say merge-ready) unless the process exits 0 **with `--signoff` or `--pr <N>`**.

## Instructions

1. Preferred (PR open):

   ```bash
   python .agents/skills/pre-merge-gate/scripts/pre_merge_gate.py \
     --project-root . --signoff
   ```

   Or pin the PR: `--pr <N>` (implies sign-off).

2. Local-only smoke (no PR/CI/thread checks): omit `--signoff` / `--pr`.
3. Read the report: each check is PASS/FAIL/SKIP. Optional `--json` appends a machine payload.
4. Fix FAILs and re-run until exit 0.

**Eval / harness:** use `--skip-visual-audit` when Playwright is unavailable in the agent turn.

## Without the gh CLI

`gh` is optional for the local checks. The PR checks (`pr-checks`, `pr-review-threads`) need GitHub. When `gh` is missing or logged out they show **UNVERIFIED**, the overall verdict is **UNVERIFIED**, and the process exits **3**.

- A skipped HeyEddi Reviewer is a FAIL (its automatic passes are capped per PR): comment `/heyeddi review`, wait, rerun.
- UNVERIFIED is not a pass. Do not say merge-ready. Exit 0 is still the only sign-off.
- A real FAIL still wins: any FAIL gives BLOCKED and exit 1.
- `--signoff` with no `gh` used to skip the PR checks silently. It now reports them UNVERIFIED.
- Check CI and review threads by hand or with the GitHub MCP tools, or run `gh auth login` and re-run.

## Checks

### Always (stack-aware)

| Check | When |
|-------|------|
| setup-audit | `@heyeddi-setup verify_setup --check` |
| test / build / vue-tsc | `package.json` present (vue-tsc only if Vue deps) |
| backend-pytest / backend-f821 | `backend/` present |
| dart-analyze / flutter-test | `pubspec.yaml` present |
| duplicate-ui | skill installed |
| prose-audit | defaults + changed `*.md` globs from PR/diff |
| engineering-audit | `@engineering-excellence --check` |
| cost-estimate | `@engineering-excellence estimate_change_cost --check` (over budget → FAIL until the user approves, then pass `--cost-approved "<reason>"`) |
| contrast-audit | product routes (see visual rules) |

### Sign-off (`--signoff` or `--pr`)

| Check | Rule |
|-------|------|
| git-clean | dirty tree → FAIL. Gate reports, contrast audits, and skill auto-sync files do not count |
| git-pushed | unpushed commits → FAIL |
| pr-checks | `gh pr checks` failing/pending → FAIL. No checks reported passes only when the repo configures no CI |
| pr-review-threads | unresolved review threads → FAIL (run respond), except those declined as below |
| signoff-emergency-skips | `--skip-backend` / setup / engineering / cost → FAIL |
| visual | with a frontend, routes, and `.heyeddi/product.md`: missing Playwright or no reachable app → FAIL (not silent SKIP) |

### Declined threads

An unresolved thread passes only when its last reply is the PR author's and starts with `**Declined:**` followed by a reason. The report lists every such thread with its link and reason; repeat that list in the final summary. A later comment by anyone else makes the thread block again.

### Pending checks

Run `gh pr checks <N> --watch` in the background until they finish, then rerun the gate.

### Backend runner

With `uv.lock` / `[tool.uv]` or `poetry.lock` / `[tool.poetry]` (in `backend/` or the root), pytest and ruff run through `uv run` / `poetry run`. Install missing dependencies with the same tool. Otherwise `backend/.venv` or the system Python is used.

### Visual audit

SKIP when there is no frontend or `.heyeddi/product.md` lists no routes. With `DEV_SERVER_URL` set, that server is audited. Otherwise the gate starts `npm run dev` on a free port and stops it afterwards. A frontend without an `npm run dev` script (Flutter web): start it yourself, set `DEV_SERVER_URL`, and stop it when done.

### Approved cost

Only after the user approved the spend: `pre_merge_gate.py --signoff --cost-approved "<their reason>"`. The approval is recorded in `.heyeddi/docs/engineering/decisions.md`. Commit that entry and push, then rerun with the same flag; it is not recorded twice.

### Flags

- `--cost-approved "<reason>"`: pass the user's cost approval to `estimate_change_cost --approved`

- `--skip-duplicate-ui`, `--skip-prose-audit`, `--skip-visual-audit`, `--skip-flutter`, `--skip-git-clean`
- Emergency only (blocked under sign-off): `--skip-backend`, `--skip-engineering-audit`, `--skip-setup-audit`, `--skip-cost-estimate`
- `--no-pr` with `--signoff`: local sign-off without PR/CI/thread checks (still git-clean + emergency ban)

## Never

- Claim merge-ready without exit 0 under `--signoff` or `--pr`
- Use emergency skips for real merge sign-off
- Substitute this skill for code review or thread replies
- Treat SKIP as PASS when a required tree exists but tooling is missing

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill pre-merge-gate --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
