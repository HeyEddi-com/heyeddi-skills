# PR workflows

**Date:** 2026-11-07

HeyEddi splits pull request work into **skills** with distinct roles. Use the right one - they are not interchangeable.

## Overview

| Workflow | Skill | Who | When |
|----------|-------|-----|------|
| **1. Review submitted PR** | `@heyeddi-pr-review` | Reviewer, QA, or author self-check | Inline line findings (not merge gates) |
| **2. Respond to PR review** | `@heyeddi-pr-respond` | PR author | Every thread (same GitHub user ok) |
| **3. Merge readiness** | `@pre-merge-gate --signoff` | Author / QA | After respond; before merge-ready claim |

```
@heyeddi-pr-review  → inline findings (or Approve)
@heyeddi-pr-respond → fix/decline + reply every thread
@pre-merge-gate --signoff → clean tree, CI green, threads resolved or declined with a reason
→ merge (below production) · production waits for authorize merge
```

## Workflow 1 - Review submitted PR

**Invoke:** `@heyeddi-pr-review` + PR number

**Scope rule:** Only committed changes (`base...head`). Ignore uncommitted files.

### Pipeline

1. `fetch_pr_context` - changed files and categories
2. Read the committed patch (`gh pr diff`) and the related call sites
3. `post_inline_review` - real findings on exact lines (`<!-- heyeddi-pr-review -->`); zero findings → Approve (your own PR: posted as a comment)
4. `verify_inline_review --check`
5. Do **not** run `@pre-merge-gate` inside review (that is step 3 after respond)

### Output

Inline GitHub review comments on the committed diff. Lint/CI/merge gates stay with `@pre-merge-gate`.

### Example prompt

```
@heyeddi-pr-review Review PR #42 - committed changes only.
Leave real findings as inline comments (security, logic, related call sites).
```

## Workflow 2 - Respond to PR review

**Invoke:** `@heyeddi-pr-respond` + PR number

Covers human reviewers, HeyEddi CI root summaries, inline threads, and discussion comments.

### Pipeline

1. `fetch_pr_comments` + `build_comment_inventory --write-cache`
2. Tracking in chat (every inventory item)
3. Fix vs decline each item; commit + push before Fixed replies. Valid but out of scope: its own branch and PR
4. `post_thread_replies --replies-text` + `verify_response --use-inventory --live`. Fixed replies resolve their thread; every other reply starts with `**Declined:** <reason>`
5. `gh pr checks <N> --watch`; read failures with `gh run view <run-id> --log-failed`, fix, push, watch again
6. Below production, merge once `@pre-merge-gate --signoff` exits 0. A production merge takes **authorize merge** in the current turn

### Example prompt

```
@heyeddi-pr-respond Handle review feedback on PR #42.
```

### vs `/babysit`

| Tool | Use when |
|------|----------|
| `/babysit` | Fast merge-ready loop |
| `@heyeddi-pr-respond` | Team rules - every comment, fix matrix, threaded replies |

**Removed:** `@heyeddi-ci-respond` - deleted; use `@heyeddi-pr-respond` only.

## Delegation map

| Concern | Workflow 1 | Workflow 2 |
|---------|------------|------------|
| Product / AC | not part of review | fix-vs-decline uses PR goals |
| Engineering | findings in the diff | fixes + `@engineering-excellence` audit |
| Visual / UX | not part of review | only if comment is visual |
| CI / tests / ship | not part of review | `@pre-merge-gate --signoff` after threads |
| GitHub | optional review | **required** threaded replies |

## Artifacts (`.heyeddi/docs/`) - local / gitignored / not for commit

These files are **ephemeral session scratch** for agent verify gates. **Do not commit them.** GitHub PR threads (and posted `gh pr review`) are the SSOT.

| File | Workflow | Commit? |
|------|----------|---------|
| `pr-<N>-context.json` | Cached fetch_pr_context | No - gitignore |
| `pr-<N>-ci-*` | **Deprecated** - delete if present | No |

## Eval cases

```bash
uv run poe eval-pr-submission   # workflow 1 - fixture diff
uv run poe eval-pr              # workflow 2 - fixture comments
```

## Related docs

- [team-cheat-sheet.md](./team-cheat-sheet.md) - quick invoke table
- [heyeddi-folder.md](./heyeddi-folder.md) - `.heyeddi/docs/` layout
- [subagent-delegation.md](./subagent-delegation.md) - Task tool patterns
