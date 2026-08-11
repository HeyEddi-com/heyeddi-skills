---
name: heyeddi-pr-respond
description: "Respond to all PR review feedback — human reviewers, HeyEddi CI root summaries, and inline threads. Fetch, inventory, fix-or-decline, commit+push, in-thread replies, verify. One skill for every review source."
version: 2.0.0
product-version: 3.4.3
author: HeyEddi-com
disable-model-invocation: true
---

# HeyEddi PR Respond

**PR author response to every review source** — human teammates, bots, and **HeyEddi CI root summaries** (e.g. `heyeddi-ci` review bodies that list findings on the diff).

There is **one** respond skill. Do not split human vs CI into different pipelines.

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

Review **submission bodies** (Conversation / Files tab root comment) often list findings like:

```
**Commented on the diff**
1. 🔴 Bug title — `path/to/file.py:185`
```

**Mandatory:**

1. Run `build_comment_inventory` after fetch — it parses every review body for `` `path:line` `` bullets and links them to inline comment IDs.
2. Every **postable** item (inline + discussion) gets fix/decline analysis, a code change when needed, and a `## Comment <id>` reply draft.
3. Orphan items (listed in the root summary but no inline thread) still get fix/decline in code and must appear in `## Summary`.
4. Do **not** treat the root summary as "done" after one top-level reply — each inline thread needs `/replies`.

## Critical: commit + push before "Fixed" replies

Reviewers and HeyEddi debate only see **remote HEAD**.

1. Apply fixes for every inventory item marked fix/partial
2. **Commit** (ask the user if needed)
3. **Push** to the PR branch
4. Post in-thread replies

Hard gate: `assert_fixes_pushed --check` (also inside `post_thread_replies` unless `--dry-run` / `--allow-unpushed`).

## Critical: in-thread replies only

- **Do** `gh api …/pulls/<N>/comments/<ID>/replies`
- **Do not** `gh pr comment` per finding
- **Do not** "Acknowledged review attachment…" spam
- Review submission bodies are not threads — reply on each inline ID; optional one Summary at the end

## Mandatory pipeline

```
fetch_pr_comments --pr <N>
build_comment_inventory --pr <N> --write-cache
→ tracking table in chat (every inventory item: id, type, fix|decline, status)
for each item: analyze vs PR goals → fix | decline | partial | out-of-scope
apply code/docs fixes when fix
discover_and_verify [--run]              → evidenced commands only (optional)
assert_no_merge --check                  → unless user said authorize merge
→ if any fix: commit + push (ask user if commit not authorized)
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
| `build_comment_inventory` | Parse root summaries + inline; list every item to address |
| `filter_comments` | Optional `--scope heyeddi` (default `all`) |
| `discover_and_verify` | Evidenced test/build commands |
| `assert_no_merge` | Merge hard gate |
| `assert_fixes_pushed` | Commit+push gate before Fixed replies |
| `post_thread_replies` | Post every draft in-thread (`--replies-text` required) |
| `verify_response` | Hard-fail if any postable ID missing draft or live thread |

## Requires

- `gh` CLI authenticated

## When the task is complete: suggest next skills

```bash
python .agents/skills/heyeddi-orchestrator/scripts/suggest_next_skill.py \
  --current-skill heyeddi-pr-respond --project-root .
```
