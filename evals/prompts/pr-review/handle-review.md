@heyeddi-pr-respond

## Handle PR #42 review (fixture mode)

This eval uses **fixture comments** — do not call live `gh api` to post replies.

1. Run `fetch_pr_comments` with `--pr 42 --fixture .pr-fixture/comments.json --project-root .`
2. Build a **tracking table** in `.heyeddi/docs/pr-42-tracking.md` — **every** inline comment, discussion comment, and review must have a row with: ID, type, author, summary, action (fix / decline / acknowledge), response status.
3. Draft threaded replies in `.heyeddi/docs/pr-42-replies.md` using this exact shape:
   - One `## Comment <id> (type)` section **per** comment ID (9001001, 9001002, DC_10001, 8001, 8002)
   - Non-empty reply body under each heading
   - `## Summary` **last** (only after all individual sections)
4. For comments marked **fix**: apply the code fix in this repo if the referenced files exist (`src/composables/useUsers.ts`, `backend/app/routers/users.py`); otherwise document the fix in the tracking table.
5. Run `pre_merge_gate` (or document SKIP if no package.json tests).
6. Optional offline post log: `post_thread_replies --pr 42 --dry-run --project-root .`
7. Run `verify_response --pr 42 --fixture .pr-fixture/comments.json --check --project-root .` after tracking and replies are complete.

Team rules: reply to **every** comment; a summary alone is not enough.
