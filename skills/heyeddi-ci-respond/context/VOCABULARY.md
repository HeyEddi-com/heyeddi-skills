# Vocabulary: HeyEddi CI respond

- **HeyEddi finding**: inline/review/discussion comment with `<!-- heyeddi-ci-review` or bot login
- **ci-comments cache**: filtered JSON in system temp only (from `fetch_pr_comments` / `filter_heyeddi_comments`) — never under `.heyeddi/docs/`
- **tracking**: in-agent table (comment ID, action, status) — never a `pr-*-ci-tracking.md` file
- **reply draft**: markdown with `## Comment <id>` sections + `## Summary` last — pass via `--replies-text`, not `pr-*-ci-replies.md`
- **post log**: stdout JSON from `post_thread_replies` — never `pr-*-ci-posted.json`
