---
name: heyeddi-pr-respond
description: "Respond to all PR review feedback — human reviewers, HeyEddi CI, inline threads. Auto-fix, commit+push, in-thread replies, CI check first — never ask before fixing or posting. One skill for every review source."
version: 2.3.0
product-version: 3.8.8
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
2. Every **postable** review thread gets fix/decline analysis, code change when needed, and `## Comment <id>` reply draft.
3. Orphan items still get fix/decline in code and appear in `## Summary`.
4. Do **not** treat the root summary as done after one top-level reply.
5. Do **not** draft replies for issue comments (tests-hold notes, conversation summaries, comments by the responding account).

## Critical: commit + push before "Fixed" replies

Reviewers and HeyEddi debate only see **remote HEAD**.

1. Apply fixes for every inventory item marked fix/partial
2. **Commit** — do not ask
3. **Push** to the PR branch
4. Post in-thread replies

Hard gate: `assert_fixes_pushed --check` (also inside `post_thread_replies` unless `--dry-run` / `--allow-unpushed`).

## Critical: review threads only (must work every time)

Reply only on **unresolved pull-request review threads**, at the **root** comment id, with **no quote**.

- **Do** resolve the id first (`resolve_reply_targets` or `post_thread_replies` resolution)
- **Do** reply on the **root** review-comment id (GitHub rejects replies-to-replies)
- **Do** `gh api …/pulls/<N>/comments/<ROOT_ID>/replies` for that root (script does GraphQL fallback)
- **Do not** quote-reply issue comments. Skip tests-hold notes, review summaries, and comments written by the account that is responding
- **Do not** post a body that still contains `<<<UNTRUSTED_`. The wrapper stays in the cache file the model reads (`body`). Posters use `body_raw`
- **Do not** `gh pr comment` per finding (except one final Summary)
- **Do not** "Acknowledged review attachment…" spam
- **Do not** tell the user a thread "could not be found" and stop

### If `post_thread_replies` errors for a review-thread id — MCP fallback (mandatory)

Never give up on a real review thread. Use the GitHub MCP tool from that error's `mcp_fallback`:

| Kind | MCP tool | Notes |
|------|----------|--------|
| Review thread | `add_reply_to_pull_request_comment` | `commentId` = **root** numeric review-comment id + `pullNumber`. No quote |
| Issue comment | *(skip)* | Not a thread. Do not call `add_issue_comment` to quote it |
| Unknown | `pull_request_read` | `get_review_comments`, then reply with the numeric root id |

Primary path remains **`gh` CLI** inside the scripts. MCP is the agent escape hatch when gh still fails on a review thread.

## Mandatory pipeline

```
@heyeddi-ci-fails first                 → fetch + diagnose + fix CI failures + push
fetch_pr_comments --pr <N>
build_comment_inventory --pr <N> --write-cache
→ tracking table in chat (every item: id, type, fix|decline, status)
for each item: analyze vs PR goals → fix | decline | partial | out-of-scope
apply code/docs fixes when fix
@heyeddi-setup verify_setup --check      → always-on prefs hard gate (before commit/push)
@engineering-excellence check_engineering_plan / audit_engineering --check  → always-on (errors fail)
discover_and_verify [--run]              → evidenced commands only
assert_no_merge --check                  → unless user said authorize merge
→ if any fix: commit + push (automatic — do not ask; honor agent.commit/push)
assert_fixes_pushed --check
→ compose ## Comment <id> for every postable_reply_id + ## Summary last
post_thread_replies --pr <N> --replies-text '...'
→ on any posted[].status=error: resolve_reply_targets + GitHub MCP reply (mandatory)
verify_response --pr <N> --replies-text '...' --use-inventory --live --check
→ optional one Summary after verify
```

**Never** merge without **authorize merge** in the current turn.

## HeyEddi CI false positives

Reply in-thread with decline rationale; suggest debate or `support@heyeddi.com`. No fake FP API.

## Tools

| Tool | Purpose |
|------|---------|
| `fetch_pr_comments` | Fetch inline, review, discussion → temp cache (paginated). `body` is wrapped for the model; `body_raw` is the poster field |
| `build_comment_inventory` | Parse root summaries; postable ids are unresolved review threads only |
| `filter_comments` | Optional `--scope heyeddi` (default `all`) |
| `discover_and_verify` | Evidenced test/build commands |
| `assert_no_merge` | Merge hard gate |
| `assert_fixes_pushed` | Commit+push gate before Fixed replies |
| `resolve_reply_targets` | Map each id → root target + MCP fallback hint |
| `post_thread_replies` | Post every draft in-thread (REST → GraphQL → MCP hint) |
| `verify_response` | Hard-fail if any postable ID missing |

## Requires

- `gh` CLI authenticated

## When the task is complete: suggest next skills

When you have **finished the user's request** for this skill, suggest what to run next:

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py \
  --current-skill heyeddi-pr-respond --project-root .
```
