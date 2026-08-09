
# Vocabulary: PR review

- Inline comment: line-specific code feedback: reply via `/replies` endpoint.
- Review comment: general review body from a submitted review.
- Discussion comment: PR conversation thread.
- Tracking table: Comment ID, type, author, summary, action, status (PENDING/RESPONDED).
- Replies draft: `.heyeddi/docs/pr-<N>-replies.md` with `## Comment <id>` per thread and `## Summary` last.
- Posted log: `.heyeddi/docs/pr-<N>-posted.json` written by `post_thread_replies` (required by live verify).
- Ephemeral artifacts: all `pr-<N>-*` tracking/replies/posted/comments files are **never committed**; GitHub is SSOT.
