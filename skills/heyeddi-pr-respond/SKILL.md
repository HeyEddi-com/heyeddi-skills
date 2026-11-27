---
name: heyeddi-pr-respond
description: "Respond to all PR review feedback: human reviewers, @heyeddi-pr-review inline findings, HeyEddi CI. Same GitHub user who left the review is fine. Auto-fix, commit+push, in-thread replies, CI check first. Not the reviewer skill (use heyeddi-pr-review) and not the merge gate (use pre-merge-gate)."
version: 2.4.2
product-version: 3.8.27
author: HeyEddi-com
---

# HeyEddi PR Respond

**PR author response to every review source**: human teammates, **`@heyeddi-pr-review` line findings**, bots, and **HeyEddi CI**.

Same GitHub account may both review and respond. Unresolved **review-thread roots** stay postable even when authored by the responder. Skip only when the thread already ends with the responder's reply, or when the item is a non-thread issue comment.

There is **one** respond skill. Do not split human vs CI into different pipelines.

## Flow

```
@heyeddi-pr-review   → inline findings (or Approve)
@heyeddi-pr-respond  → this skill: fix/decline + reply every thread
@pre-merge-gate      → merge readiness after threads are done
```


## Default behavior (no confirmation)

On any PR work, **do not ask** whether to fix findings, check CI, or post threaded replies. Always do all three.

1. **Always** run `@heyeddi-ci-fails` first (fetch, diagnose, fix actionable CI failures)
2. **Fix** valid review items automatically
3. **Commit + push** automatically
4. **Post** every reply in-thread automatically
5. **Finish**: watch checks until green, run the pre-merge gate, merge. Merge into dev / test / staging yourself once `@pre-merge-gate --signoff` exits 0. A production merge takes the user's **authorize merge** in the current turn; never run it earlier.

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
1. 🔴 Bug title: `path/to/file.py:185`
```

**Mandatory:**

1. Run `build_comment_inventory` after fetch. It parses root summaries + inline IDs.
2. Every **postable** review thread gets fix/decline analysis, code change when needed, and `## Comment <id>` reply draft.
3. Orphan items still get fix/decline in code and appear in `## Summary`.
4. Do **not** treat the root summary as done after one top-level reply.
5. Do **not** draft replies for issue comments (tests-hold notes, conversation summaries). Own **issue** notes are skipped; own **review-thread findings** from `@heyeddi-pr-review` are **not** skipped.

## Critical: commit + push before "Fixed" replies

Reviewers and HeyEddi debate only see **remote HEAD**.

1. Apply fixes for every inventory item marked fix/partial
2. **Commit**: do not ask
3. **Push** to the PR branch
4. Post in-thread replies

Hard gate: `assert_fixes_pushed --check` (also inside `post_thread_replies` unless `--dry-run` / `--allow-unpushed`).

## Critical: review threads only (must work every time)

Reply only on **unresolved pull-request review threads**, at the **root** comment id, with **no quote**.

- **Do** resolve the id first (`resolve_reply_targets` or `post_thread_replies` resolution)
- **Do** reply on the **root** review-comment id (GitHub rejects replies-to-replies)
- **Do** `gh api …/pulls/<N>/comments/<ROOT_ID>/replies` for that root (script does GraphQL fallback)
- **Do not** quote-reply issue comments. Skip tests-hold notes and review submission bodies. Do **not** skip unresolved inline findings just because you authored them (self-review → respond is supported)
- **Do not** post a body that still contains `<<<UNTRUSTED_`. The wrapper stays in the cache file the model reads (`body`). Posters use `body_raw`
- **Do not** `gh pr comment` per finding (except one final Summary)
- **Do not** "Acknowledged review attachment…" spam
- **Do not** tell the user a thread "could not be found" and stop

### Resolve fixed threads

The HeyEddi Reviewer does not review a new commit while a thread is open. Start every fixed reply with **Fixed** (or Done / Addressed): `post_thread_replies` resolves that thread right after the reply posts.

Every other reply stays open and MUST start with `**Declined:** <reason>`. The pre-merge gate passes an open thread only when its last reply is the PR author's and carries that marker with a reason, and it lists each one. Any other open thread blocks the merge.

- **Partial:** fix the valid part, then `**Declined:** <what you left out and why>. The rest is fixed in <sha>.`
- **Out-of-scope** but valid: fix it on its own branch and PR in this run, then `**Declined:** outside this PR; fixed in <PR URL>.`
- A thread that already ends with your unmarked reply is skipped by the poster: add the marked reply with `gh api repos/<owner>/<repo>/pulls/<N>/comments/<ROOT_ID>/replies -f body=...`, or fix it and resolve the thread.

 `--no-resolve` leaves every thread open. A `resolve_errors` entry is not a failed reply: resolve that thread with GitHub MCP `resolve_review_thread` or `gh api graphql` `resolveReviewThread`.

### If `post_thread_replies` errors for a review-thread id: MCP fallback (mandatory)

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
for each item: analyze vs PR goals → fix | decline | partial | out-of-scope (fixed on its own branch and PR)
apply code/docs fixes when fix
@heyeddi-setup verify_setup --check      → prefs (defaults when missing; never a stop)
@engineering-excellence check_engineering_plan / audit_engineering --check  → always-on (errors fail)
discover_and_verify [--run]              → evidenced commands only
→ if any fix: commit + push (automatic; check_permission decides, default balanced allows on a PR branch)
assert_fixes_pushed --check
→ compose ## Comment <id> for every postable_reply_id + ## Summary last
post_thread_replies --pr <N> --replies-text '...'   → also resolves threads whose reply starts with Fixed
→ on any posted[].status=error: resolve_reply_targets + GitHub MCP reply (mandatory)
→ on any resolve_errors entry: resolve that thread (MCP resolve_review_thread)
verify_response --pr <N> --replies-text '...' --use-inventory --live --check
→ optional one Summary after verify
gh pr checks <N> --watch                  → run in the background until every check finishes
gh run view <run-id> --log-failed         → read each failure; fix, commit, push, watch again
gh run rerun <run-id> --failed            → flaky or infrastructure failure with no code cause (once, then treat it as real)
pre_merge_gate.py --signoff --project-root .  → (.agents/skills/pre-merge-gate/scripts/) fix every FAIL and rerun
assert_no_merge --check --base <baseRefName> --planned-command "gh pr merge <N>" --project-root .
gh pr merge <N> --merge                   → base below production: run it. Production base: only after authorize merge
```

Merge into dev / test / staging yourself once `@pre-merge-gate --signoff` exits 0. A production merge takes the user's **authorize merge** in the current turn; never run it earlier.

## HeyEddi CI false positives

Reply in-thread with decline rationale; suggest debate or `support@heyeddi.com`. No fake FP API.

## Tools

| Tool | Purpose |
|------|---------|
| `fetch_pr_comments` | Fetch inline, review, discussion → temp cache (paginated). `body` is wrapped for the model; `body_raw` is the poster field |
| `build_comment_inventory` | Parse root summaries; postable ids are unresolved review threads only |
| `filter_comments` | Optional `--scope heyeddi` (default `all`) |
| `discover_and_verify` | Evidenced test/build commands |
| `assert_no_merge` | Check right before a merge: production needs authorize merge |
| `assert_fixes_pushed` | Commit+push gate before Fixed replies |
| `resolve_reply_targets` | Map each id → root target + MCP fallback hint |
| `post_thread_replies` | Post every draft in-thread (REST → GraphQL → MCP hint); resolve threads answered with Fixed |
| `verify_response` | Hard-fail if any postable ID missing |

## Requires

- `gh` CLI authenticated

## Without the gh CLI

`gh` is optional. Every script here that talks to GitHub checks for it first. When `gh` is missing or logged out, the script prints `{"status": "degraded", ...}` with the reason and a `manual` list, and exits **3**.

- Exit 3 is not a pass and not a failure. It means the step could not run.
- Do not retry in a loop and do not report the step as done.
- Do the step by hand with the GitHub MCP tools named in `manual`; if that is not possible, keep going and list `gh auth login` under **Needs you**.
- Nothing is posted, verified or signed off when a script exits 3.

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi/scripts/suggest_next_skill.py --current-skill heyeddi-pr-respond --project-root .
```

Add `--route /path` or `--mode <sub-command>` when you know them. If the suggested skill is still part of the user's request, run it now; do not hand it back. In a build request, once the request is done, run `python .agents/skills/heyeddi-product/scripts/backlog.py --project-root . next`, build the item it returns through merge below production, and repeat until it returns none. Only new work nobody asked for goes under **Next** in the final summary, in one line; never list leftovers there. See `@heyeddi` `reference/next-skill-handoff.md` and `reference/autonomy.md`.
