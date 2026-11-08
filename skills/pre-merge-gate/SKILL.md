---
name: pre-merge-gate
description: "Ship gate after review→respond: setup, stack tests/build/analyze, engineering + prose, optional UI contrast, and with --signoff/--pr also git-clean, CI checks, and unresolved review threads. Any FAIL exits 1. Use before claiming merge-ready or merging to main."
version: 2.0.0
product-version: 3.8.14
author: HeyEddi-com
disable-model-invocation: true
---

# Pre-merge Gate

Final **merge readiness** gate. It does **not** replace `@heyeddi-pr-review` (line findings) or `@heyeddi-pr-respond` (thread replies).

## Flow

```
@heyeddi-pr-review   → inline findings (or Approve)
@heyeddi-pr-respond  → fix/decline + reply every thread
@pre-merge-gate --signoff   → this skill (local + PR CI + open threads)
→ authorize merge
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
| contrast-audit | product routes (see visual rules) |

### Sign-off (`--signoff` or `--pr`)

| Check | Rule |
|-------|------|
| git-clean | dirty tree → FAIL |
| git-pushed | unpushed commits → FAIL |
| pr-checks | `gh pr checks` failing/pending → FAIL |
| pr-review-threads | unresolved review threads → FAIL (run respond) |
| signoff-emergency-skips | `--skip-backend` / setup / engineering → FAIL |
| visual | if `.heyeddi/product.md` exists, missing Playwright → FAIL (not silent SKIP) |

### Flags

- `--skip-duplicate-ui`, `--skip-prose-audit`, `--skip-visual-audit`, `--skip-flutter`, `--skip-git-clean`
- Emergency only (blocked under sign-off): `--skip-backend`, `--skip-engineering-audit`, `--skip-setup-audit`
- `--no-pr` with `--signoff`: local sign-off without PR/CI/thread checks (still git-clean + emergency ban)

## Never

- Claim merge-ready without exit 0 under `--signoff` or `--pr`
- Use emergency skips for real merge sign-off
- Substitute this skill for code review or thread replies
- Treat SKIP as PASS when a required tree exists but tooling is missing

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py \
  --current-skill pre-merge-gate --project-root .
```

Include the script's `### Next step` in your final reply.
