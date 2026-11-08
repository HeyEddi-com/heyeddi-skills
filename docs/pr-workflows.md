# PR workflows

**Date:** 2026-11-07

HeyEddi splits pull request work into **skills** with distinct roles. Use the right one — they are not interchangeable.

## Overview

| Workflow | Skill | Who | When |
|----------|-------|-----|------|
| **1. Review submitted PR** | `@heyeddi-pr-review` | Reviewer, QA, or author self-check | Inline line findings (not merge gates) |
| **2. Respond to PR review** | `@heyeddi-pr-respond` | PR author | Every thread (same GitHub user ok) |
| **3. Merge readiness** | `@pre-merge-gate --signoff` | Author / QA | After respond; before merge-ready claim |

```
@heyeddi-pr-review  → inline findings (or Approve)
@heyeddi-pr-respond → fix/decline + reply every thread
@pre-merge-gate --signoff → clean tree, CI green, threads resolved
→ authorize merge
```

## Workflow 1 — Review submitted PR

**Invoke:** `@heyeddi-pr-review` + PR number

**Scope rule:** Only committed changes (`base...head`). Ignore uncommitted files.

### Pipeline

1. `fetch_pr_context` — diff, changed files, categories, routes touched
2. `check_doc_drift` — product.md, design.md, engineering docs vs changes
3. `audit_pr_changes` — KISS/test signals on changed files only
4. `@heyeddi-product` — `load_product_context`, `check_features` for touched routes
5. Conditional delegates when UI/API files change (visual-auditor, composable-patterns, etc.)
6. `post_inline_review` — real findings on exact lines (`<!-- heyeddi-pr-review -->`); zero findings → Approve
7. Do **not** own `@pre-merge-gate` inside review (that is step 3 after respond)

### Output

Inline GitHub review comments on the committed diff. Lint/CI/merge gates stay with `@pre-merge-gate`.

### Example prompt

```
@heyeddi-pr-review Review PR #42 — committed changes only.
Leave real findings as inline comments (security, logic, related call sites).
```

## Workflow 2 — Respond to PR review

**Invoke:** `@heyeddi-pr-respond` + PR number

**Scope rule:** Address **every** reviewer comment with fix-vs-decline reasoning.

### Pipeline

1. `fetch_pr_comments` — inline, review, discussion
2. Tracking table → `.heyeddi/docs/pr-<N>-tracking.md`
3. Per comment: fix | decline | partial | out-of-scope
4. Apply fixes in code/docs
5. Draft `.heyeddi/docs/pr-<N>-replies.md` — one `## Comment <id>` per thread, `## Summary` last
6. `post_thread_replies` — resolve root id; inline REST `/replies` (+ GraphQL fallback); discussion = **quote-reply** via issues comments (never fake `/issues/comments/{id}/replies`). On error: GitHub MCP `add_reply_to_pull_request_comment` / `add_issue_comment`
7. `verify_response --check` (add `--live` to confirm GitHub threaded replies for inline)
8. Summary comment on PR **only after** verify passes
9. `@pre-merge-gate --signoff` after threads are done

### vs `/babysit`

| Tool | Use when |
|------|----------|
| `/babysit` | Fast merge-ready loop |
| `@heyeddi-pr-respond` | Team rules — every comment, fix matrix, documented tracking |

### Example prompt

```
@heyeddi-pr-respond Handle review feedback on PR #42.
Reply to every comment; fix what's correct; re-run pre-merge gate.
```

## Workflow 2 — Respond to PR review (unified)

**Invoke:** `@heyeddi-pr-respond` + PR number

Covers human reviewers, HeyEddi CI root summaries, inline threads, and discussion comments.

### Pipeline

1. `fetch_pr_comments` + `build_comment_inventory --write-cache`
2. Tracking in chat (every inventory item)
3. Fix vs decline each item; commit + push before Fixed replies
4. `post_thread_replies --replies-text` + `verify_response --use-inventory --live`
5. Never merge without **authorize merge**

**Removed:** `@heyeddi-ci-respond` — deleted; use `@heyeddi-pr-respond` only.

## Delegation map

| Concern | Workflow 1 | Workflow 2 |
|---------|------------|------------|
| Product / AC | `@heyeddi-product` | fix-vs-decline uses PR goals |
| Engineering | `audit_pr_changes`, `@engineering-excellence` | fixes + re-audit if needed |
| Visual / UX | `@visual-auditor` (if UI in diff) | only if comment is visual |
| CI / tests / ship | `@pre-merge-gate --signoff` | `@pre-merge-gate --signoff` after threads |
| GitHub | optional review | **required** threaded replies |

## Artifacts (`.heyeddi/docs/`) — local / gitignored / not for commit

These files are **ephemeral session scratch** for agent verify gates. **Do not commit them.** GitHub PR threads (and posted `gh pr review`) are the SSOT.

| File | Workflow | Commit? |
|------|----------|---------|
| `pr-<N>-review.md` | Submission review report | No — gitignore |
| `pr-<N>-context.json` | Cached fetch_pr_context | No — gitignore |
| `pr-<N>-ci-*` | **Deprecated** — delete if present | No |

## Eval cases

```bash
uv run poe eval-pr-submission   # workflow 1 — fixture diff
uv run poe eval-pr              # workflow 2 — fixture comments
```

## Related docs

- [team-cheat-sheet.md](./team-cheat-sheet.md) — quick invoke table
- [heyeddi-folder.md](./heyeddi-folder.md) — `.heyeddi/docs/` layout
- [subagent-delegation.md](./subagent-delegation.md) — Task tool patterns
