---
name: heyeddi-pr-respond
description: "Respond to all PR review feedback — human reviewers, HeyEddi CI, inline threads. Auto-fix, commit+push, in-thread replies, CI check first — never ask before fixing or posting. One skill for every review source."
version: 2.1.0
product-version: 3.4.6
author: HeyEddi-com
disable-model-invocation: true
---

# HeyEddi PR Respond

**PR author response to every review source** — human teammates, bots, and **HeyEddi CI** (inline + root summaries).

There is **one** respond skill. Do not split human vs CI into different pipelines.

## Default behavior (no confirmation)

On any PR work, **do not ask** whether to fix findings, check CI, or post threaded replies — always do all three.

1. **Always** run `@heyeddi-ci-fails` first (fetch, diagnose, fix actionable CI failures)
2. **Fix** valid review items automatically
3. **Commit + push** automatically
4. **Post** every reply in-thread automatically
5. Only **merge** requires **authorize merge** in the current turn

## No project scratch files

**Never write** `.heyeddi/docs/pr-*` (tracking, replies, posted, comments). GitHub threads are the SSOT.

| Data | Where it lives |
|------|----------------|
| Comment cache | System temp (`fetch_pr_comments` stdout path) |
| Inventory | `build_comment_inventory` stdout (optional temp cache) |
| Tracking | In chat only |
| Reply drafts | `--replies-text` to `post_thread_replies` / `verify_response` |
| Post log | `post_thread_replies` stdout JSON only |

Delete legacy `pr-*` / `pr-*-ci-*` files under `.heyeddi/docs/` if present.

## Root review summaries (HeyEddi CI and others)

Review **submission bodies** often list findings like:

```
**Commented on the diff**
1. 🔴 Bug title — `path/to/file.py:185`
```

**Mandatory:**

1. Run `build_comment_inventory` after fetch — parses root summaries + inline IDs.
2. Every **postable** item gets fix/decline analysis, code change when needed, and `## Comment <id>` reply draft.
3. Orphan items still get fix/decline in code and appear in `## Summary`.
4. Do **not** treat the root summary as done after one top-level reply.

## Critical: commit + push before "Fixed" replies

Reviewers and HeyEddi debate only see **remote HEAD**.

1. Apply fixes for every inventory item marked fix/partial
2. **Commit** — do not ask
3. **Push** to the PR branch
4. Post in-thread replies

Hard gate: `assert_fixes_pushed --check` (also inside `post_thread_replies` unless `--dry-run` / `--allow-unpushed`).

## Critical: in-thread replies only

- **Do** `gh api …/pulls/<N>/comments/<ID>/replies`
- **Do not** `gh pr comment` per finding
- **Do not** "Acknowledged review attachment…" spam

## Mandatory pipeline

```
@heyeddi-ci-fails first                 → fetch + diagnose + fix CI failures + push
fetch_pr_comments --pr <N>
build_comment_inventory --pr <N> --write-cache
→ tracking table in chat (every item: id, type, fix|decline, status)
for each item: analyze vs PR goals → fix | decline | partial | out-of-scope
apply code/docs fixes when fix
discover_and_verify [--run]              → evidenced commands only
assert_no_merge --check                  → unless user said authorize merge
→ if any fix: commit + push (automatic — do not ask)
assert_fixes_pushed --check
→ compose ## Comment <id> for every postable_reply_id + ## Summary last
post_thread_replies --pr <N> --replies-text '...'
verify_response --pr <N> --replies-text '...' --use-inventory --live --check
→ optional one Summary after verify
```

**Never** merge without **authorize merge** in the current turn.

## HeyEddi CI false positives

Reply in-thread with decline rationale; suggest debate or `support@heyeddi.com`. No fake FP API.

## Tools

| Tool | Purpose |
|------|---------|
| `fetch_pr_comments` | Fetch inline, review, discussion → temp cache |
| `build_comment_inventory` | Parse root summaries + inline; list every item |
| `filter_comments` | Optional `--scope heyeddi` (default `all`) |
| `discover_and_verify` | Evidenced test/build commands |
| `assert_no_merge` | Merge hard gate |
| `assert_fixes_pushed` | Commit+push gate before Fixed replies |
| `post_thread_replies` | Post every draft in-thread |
| `verify_response` | Hard-fail if any postable ID missing |

## Requires

- `gh` CLI authenticated

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

```bash
python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py \
  --current-skill heyeddi-pr-respond --project-root .
```
